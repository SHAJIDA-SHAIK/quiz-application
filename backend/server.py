from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import os
import random
import logging
import secrets
import json as jsonlib
from io import BytesIO
from datetime import datetime, timezone
from typing import List, Optional, Any

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import inch

from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, get_current_user, get_current_admin,
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
    role: str = "user"
    email_verified: bool = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6, max_length=100)


class VerifyEmailRequest(BaseModel):
    token: str


class QuizStartRequest(BaseModel):
    category: str
    difficulty: str
    num_questions: int = 10
    negative_marking: bool = False


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
    negative_marking: bool = False


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
    negative_marking: bool = False
    passed: bool = False
    review: List[ReviewItem]
    created_at: str


class LeaderboardEntry(BaseModel):
    rank: int
    user_name: str
    user_id: Optional[str] = None
    score: int
    accuracy: float
    category: str
    difficulty: str
    created_at: str


class AdminQuestionCreate(BaseModel):
    category: str
    difficulty: str
    question: str = Field(min_length=3, max_length=500)
    options: List[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)


class AIGenerateRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=60)
    difficulty: str = "Medium"
    count: int = Field(default=5, ge=1, le=10)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============ AUTH ROUTES ============
def _make_verify_link(token: str) -> str:
    frontend = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    return f"{frontend}/verify-email?token={token}"


def _make_reset_link(token: str) -> str:
    frontend = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    return f"{frontend}/reset-password?token={token}"


@api_router.post("/auth/register")
async def register(payload: RegisterRequest, response: Response):
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    verify_token = secrets.token_urlsafe(32)
    doc = {
        "email": email,
        "name": payload.name.strip(),
        "password_hash": hash_password(payload.password),
        "role": "user",
        "email_verified": False,
        "verify_token": verify_token,
        "verify_token_expires": (datetime.now(timezone.utc) + __import__("datetime").timedelta(days=2)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.users.insert_one(doc)
    user_id = str(result.inserted_id)
    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)
    dev_link = _make_verify_link(verify_token)
    logger.info(f"[VERIFY EMAIL] {email} -> {dev_link}")
    return {
        "id": user_id, "name": doc["name"], "email": email,
        "role": "user", "email_verified": False,
        "dev_verify_link": dev_link,
    }


@api_router.post("/auth/login")
async def login(payload: LoginRequest, response: Response):
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user_id = str(user["_id"])
    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)
    return {
        "id": user_id, "name": user["name"], "email": email,
        "role": user.get("role", "user"),
        "email_verified": user.get("email_verified", False),
    }


