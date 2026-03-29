# Контрольная работа №2 — FastAPI

## Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Задание 3.1 — POST /create_user

### Запуск
```bash
uvicorn task_3_1.app:app --reload --port 8001
```

### Тест (curl)
```bash
# Успешный запрос
curl -X POST http://localhost:8001/create_user \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "age": 30, "is_subscribed": true}'

# Ошибка — невалидный email
curl -X POST http://localhost:8001/create_user \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "not-an-email"}'

# Ошибка — отрицательный возраст
curl -X POST http://localhost:8001/create_user \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "bob@example.com", "age": -5}'
```

### Ожидаемый ответ (успех)
```json
{"name":"Alice","email":"alice@example.com","age":30,"is_subscribed":true}
```

---

## Задание 3.2 — Продукты

### Запуск
```bash
uvicorn task_3_2.app:app --reload --port 8002
```

### Тест (curl)
```bash
# Получить продукт по ID
curl http://localhost:8002/product/123

# Поиск по keyword
curl "http://localhost:8002/products/search?keyword=phone"

# Поиск с фильтром по категории и лимитом
curl "http://localhost:8002/products/search?keyword=phone&category=Electronics&limit=5"

# Несуществующий продукт → 404
curl http://localhost:8002/product/9999
```

### Ожидаемые ответы
```json
// GET /product/123
{"product_id":123,"name":"Smartphone","category":"Electronics","price":599.99}

// GET /products/search?keyword=phone&category=Electronics&limit=5
[
  {"product_id":123,"name":"Smartphone","category":"Electronics","price":599.99},
  {"product_id":789,"name":"Iphone","category":"Electronics","price":1299.99}
]
```

---

## Задание 5.1 — Cookie-аутентификация (базовая)

### Запуск
```bash
uvicorn task_5_1.app:app --reload --port 8003
```

### Тест (curl)
```bash
# Логин — сохраняем cookie в файл
curl -X POST http://localhost:8003/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "password123"}' \
  -c cookies.txt -v

# Получить профиль с cookie
curl http://localhost:8003/user -b cookies.txt

# Без cookie → 401
curl http://localhost:8003/user

# Неверный пароль → 401
curl -X POST http://localhost:8003/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "wrong"}'
```

---

## Задание 5.2 — Cookie с криптографической подписью

### Запуск
```bash
uvicorn task_5_2.app:app --reload --port 8004
```

### Тест (curl)
```bash
# Логин
curl -X POST http://localhost:8004/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "password123"}' \
  -c cookies52.txt -v

# Профиль с валидным токеном
curl http://localhost:8004/profile -b cookies52.txt

# Профиль с поддельным токеном → 401
curl http://localhost:8004/profile \
  -H "Cookie: session_token=fake.token.value"
```

---

## Задание 5.3 — Динамическое время жизни сессии

### Запуск
```bash
uvicorn task_5_3.app:app --reload --port 8005
```

### Тест (curl)
```bash
# Логин
curl -X POST http://localhost:8005/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "password123"}' \
  -c cookies53.txt

# Запрос сразу → кука НЕ обновляется (elapsed < 3 мин)
curl http://localhost:8005/profile -b cookies53.txt -c cookies53.txt

# Подождите 3 минуты, затем:
# Запрос → кука обновляется (3 ≤ elapsed < 5 мин)
curl http://localhost:8005/profile -b cookies53.txt -c cookies53.txt

# Подождите 5+ минут без запросов:
# Запрос → 401 Session expired
curl http://localhost:8005/profile -b cookies53.txt

# Поддельные данные → 401 Invalid session
curl http://localhost:8005/profile \
  -H "Cookie: session_token=fake.12345.invalidsig"
```

### Сценарии из задания
| Событие | Результат |
|---|---|
| Логин в 10:00 | Сессия до 10:05 |
| Запрос в 10:02 (elapsed=2 мин) | Кука НЕ обновляется |
| Запрос в 10:03 (elapsed=3 мин) | Кука обновляется → до 10:08 |
| Запрос в 10:05 (elapsed=2 мин от 10:03) | Кука НЕ обновляется |
| Запрос в 10:07 (elapsed=4 мин от 10:03) | Кука обновляется → до 10:12 |
| Запрос в 10:16 (elapsed=9 мин) | 401 Session expired |

---

## Задание 5.4 — Заголовки запроса

### Запуск
```bash
uvicorn task_5_4.app:app --reload --port 8006
```

### Тест (curl)
```bash
# Успешный запрос
curl http://localhost:8006/headers \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -H "Accept-Language: en-US,en;q=0.9,es;q=0.8"

# Без User-Agent → 400
curl http://localhost:8006/headers \
  -H "Accept-Language: en-US,en;q=0.9"

# Неверный формат Accept-Language → 400
curl http://localhost:8006/headers \
  -H "User-Agent: TestAgent/1.0" \
  -H "Accept-Language: INVALID FORMAT!!!"
```

---

## Задание 5.5 — CommonHeaders (DRY)

### Запуск
```bash
uvicorn task_5_5.app:app --reload --port 8007
```

### Тест (curl)
```bash
# GET /headers
curl http://localhost:8007/headers \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -H "Accept-Language: en-US,en;q=0.9,es;q=0.8"

# GET /info (в ответе будет заголовок X-Server-Time)
curl -v http://localhost:8007/info \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -H "Accept-Language: en-US,en;q=0.9,es;q=0.8"

# Без заголовков → 400
curl http://localhost:8007/info
```

### Ожидаемый ответ /info
```json
{
  "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8"
  }
}
```
И в HTTP-заголовках ответа: `X-Server-Time: 2025-04-16T12:34:56`

