from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI(title="Задание 3.2")

sample_product_1 = {"product_id": 123, "name": "Smartphone",  "category": "Electronics",  "price": 599.99}
sample_product_2 = {"product_id": 456, "name": "Phone Case",  "category": "Accessories",  "price": 19.99}
sample_product_3 = {"product_id": 789, "name": "Iphone",      "category": "Electronics",  "price": 1299.99}
sample_product_4 = {"product_id": 101, "name": "Headphones",  "category": "Accessories",  "price": 99.99}
sample_product_5 = {"product_id": 202, "name": "Smartwatch",  "category": "Electronics",  "price": 299.99}

sample_products = [
    sample_product_1,
    sample_product_2,
    sample_product_3,
    sample_product_4,
    sample_product_5,
]

# ВАЖНО: маршрут /products/search объявлен РАНЬШЕ /product/{id},
# иначе FastAPI попытается привести строку "search" к int и упадёт.

@app.get("/products/search")
def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10,
):
    results = []
    for product in sample_products:
        name_matches = keyword.lower() in product["name"].lower()
        category_matches = (category is None) or (product["category"].lower() == category.lower())
        if name_matches and category_matches:
            results.append(product)
    return results[:limit]

@app.get("/product/{product_id}")
def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail=f"Продукт с id={product_id} не найден")
