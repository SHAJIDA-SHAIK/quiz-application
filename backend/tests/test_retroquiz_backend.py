"""Backend tests for Retro Quiz iteration 2.

Covers:
- Auth (register/login/verify-email/resend/forgot/reset)
- Admin seeding + admin RBAC
- Quiz (categories, start, submit, negative marking, passed flag)
- Admin CRUD questions & analytics & AI generation
- Certificate PDF
- Leaderboard user_id inclusion
"""
import os
import time
import uuid
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL") or "https://trivia-challenge-118.preview.emergentagent.com"
BASE_URL = BASE_URL.rstrip("/")

ADMIN_EMAIL = "admin@quiz.sys"
ADMIN_PASSWORD = "admin123"


# ------------- fixtures -------------
@pytest.fixture(scope="session")
def admin_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=20)
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    body = r.json()
    assert body.get("role") == "admin"
    assert body.get("email_verified") is True
    return s


@pytest.fixture(scope="session")
def user_session():
    """Register a fresh test user and return an authenticated session + user info + verify_link."""
    s = requests.Session()
    email = f"test_user_{uuid.uuid4().hex[:8]}@quiz.sys"
    password = "player123"
    r = s.post(f"{BASE_URL}/api/auth/register", json={"name": "Test User", "email": email, "password": password}, timeout=20)
    assert r.status_code == 200, f"register failed: {r.status_code} {r.text}"
    body = r.json()
    assert body["email"] == email
    assert body["email_verified"] is False
    assert body["role"] == "user"
    assert "dev_verify_link" in body and body["dev_verify_link"]
    return {
        "session": s,
        "email": email,
        "password": password,
        "id": body["id"],
        "verify_link": body["dev_verify_link"],
    }


# ============ AUTH / ADMIN SEED ============
class TestAuthAndAdminSeed:
    def test_admin_can_login(self, admin_session):
        # If fixture succeeded we're good; verify /me returns admin role
        r = admin_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        me = r.json()
        assert me["role"] == "admin"
        assert me["email_verified"] is True
        assert me["email"] == ADMIN_EMAIL

    def test_register_returns_dev_verify_link(self, user_session):
        assert user_session["verify_link"].startswith("http")
        assert "/verify-email?token=" in user_session["verify_link"]

    def test_verify_email_and_reuse_is_already_verified(self, user_session):
        token = user_session["verify_link"].split("token=", 1)[1]
        # first call verifies
        r = requests.post(f"{BASE_URL}/api/auth/verify-email", json={"token": token}, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert body.get("ok") is True
        # Second call: token has been unset from user so it becomes invalid, not "already_verified".
        # NOTE: This is a behavior detail — spec says already-used token should return already_verified:true.
        r2 = requests.post(f"{BASE_URL}/api/auth/verify-email", json={"token": token}, timeout=15)
        # accept either behavior but flag mismatch
        if r2.status_code == 200:
            j = r2.json()
            assert j.get("already_verified") is True
        else:
            # Report as failure to be visible in report
            pytest.fail(
                f"Reusing verify token returned {r2.status_code} instead of 200 already_verified. body={r2.text}"
            )

    def test_resend_verification_for_new_unverified_user(self):
        s = requests.Session()
        email = f"test_resend_{uuid.uuid4().hex[:8]}@quiz.sys"
        r = s.post(f"{BASE_URL}/api/auth/register", json={"name": "R", "email": email, "password": "player123"}, timeout=15)
        assert r.status_code == 200
        r2 = s.post(f"{BASE_URL}/api/auth/resend-verification", timeout=15)
        assert r2.status_code == 200
        body = r2.json()
        assert body.get("ok") is True
        assert body.get("dev_verify_link", "").startswith("http")

    def test_forgot_password_existing_user(self, user_session):
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": user_session["email"]}, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body.get("dev_reset_link", "").startswith("http")

    def test_forgot_password_unknown_user_returns_null(self):
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": f"nobody_{uuid.uuid4().hex[:8]}@quiz.sys"}, timeout=15)
        assert r.status_code == 200
        assert r.json().get("dev_reset_link") is None

    def test_reset_password_flow_and_token_reuse_rejected(self, user_session):
        # request a reset link
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": user_session["email"]}, timeout=15)
        link = r.json().get("dev_reset_link")
        assert link
        token = link.split("token=", 1)[1]
        new_pw = "newPass123!"
        r2 = requests.post(f"{BASE_URL}/api/auth/reset-password", json={"token": token, "new_password": new_pw}, timeout=15)
        assert r2.status_code == 200
        # login with new password
        s = requests.Session()
        r3 = s.post(f"{BASE_URL}/api/auth/login", json={"email": user_session["email"], "password": new_pw}, timeout=15)
        assert r3.status_code == 200
        # reuse token -> should 400
        r4 = requests.post(f"{BASE_URL}/api/auth/reset-password", json={"token": token, "new_password": "anotherPw123"}, timeout=15)
        assert r4.status_code == 400
        # update fixture session to still work with the new password
        user_session["password"] = new_pw
        s2 = requests.Session()
        s2.post(f"{BASE_URL}/api/auth/login", json={"email": user_session["email"], "password": new_pw}, timeout=15)
        user_session["session"] = s2


# ============ QUIZ + QUESTION BANK ============
class TestQuizCore:
    def test_categories(self, user_session):
        r = requests.get(f"{BASE_URL}/api/quiz/categories", timeout=15)
        assert r.status_code == 200
        j = r.json()
        assert set(j["categories"]) == {"Python", "DBMS", "OS", "Aptitude"}
        assert set(j["difficulties"]) == {"Easy", "Medium", "Hard"}

    @pytest.mark.parametrize("cat,diff", [
        ("Python", "Easy"), ("Python", "Medium"), ("Python", "Hard"),
        ("DBMS", "Easy"), ("DBMS", "Medium"), ("DBMS", "Hard"),
        ("OS", "Easy"), ("OS", "Medium"), ("OS", "Hard"),
        ("Aptitude", "Easy"), ("Aptitude", "Medium"), ("Aptitude", "Hard"),
    ])
    def test_start_quiz_all_combinations_return_questions(self, user_session, cat, diff):
        s = user_session["session"]
        r = s.post(f"{BASE_URL}/api/quiz/start",
                   json={"category": cat, "difficulty": diff, "num_questions": 5}, timeout=15)
        assert r.status_code == 200, r.text
        j = r.json()
        assert len(j["questions"]) > 0
        assert j["time_per_question"] == 20

    def test_bank_has_at_least_80(self, user_session):
        s = user_session["session"]
        r = s.post(f"{BASE_URL}/api/quiz/start", json={"category": "Mixed", "difficulty": "Mixed", "num_questions": 80}, timeout=15)
        assert r.status_code == 200
        j = r.json()
        assert len(j["questions"]) >= 80, f"expected >=80 questions in Mixed/Mixed pool, got {len(j['questions'])}"


# ============ NEGATIVE MARKING + PASSED ============
class TestSubmitAndScoring:
    def _start(self, s, negative):
        r = s.post(f"{BASE_URL}/api/quiz/start",
                   json={"category": "Python", "difficulty": "Easy", "num_questions": 5, "negative_marking": negative},
                   timeout=15)
        assert r.status_code == 200
        return r.json()

    def test_negative_marking_penalty(self, user_session):
        s = user_session["session"]
        start = self._start(s, negative=True)
        answers = []
        # For a controllable score, submit ALL WRONG (except skip one)
        for i, q in enumerate(start["questions"]):
            if i == 0:
                # Skipped answer should NOT be penalized
                answers.append({"question_id": q["id"], "selected_index": None, "time_taken": 0})
            else:
                # deliberately wrong: pick index 3 unless that happens to be right, then pick 0
                # We don't know the correct index from public data, so pick a fixed guess.
                answers.append({"question_id": q["id"], "selected_index": 3, "time_taken": 0})
        r = s.post(f"{BASE_URL}/api/quiz/submit",
                   json={"quiz_id": start["quiz_id"], "category": "Python", "difficulty": "Easy",
                         "answers": answers, "negative_marking": True}, timeout=15)
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["negative_marking"] is True
        # score should include -5 per wrong (there will be some wrong)
        # verify formula: score = 10*correct - 5*wrong_non_skipped (Easy weight=10)
        wrong_non_skipped = sum(1 for a, item in zip(answers, j["review"]) if a["selected_index"] is not None and not item["is_correct"])
        expected_score = 10 * j["correct"] - 5 * wrong_non_skipped
        assert j["score"] == expected_score, f"score {j['score']} != expected {expected_score}; correct={j['correct']} wrong_non_skipped={wrong_non_skipped}"
        # passed flag should be boolean
        assert isinstance(j["passed"], bool)
        assert j["passed"] == (j["accuracy"] >= 70.0)

    def test_no_penalty_when_flag_false(self, user_session):
        s = user_session["session"]
        start = self._start(s, negative=False)
        answers = [{"question_id": q["id"], "selected_index": 3, "time_taken": 0} for q in start["questions"]]
        r = s.post(f"{BASE_URL}/api/quiz/submit",
                   json={"quiz_id": start["quiz_id"], "category": "Python", "difficulty": "Easy",
                         "answers": answers, "negative_marking": False}, timeout=15)
        assert r.status_code == 200
        j = r.json()
        assert j["negative_marking"] is False
        # score should be non-negative (no penalty)
        assert j["score"] >= 0

    def test_certificate_generation_and_ownership(self, user_session):
        s = user_session["session"]
        # Do a quiz to get a result_id
        start = self._start(s, negative=False)
        answers = [{"question_id": q["id"], "selected_index": 0, "time_taken": 0} for q in start["questions"]]
        r = s.post(f"{BASE_URL}/api/quiz/submit",
                   json={"quiz_id": start["quiz_id"], "category": "Python", "difficulty": "Easy",
                         "answers": answers, "negative_marking": False}, timeout=15)
        rid = r.json()["id"]
        cr = s.get(f"{BASE_URL}/api/quiz/certificate/{rid}", timeout=20)
        assert cr.status_code == 200
        assert cr.headers.get("content-type", "").startswith("application/pdf")
        assert cr.content[:4] == b"%PDF"
        # Different user should get 404
        s2 = requests.Session()
        email2 = f"test_other_{uuid.uuid4().hex[:8]}@quiz.sys"
        s2.post(f"{BASE_URL}/api/auth/register", json={"name": "Other", "email": email2, "password": "player123"}, timeout=15)
        cr2 = s2.get(f"{BASE_URL}/api/quiz/certificate/{rid}", timeout=15)
        assert cr2.status_code == 404, f"other user could access cert, got {cr2.status_code}"

    def test_leaderboard_includes_user_id(self, user_session):
        r = requests.get(f"{BASE_URL}/api/quiz/leaderboard?limit=10", timeout=15)
        assert r.status_code == 200
        entries = r.json()
        assert isinstance(entries, list)
        assert len(entries) > 0
        # each entry has user_id field (may or may not be None for old rows)
        assert "user_id" in entries[0]


# ============ ADMIN RBAC + CRUD + ANALYTICS + AI ============
class TestAdmin:
    def test_non_admin_forbidden(self, user_session):
        s = user_session["session"]
        r = s.get(f"{BASE_URL}/api/admin/questions", timeout=15)
        assert r.status_code == 403
        r2 = s.get(f"{BASE_URL}/api/admin/analytics", timeout=15)
        assert r2.status_code == 403

    def test_admin_add_list_delete_question(self, admin_session, user_session):
        payload = {
            "category": "Python",
            "difficulty": "Easy",
            "question": "TEST_ADMIN_Q what is 2+2?",
            "options": ["1", "2", "3", "4"],
            "correct_index": 3,
        }
        r = admin_session.post(f"{BASE_URL}/api/admin/questions", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        created = r.json()
        qid = created["id"]
        # list
        r2 = admin_session.get(f"{BASE_URL}/api/admin/questions", timeout=15)
        assert r2.status_code == 200
        ids = [d["id"] for d in r2.json()]
        assert qid in ids
        # Admin question should be selectable via quiz/start pool. We'll try a few times because pool is shuffled.
        found = False
        s = user_session["session"]
        for _ in range(6):
            rs = s.post(f"{BASE_URL}/api/quiz/start",
                        json={"category": "Python", "difficulty": "Easy", "num_questions": 80}, timeout=15)
            if any(q["id"] == f"adm-{qid}" for q in rs.json()["questions"]):
                found = True
                break
        assert found, "admin-authored question not present in quiz/start pool"
        # delete
        rd = admin_session.delete(f"{BASE_URL}/api/admin/questions/{qid}", timeout=15)
        assert rd.status_code == 200
        # confirm removed
        r3 = admin_session.get(f"{BASE_URL}/api/admin/questions", timeout=15)
        ids2 = [d["id"] for d in r3.json()]
        assert qid not in ids2

    def test_admin_analytics_shape(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/analytics", timeout=15)
        assert r.status_code == 200
        j = r.json()
        for k in ["total_users", "verified_users", "total_games", "total_admin_questions",
                  "static_questions", "overall_avg_accuracy", "by_category", "top_players"]:
            assert k in j, f"missing key {k} in analytics"
        assert j["static_questions"] == 80, f"expected 80 static questions, got {j['static_questions']}"
        assert isinstance(j["by_category"], list)
        assert isinstance(j["top_players"], list)

    def test_ai_generate_gemini_flash(self, admin_session):
        r = admin_session.post(f"{BASE_URL}/api/admin/ai-generate",
                               json={"topic": "React hooks", "difficulty": "Medium", "count": 2},
                               timeout=90)
        assert r.status_code == 200, f"ai-generate failed: {r.status_code} {r.text}"
        j = r.json()
        assert "questions" in j
        assert len(j["questions"]) >= 1
        for q in j["questions"]:
            assert len(q["options"]) == 4
            assert 0 <= q["correct_index"] <= 3
            assert q["question"]
