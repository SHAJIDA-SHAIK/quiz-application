from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import os
import random
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, get_current_user,
)
from questions_data import QUESTIONS, CATEGORIES, DIFFICULTIES, QUESTIONS_BY_ID

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Retro Quiz API")
api_router = APIRouter(prefix="/api")

# ============ MODELS ============
class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    name: str
    email: str


class QuizStartRequest(BaseModel):
    category: str
    difficulty: str
    num_questions: int = 10


class QuestionPublic(BaseModel):
    id: str
    category: str
    difficulty: str
    question: str
    options: List[str]


class QuizStartResponse(BaseModel):
    quiz_id: str
    questions: List[QuestionPublic]
    time_per_question: int = 20


class SubmittedAnswer(BaseModel):
    question_id: str
    selected_index: Optional[int] = None
    time_taken: float = 0.0


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    category: str
    difficulty: str
    answers: List[SubmittedAnswer]


class ReviewItem(BaseModel):
    question_id: str
    question: str
    options: List[str]
    correct_index: int
    selected_index: Optional[int]
    is_correct: bool


class QuizResult(BaseModel):
    id: str
    user_name: str
    category: str
    difficulty: str
    total: int
    correct: int
    wrong: int
    score: int
    accuracy: float
    review: List[ReviewItem]
    created_at: str


class LeaderboardEntry(BaseModel):
    rank: int
    user_name: str
    score: int
    accuracy: float
    category: str
    difficulty: str
    created_at: str


# ============ AUTH ROUTES ============
@api_router.post("/auth/register", response_model=UserPublic)
async def register(payload: RegisterRequest, response: Response):
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": email,
        "name": payload.name.strip(),
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.users.insert_one(doc)
    user_id = str(result.inserted_id)
    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)
    return UserPublic(id=user_id, name=doc["name"], email=email)


@api_router.post("/auth/login", response_model=UserPublic)
async def login(payload: LoginRequest, response: Response):
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user_id = str(user["_id"])
    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)
    return UserPublic(id=user_id, name=user["name"], email=email)


