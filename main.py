from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union

# 1. Налаштування
# --------------------

app = FastAPI(title="Heil PYTHON") #Назву можно змінити

class Item(BaseModel):
    name: str
    image_url: str
    price: float

# Наша "фальшива" база даних
items_db = []
next_id = 1


# 2. "Розумна" функція для додавання товару
# ----------------------------------------
# Ця допоміжна функція обробляє логіку додавання
# одного товару в БД, щоб уникнути дублювання коду.
def add_item_to_db(item: Item) -> dict:
    global next_id
    new_item = {
        "id": next_id,
        "name": item.name,
        "image_url": item.image_url,
        "price": item.price
    }
    items_db.append(new_item)
    next_id += 1
    return new_item


# 3. Маршрути (Endpoints)
# --------------------

@app.get("/")
def root():
    return {"message": "Вітаю! Це просте API без бази даних 👋"}

@app.get("/items")
def get_items():
    return items_db

# Ось головна зміна:
# FastAPI тепер очікує або один 'Item', або 'List[Item]'
@app.post("/items")
def create_item(payload: Union[Item, List[Item]]):

    # Випадок 1: Нам надіслали список товарів
    if isinstance(payload, list):
        created_items_list = []
        # Просто проходимо по списку і додаємо кожен товар
        for item in payload:
            new_item = add_item_to_db(item)
            created_items_list.append(new_item)

        return {"message": f"Успішно додано {len(created_items_list)} товарів", "items": created_items_list}

    # Випадок 2: Нам надіслали один товар (якщо це не список)
    elif isinstance(payload, Item):
        new_item = add_item_to_db(payload)
        return {"message": "Товар успішно додано", "item": new_item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    item_to_delete = None
    for item in items_db:
        if item["id"] == item_id:
            item_to_delete = item
            break

    if item_to_delete:
        items_db.remove(item_to_delete)
        return {"message": f"Товар з id={item_id} видалено"}

    raise HTTPException(status_code=404, detail=f"Товар з id={item_id} не знайдено")

