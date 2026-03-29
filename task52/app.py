import uuid
from fastapi import FastAPI, Cookie, Response
from pydantic import BaseModel
from typing import Optional
from itsdangerous import URLSafeSerializer, BadSignature

app = FastAPI(title="Задание 5.2 ")

SECRET_KEY = "super-secret-key-change-in-production"

serializer = URLSafeSerializer(SECRET_KEY, salt="session")

FAKE_USERS = {
    "user123": {
        "password": "password123",
        "profile": {
            "username": "user123",
            "email": "user123@example.com",
            "full_name": "Иван Иванов",
        },
    },
    "alice": {
        "password": "alice_pass",
        "profile": {
            "username": "alice",
            "email": "alice@example.com",
            "full_name": "Алиса Смирнова",
        },
    },
}

user_store: dict[str, str] = {}

class LoginData(BaseModel):
    username: str
    password: str

def create_session_token(user_id: str) -> str:
    return serializer.dumps(user_id)

def verify_session_token(token: str) -> Optional[str]:
    try:
        user_id = serializer.loads(token)
        return user_id
    except BadSignature:
        return None

@app.post("/login")
def login(data: LoginData, response: Response):
    user = FAKE_USERS.get(data.username)
    if user is None or user["password"] != data.password:
        response.status_code = 401
        return {"message": "Неверный логин или пароль"}
    user_id = str(uuid.uuid4())
    user_store[user_id] = data.username
    token = create_session_token(user_id)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=3600,
        samesite="lax",
    )
    return {"message": "Вход выполнен успешно", "session_token": token}

@app.get("/profile")
def get_profile(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token is None:
        response.status_code = 401
        return {"message": "Unauthorized"}
    user_id = verify_session_token(session_token)
    if user_id is None or user_id not in user_store:
        response.status_code = 401
        return {"message": "Unauthorized"}
    username = user_store[user_id]
    return FAKE_USERS[username]["profile"]