@api_router.post("/auth/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}


async def _current_user(request: Request):
    return await get_current_user(request, db)


@api_router.get("/auth/me", response_model=UserPublic)
async def me(user: dict = Depends(_current_user)):
    return UserPublic(id=user["id"], name=user["name"], email=user["email"])


# ============ QUIZ ROUTES ============
@api_router.get("/quiz/categories")
async def get_categories():
    return {"categories": CATEGORIES, "difficulties": DIFFICULTIES}


@api_router.post("/quiz/start", response_model=QuizStartResponse)
async def start_quiz(payload: QuizStartRequest, user: dict = Depends(_current_user)):
    pool = list(QUESTIONS)
    if payload.category != "Mixed":
        if payload.category not in CATEGORIES:
            raise HTTPException(status_code=400, detail="Invalid category")
        pool = [q for q in pool if q["category"] == payload.category]
    if payload.difficulty != "Mixed":
        if payload.difficulty not in DIFFICULTIES:
            raise HTTPException(status_code=400, detail="Invalid difficulty")
        pool = [q for q in pool if q["difficulty"] == payload.difficulty]
    if not pool:
        raise HTTPException(status_code=400, detail="No questions available for this combination")
    random.shuffle(pool)
    n = max(1, min(payload.num_questions, len(pool)))
    chosen = pool[:n]
    quiz_id = str(ObjectId())
    await db.quiz_sessions.insert_one({
        "_id": ObjectId(quiz_id),
        "user_id": user["id"],
        "question_ids": [q["id"] for q in chosen],
        "category": payload.category,
        "difficulty": payload.difficulty,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    public_qs = [QuestionPublic(id=q["id"], category=q["category"], difficulty=q["difficulty"],
                                question=q["question"], options=q["options"]) for q in chosen]
    return QuizStartResponse(quiz_id=quiz_id, questions=public_qs, time_per_question=20)


@api_router.post("/quiz/submit", response_model=QuizResult)
async def submit_quiz(payload: QuizSubmitRequest, user: dict = Depends(_current_user)):
    session = await db.quiz_sessions.find_one({"_id": ObjectId(payload.quiz_id), "user_id": user["id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Quiz session not found")
    valid_ids = set(session["question_ids"])
    review: List[ReviewItem] = []
    correct = 0
    difficulty_weight = {"Easy": 10, "Medium": 15, "Hard": 20}
    score = 0
    for ans in payload.answers:
        if ans.question_id not in valid_ids:
            continue
        q = QUESTIONS_BY_ID[ans.question_id]
        is_correct = ans.selected_index == q["correct_index"]
        if is_correct:
            correct += 1
            score += difficulty_weight.get(q["difficulty"], 10)
        review.append(ReviewItem(
            question_id=q["id"], question=q["question"], options=q["options"],
            correct_index=q["correct_index"], selected_index=ans.selected_index,
            is_correct=is_correct,
        ))
    total = len(review)
    wrong = total - correct
    accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0
    now_iso = datetime.now(timezone.utc).isoformat()
    result_doc = {
        "user_id": user["id"],
        "user_name": user["name"],
        "category": payload.category,
        "difficulty": payload.difficulty,
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "score": score,
        "accuracy": accuracy,
        "created_at": now_iso,
    }
    ins = await db.quiz_results.insert_one(result_doc)
    return QuizResult(
        id=str(ins.inserted_id), user_name=user["name"],
        category=payload.category, difficulty=payload.difficulty,
        total=total, correct=correct, wrong=wrong, score=score, accuracy=accuracy,
        review=review, created_at=now_iso,
    )


@api_router.get("/quiz/leaderboard", response_model=List[LeaderboardEntry])
async def leaderboard(limit: int = 10, category: Optional[str] = None):
    query = {}
    if category and category != "Mixed":
        query["category"] = category
    cursor = db.quiz_results.find(query).sort([("score", -1), ("accuracy", -1), ("created_at", 1)]).limit(limit)
    docs = await cursor.to_list(length=limit)
    entries = []
    for i, d in enumerate(docs, start=1):
        entries.append(LeaderboardEntry(
            rank=i, user_name=d.get("user_name", "Anonymous"),
            score=d.get("score", 0), accuracy=d.get("accuracy", 0.0),
            category=d.get("category", "Mixed"), difficulty=d.get("difficulty", "Mixed"),
            created_at=d.get("created_at", ""),
        ))
    return entries


@api_router.get("/quiz/stats")
async def user_stats(user: dict = Depends(_current_user)):
    cursor = db.quiz_results.find({"user_id": user["id"]}).sort("created_at", -1)
    docs = await cursor.to_list(length=1000)
    if not docs:
        return {
            "games_played": 0, "best_score": 0, "avg_accuracy": 0.0,
            "total_correct": 0, "total_questions": 0, "by_category": {}, "recent": [],
        }
    games_played = len(docs)
    best_score = max(d.get("score", 0) for d in docs)
    total_correct = sum(d.get("correct", 0) for d in docs)
    total_questions = sum(d.get("total", 0) for d in docs)
    avg_accuracy = round(sum(d.get("accuracy", 0) for d in docs) / games_played, 1)
    by_category = {}
    for d in docs:
        cat = d.get("category", "Mixed")
        entry = by_category.setdefault(cat, {"games": 0, "correct": 0, "total": 0, "best_score": 0})
        entry["games"] += 1
        entry["correct"] += d.get("correct", 0)
        entry["total"] += d.get("total", 0)
        entry["best_score"] = max(entry["best_score"], d.get("score", 0))
    for cat, e in by_category.items():
        e["accuracy"] = round((e["correct"] / e["total"]) * 100, 1) if e["total"] else 0.0
    recent = [
        {"score": d.get("score", 0), "accuracy": d.get("accuracy", 0.0),
         "category": d.get("category"), "difficulty": d.get("difficulty"),
         "created_at": d.get("created_at", "")}
        for d in docs[:10]
    ]
    return {
        "games_played": games_played, "best_score": best_score,
        "avg_accuracy": avg_accuracy, "total_correct": total_correct,
        "total_questions": total_questions, "by_category": by_category, "recent": recent,
    }


@api_router.get("/")
async def root():
    return {"message": "Retro Quiz API is running"}


# ============ APP SETUP ============
app.include_router(api_router)

frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def on_startup():
    await db.users.create_index("email", unique=True)
    await db.quiz_results.create_index([("score", -1)])
    logger.info("Retro Quiz backend started.")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
