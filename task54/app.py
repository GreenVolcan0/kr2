import re
from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="Задание 5.4")

ACCEPT_LANGUAGE_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?"
    r"(;q=[01](\.\d{1,3})?)?"
    r"(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(;q=[01](\.\d{1,3})?)?)*$"
)

@app.get("/headers")
def get_headers(request: Request):
    user_agent = request.headers.get("user-agent")
    accept_language = request.headers.get("accept-language")

    if not user_agent:
        raise HTTPException(
            status_code=400,
            detail="Заголовок 'User-Agent' обязателен и отсутствует в запросе",
        )
    if not accept_language:
        raise HTTPException(
            status_code=400,
            detail="Заголовок 'Accept-Language' обязателен и отсутствует в запросе",
        )
    if not ACCEPT_LANGUAGE_RE.match(accept_language):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Неверный формат заголовка 'Accept-Language': '{accept_language}'. "
                "Ожидается формат вида 'en-US,en;q=0.9,es;q=0.8'"
            ),
        )
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language,
    }
