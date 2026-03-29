import uuid
import time
from fastapi import FastAPI, Cookie, Response
from pydantic import BaseModel
from typing import Optional
from itsdangerous import URLSafeSerializer, BadSignature

app = FastAPI(title="Задание 5.3 ")

SECRET_KEY = "super-secret-key-change-in-production"
serializer = URLSafeSerializer(SECRET_KEY, salt="session-v3")

SESSION_LIFETIME = 300        
REFRESH_THRESHOLD = 180       

FAKE_USERS = {
    "user123": {
        "password": "password123",
        "profile": {"username": "user123", "email": "user123@example.com", "full_name": "Иван Иванов"},
    },
    "alice": {
        "password": "alice_pass",
        "profile": {"username": "alice", "email": "alice@example.com", "full_name": "Алиса Смирнова"},
    },
}

user_store: dict[str, str] = {}

class LoginData(BaseModel):
    username: str
    password: str

def create_token(user_id: str, timestamp: int) -> str:
    payload = f"{user_id}:{timestamp}"
    return serializer.dumps(payload)

def parse_token(token: str) -> Optional[tuple[str, int]]:
    try:
        payload: str = serializer.loads(token)
    except BadSignature:
        return None
    parts = payload.split(":", 1)
    if len(parts) != 2:
        return None
    user_id, ts_str = parts
    try:
        timestamp = int(ts_str)
    except ValueError:
        return None
    return user_id, timestamp


def build_cookie(response: Response, user_id: str, timestamp: int) -> None:
    token = create_token(user_id, timestamp)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,      
        max_age=SESSION_LIFETIME,
        samesite="lax",
    )

@app.post("/login")
def login(data: LoginData, response: Response):
    user = FAKE_USERS.get(data.username)
    if user is None or user["password"] != data.password:
        response.status_code = 401
        return {"message": "Неверный логин или пароль"}
    user_id = str(uuid.uuid4())
    user_store[user_id] = data.username
    now = int(time.time())
    build_cookie(response, user_id, now)
    return {"message": "Вход выполнен успешно"}


@app.get("/profile")
def get_profile(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token is None:
        response.status_code = 401
        return {"message": "Unauthorized"}
    parsed = parse_token(session_token)
    if parsed is None:
        response.status_code = 401
        return {"message": "Invalid session"}
    user_id, last_active = parsed
    if user_id not in user_store:
        response.status_code = 401
        return {"message": "Invalid session"}
    now = int(time.time())
    elapsed = now - last_active
    if elapsed >= SESSION_LIFETIME:
        response.status_code = 401
        return {"message": "Session expired"}
    if elapsed >= REFRESH_THRESHOLD:
        # Прошло ≥ 3 и < 5 минут → продлеваем сессию
        build_cookie(response, user_id, now)
        
    username = user_store[user_id]
    return {
        "profile": FAKE_USERS[username]["profile"],
        "session_info": {
            "last_active_seconds_ago": elapsed,
            "cookie_refreshed": elapsed >= REFRESH_THRESHOLD,
        },
    }