@api_router.post("/auth/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}


async def _current_user(request: Request):
    return await get_current_user(request, db)


async def _current_admin(request: Request):
    return await get_current_admin(request, db)


@api_router.get("/auth/me")
async def me(user: dict = Depends(_current_user)):
    return {
        "id": user["id"], "name": user["name"], "email": user["email"],
        "role": user.get("role", "user"),
        "email_verified": user.get("email_verified", False),
    }


@api_router.post("/auth/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    # Always return success shape to prevent user enumeration, but only create token if user exists.
    if user:
        token = secrets.token_urlsafe(32)
        from datetime import timedelta
        await db.password_reset_tokens.insert_one({
            "token": token,
            "user_id": str(user["_id"]),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "used": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        dev_link = _make_reset_link(token)
        logger.info(f"[PASSWORD RESET] {email} -> {dev_link}")
        return {"ok": True, "dev_reset_link": dev_link}
    return {"ok": True, "dev_reset_link": None}


@api_router.post("/auth/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    tok = await db.password_reset_tokens.find_one({"token": payload.token})
    if not tok or tok.get("used"):
        raise HTTPException(status_code=400, detail="Invalid or already-used reset link")
    if datetime.fromisoformat(tok["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset link expired")
    await db.users.update_one(
        {"_id": ObjectId(tok["user_id"])},
        {"$set": {"password_hash": hash_password(payload.new_password)}},
    )
    await db.password_reset_tokens.update_one({"_id": tok["_id"]}, {"$set": {"used": True}})
    return {"ok": True}


@api_router.post("/auth/verify-email")
async def verify_email(payload: VerifyEmailRequest):
    user = await db.users.find_one({"verify_token": payload.token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification link")
    if user.get("email_verified"):
        return {"ok": True, "already_verified": True}
    if user.get("verify_token_expires"):
        if datetime.fromisoformat(user["verify_token_expires"]) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Verification link expired")
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"email_verified": True}, "$unset": {"verify_token": "", "verify_token_expires": ""}},
    )
    return {"ok": True}


@api_router.post("/auth/resend-verification")
async def resend_verification(user: dict = Depends(_current_user)):
    if user.get("email_verified"):
        return {"ok": True, "already_verified": True}
    from datetime import timedelta
    token = secrets.token_urlsafe(32)
    await db.users.update_one(
        {"_id": ObjectId(user["id"])},
        {"$set": {
            "verify_token": token,
            "verify_token_expires": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        }},
    )
    dev_link = _make_verify_link(token)
    logger.info(f"[VERIFY EMAIL RESEND] {user['email']} -> {dev_link}")
    return {"ok": True, "dev_verify_link": dev_link}


# ============ QUIZ ROUTES ============
@api_router.get("/quiz/categories")
async def get_categories():
    return {"categories": CATEGORIES, "difficulties": DIFFICULTIES}


async def _load_admin_questions() -> List[dict]:
    """Load admin-authored questions from Mongo, formatted like static QUESTIONS entries."""
    docs = await db.admin_questions.find({}).to_list(length=1000)
    out = []
    for d in docs:
        out.append({
            "id": f"adm-{str(d['_id'])}",
            "category": d.get("category"),
            "difficulty": d.get("difficulty"),
            "question": d.get("question"),
            "options": d.get("options", []),
            "correct_index": d.get("correct_index", 0),
        })
    return out


async def _get_question_by_id(qid: str) -> Optional[dict]:
    if qid in QUESTIONS_BY_ID:
        return QUESTIONS_BY_ID[qid]
    if qid.startswith("adm-"):
        try:
            doc = await db.admin_questions.find_one({"_id": ObjectId(qid[4:])})
        except Exception:
            return None
        if doc:
            return {
                "id": qid, "category": doc.get("category"), "difficulty": doc.get("difficulty"),
                "question": doc.get("question"), "options": doc.get("options", []),
                "correct_index": doc.get("correct_index", 0),
            }
    return None


@api_router.post("/quiz/start", response_model=QuizStartResponse)
async def start_quiz(payload: QuizStartRequest, user: dict = Depends(_current_user)):
    pool = list(QUESTIONS) + await _load_admin_questions()
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
        "negative_marking": payload.negative_marking,
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
    negative = bool(session.get("negative_marking", payload.negative_marking))
    review: List[ReviewItem] = []
    correct = 0
    difficulty_weight = {"Easy": 10, "Medium": 15, "Hard": 20}
    score = 0
    for ans in payload.answers:
        if ans.question_id not in valid_ids:
            continue
        q = await _get_question_by_id(ans.question_id)
        if not q:
            continue
        is_correct = ans.selected_index == q["correct_index"]
        if is_correct:
            correct += 1
            score += difficulty_weight.get(q["difficulty"], 10)
        elif negative and ans.selected_index is not None:
            score -= 5
        review.append(ReviewItem(
            question_id=q["id"], question=q["question"], options=q["options"],
            correct_index=q["correct_index"], selected_index=ans.selected_index,
            is_correct=is_correct,
        ))
    total = len(review)
    wrong = total - correct
    accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0
    passed = accuracy >= 70.0
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
        "negative_marking": negative,
        "passed": passed,
        "created_at": now_iso,
    }
    ins = await db.quiz_results.insert_one(result_doc)
    return QuizResult(
        id=str(ins.inserted_id), user_name=user["name"],
        category=payload.category, difficulty=payload.difficulty,
        total=total, correct=correct, wrong=wrong, score=score, accuracy=accuracy,
        negative_marking=negative, passed=passed,
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
            user_id=d.get("user_id"),
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


# ============ CERTIFICATE ============
@api_router.get("/quiz/certificate/{result_id}")
async def get_certificate(result_id: str, user: dict = Depends(_current_user)):
    try:
        oid = ObjectId(result_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid result id")
    doc = await db.quiz_results.find_one({"_id": oid, "user_id": user["id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Result not found")
    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=landscape(A4))
    w, h = landscape(A4)
    # Retro-terminal dark green background
    c.setFillColorRGB(0.02, 0.04, 0.02)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    # Border
    c.setStrokeColorRGB(0.13, 0.77, 0.37)
    c.setLineWidth(2)
    c.rect(0.3 * inch, 0.3 * inch, w - 0.6 * inch, h - 0.6 * inch, stroke=1, fill=0)
    c.setLineWidth(0.5)
    c.rect(0.45 * inch, 0.45 * inch, w - 0.9 * inch, h - 0.9 * inch, stroke=1, fill=0)
    # Header
    c.setFillColorRGB(0.13, 0.77, 0.37)
    c.setFont("Courier-Bold", 14)
    c.drawCentredString(w / 2, h - 1.0 * inch, "== RETRO :: QUIZ ==")
    c.setFont("Courier", 10)
    c.drawCentredString(w / 2, h - 1.25 * inch, "CERTIFICATE OF ACHIEVEMENT")
    # Body
    c.setFont("Courier-Bold", 32)
    c.drawCentredString(w / 2, h - 2.4 * inch, doc.get("user_name", "Player"))
    c.setFont("Courier", 12)
    c.drawCentredString(w / 2, h - 2.9 * inch, "has completed the quiz")
    cat = doc.get("category", "Mixed")
    diff = doc.get("difficulty", "Mixed")
    c.setFont("Courier-Bold", 18)
    c.setFillColorRGB(0.98, 0.80, 0.08)  # yellow accent
    c.drawCentredString(w / 2, h - 3.5 * inch, f"[ {cat}  ::  {diff} ]")
    # Stats
    c.setFillColorRGB(0.13, 0.77, 0.37)
    c.setFont("Courier", 12)
    stats_y = h - 4.3 * inch
    c.drawCentredString(w / 2, stats_y,
                        f"score: {doc.get('score',0)}   accuracy: {doc.get('accuracy',0)}%   "
                        f"correct: {doc.get('correct',0)}/{doc.get('total',0)}")
    # Passed / failed stamp
    passed = doc.get("passed") or (doc.get("accuracy", 0) >= 70)
    if passed:
        c.setFillColorRGB(0.13, 0.77, 0.37)
        c.setFont("Courier-Bold", 22)
        c.drawCentredString(w / 2, h - 5.0 * inch, ">> STATUS: PASSED <<")
    else:
        c.setFillColorRGB(0.94, 0.27, 0.27)
        c.setFont("Courier-Bold", 18)
        c.drawCentredString(w / 2, h - 5.0 * inch, ">> STATUS: TRAINING MODE <<")
    # Footer date
    c.setFillColorRGB(0.10, 0.50, 0.24)
    c.setFont("Courier", 9)
    date_str = doc.get("created_at", "")[:10]
    c.drawCentredString(w / 2, 0.9 * inch, f"issued :: {date_str}   .   retro_quiz.exe   .   id :: {result_id[-8:]}")
    c.showPage()
    c.save()
    buf.seek(0)
    filename = f"retroquiz_certificate_{result_id[-8:]}.pdf"
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})


# ============ ADMIN ============
@api_router.get("/admin/questions")
async def admin_list_questions(admin: dict = Depends(_current_admin)):
    docs = await db.admin_questions.find({}).sort("created_at", -1).to_list(length=500)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@api_router.post("/admin/questions")
async def admin_add_question(payload: AdminQuestionCreate, admin: dict = Depends(_current_admin)):
    if payload.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    if payload.difficulty not in DIFFICULTIES:
        raise HTTPException(status_code=400, detail="Invalid difficulty")
    doc = {
        "category": payload.category,
        "difficulty": payload.difficulty,
        "question": payload.question.strip(),
        "options": [o.strip() for o in payload.options],
        "correct_index": payload.correct_index,
        "created_by": admin["email"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ins = await db.admin_questions.insert_one(doc)
    doc["id"] = str(ins.inserted_id)
    doc.pop("_id", None)
    return doc


@api_router.delete("/admin/questions/{qid}")
async def admin_delete_question(qid: str, admin: dict = Depends(_current_admin)):
    try:
        oid = ObjectId(qid)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")
    res = await db.admin_questions.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"ok": True}


@api_router.get("/admin/analytics")
async def admin_analytics(admin: dict = Depends(_current_admin)):
    total_users = await db.users.count_documents({})
    verified_users = await db.users.count_documents({"email_verified": True})
    total_games = await db.quiz_results.count_documents({})
    total_admin_questions = await db.admin_questions.count_documents({})
    # aggregate
    pipeline_cat = [
        {"$group": {"_id": "$category", "games": {"$sum": 1}, "avg_score": {"$avg": "$score"},
                    "avg_accuracy": {"$avg": "$accuracy"}}},
        {"$sort": {"games": -1}},
    ]
    cat_stats = []
    async for row in db.quiz_results.aggregate(pipeline_cat):
        cat_stats.append({
            "category": row["_id"], "games": row["games"],
            "avg_score": round(row["avg_score"] or 0, 1),
            "avg_accuracy": round(row["avg_accuracy"] or 0, 1),
        })
    # top players
    pipeline_top = [
        {"$group": {"_id": "$user_id", "user_name": {"$last": "$user_name"},
                    "best_score": {"$max": "$score"}, "games": {"$sum": 1}}},
        {"$sort": {"best_score": -1}}, {"$limit": 5},
    ]
    top_players = []
    async for row in db.quiz_results.aggregate(pipeline_top):
        top_players.append({
            "user_id": row["_id"], "user_name": row["user_name"],
            "best_score": row["best_score"], "games": row["games"],
        })
    # aggregate stats
    overall_avg_accuracy = 0.0
    if total_games:
        pipeline_avg = [{"$group": {"_id": None, "avg": {"$avg": "$accuracy"}}}]
        async for row in db.quiz_results.aggregate(pipeline_avg):
            overall_avg_accuracy = round(row["avg"] or 0, 1)
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "total_games": total_games,
        "total_admin_questions": total_admin_questions,
        "static_questions": len(QUESTIONS),
        "overall_avg_accuracy": overall_avg_accuracy,
        "by_category": cat_stats,
        "top_players": top_players,
    }


@api_router.post("/admin/ai-generate")
async def admin_ai_generate(payload: AIGenerateRequest, admin: dict = Depends(_current_admin)):
    """Generate MCQ questions using Gemini 3 Flash via emergentintegrations. Returns generated
    questions (not persisted). Admin can review and save selected ones via /admin/questions."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM key not configured")
    system_msg = (
        "You generate high-quality multiple-choice questions for a computer-science quiz app. "
        "Always respond with STRICT JSON only, no prose, no code fences."
    )
    prompt = (
        f"Generate {payload.count} multiple-choice questions on the topic \"{payload.topic}\" "
        f"at {payload.difficulty} difficulty.\n\n"
        "Respond with a JSON array where each element has this shape:\n"
        '{"question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0}\n\n'
        "Rules:\n"
        "- Exactly 4 options.\n"
        "- correct_index is 0..3 pointing to the correct option.\n"
        "- Options must be short (≤ 60 chars).\n"
        "- No duplicate questions.\n"
        "- Return ONLY the JSON array, nothing else."
    )
    session_id = f"quiz-ai-{secrets.token_hex(8)}"
    chat = LlmChat(api_key=api_key, session_id=session_id, system_message=system_msg).with_model(
        "gemini", "gemini-3-flash-preview"
    )
    try:
        raw = await chat.send_message(UserMessage(text=prompt))
    except Exception as e:
        logger.exception("AI generate failed")
        raise HTTPException(status_code=502, detail=f"AI generation error: {e}")
    text = raw.strip() if isinstance(raw, str) else str(raw)
    # Strip code fences if any
    if text.startswith("```"):
        # ```json ... ```
        parts = text.split("```")
        # take the largest inner block
        text = max((p for p in parts if p.strip()), key=len)
        if text.lstrip().lower().startswith("json"):
            text = text.split("\n", 1)[1] if "\n" in text else text[4:]
    try:
        parsed: Any = jsonlib.loads(text)
    except Exception:
        # Try to extract the JSON array substring
        start = text.find("[")
        end = text.rfind("]")
        if start >= 0 and end > start:
            try:
                parsed = jsonlib.loads(text[start:end + 1])
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"AI returned invalid JSON: {e}")
        else:
            raise HTTPException(status_code=502, detail="AI returned invalid JSON")
    if not isinstance(parsed, list):
        raise HTTPException(status_code=502, detail="AI response is not a JSON array")
    # Normalize/validate
    out = []
    for item in parsed:
        try:
            q = str(item["question"]).strip()
            opts = [str(o).strip() for o in item["options"]]
            ci = int(item["correct_index"])
            if len(opts) != 4 or not (0 <= ci <= 3) or not q:
                continue
            out.append({"question": q, "options": opts, "correct_index": ci})
        except Exception:
            continue
    if not out:
        raise HTTPException(status_code=502, detail="AI produced no valid questions; try again")
    return {"topic": payload.topic, "difficulty": payload.difficulty, "questions": out}


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


@app.on_event("startup")
async def on_startup():
    await db.users.create_index("email", unique=True)
    await db.quiz_results.create_index([("score", -1)])
    await db.password_reset_tokens.create_index("token", unique=True)
    await db.admin_questions.create_index([("category", 1), ("difficulty", 1)])
    # Seed admin account
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@quiz.sys").lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "email": admin_email,
            "name": "Admin",
            "password_hash": hash_password(admin_password),
            "role": "admin",
            "email_verified": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info(f"Seeded admin user: {admin_email}")
    else:
        updates = {}
        if existing.get("role") != "admin":
            updates["role"] = "admin"
        if not existing.get("email_verified"):
            updates["email_verified"] = True
        if not verify_password(admin_password, existing["password_hash"]):
            updates["password_hash"] = hash_password(admin_password)
        if updates:
            await db.users.update_one({"_id": existing["_id"]}, {"$set": updates})
            logger.info(f"Updated admin user: {admin_email}")
    logger.info("Retro Quiz backend started.")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
