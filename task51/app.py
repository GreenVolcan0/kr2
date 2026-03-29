import uuid
from fastapi import FastAPI, Cookie, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Задание 5.1")

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

active_sessions: dict[str, str] = {}

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginData, response: Response):
    user = FAKE_USERS.get(data.username)
    if user is None or user["password"] != data.password:
        response.status_code = 401
        return {"message": "Неверный логин или пароль"}
    token = str(uuid.uuid4())
    active_sessions[token] = data.username
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,  
        max_age=3600,    
        samesite="lax",
    )
    return {"message": "Вход выполнен успешно", "session_token": token}

@app.get("/user")
def get_user(response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token is None or session_token not in active_sessions:
        response.status_code = 401
        return {"message": "Unauthorized"}
    username = active_sessions[session_token]
    return FAKE_USERS[username]["profile"]
