import re
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Response

app = FastAPI(title="Задание 5.5")

# Регулярка для валидации Accept-Language
ACCEPT_LANGUAGE_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?"
    r"(;q=[01](\.\d{1,3})?)?"
    r"(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(;q=[01](\.\d{1,3})?)?)*$"
)

from dataclasses import dataclass
from fastapi import Depends


@dataclass
class CommonHeaders:
    user_agent: str
    accept_language: str

def get_common_headers(
    user_agent: Annotated[str | None, Header(alias="user-agent")] = None,
    accept_language: Annotated[str | None, Header(alias="accept-language")] = None,
) -> CommonHeaders:
    if not user_agent:
        raise HTTPException(
            status_code=400,
            detail="Заголовок 'User-Agent' обязателен и отсутствует",
        )
    if not accept_language:
        raise HTTPException(
            status_code=400,
            detail="Заголовок 'Accept-Language' обязателен и отсутствует",
        )

    if not ACCEPT_LANGUAGE_RE.match(accept_language):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Неверный формат 'Accept-Language': '{accept_language}'. "
                "Ожидается формат вида 'en-US,en;q=0.9,es;q=0.8'"
            ),
        )
    return CommonHeaders(user_agent=user_agent, accept_language=accept_language)

@app.get("/headers")
def headers_route(headers: Annotated[CommonHeaders, Depends(get_common_headers)]):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }

@app.get("/info")
def info_route(
    response: Response,
    headers: Annotated[CommonHeaders, Depends(get_common_headers)],
):
    server_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    response.headers["X-Server-Time"] = server_time

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }
