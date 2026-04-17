from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets
from typing import List, Optional

app = FastAPI(title="Practice API for Rest Assured", version="1.0")

security = HTTPBasic()

# In-memory database (resets when server restarts - perfect for practice)
items_db: List[dict] = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Smartphone", "price": 699.99},
    {"id": 3, "name": "Headphones", "price": 149.99},
]
next_id = 4

class Item(BaseModel):
    name: str
    price: Optional[float] = None

# Basic Auth validator
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "password")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/items", response_model=List[dict], tags=["Items"])
def get_all_items(current_user: str = Depends(authenticate)):
    """Pull all records (GET)"""
    return items_db

@app.post("/items", response_model=dict, status_code=201, tags=["Items"])
def create_item(item: Item, current_user: str = Depends(authenticate)):
    """Add a new record (POST)"""
    global next_id
    new_item = {
        "id": next_id,
        "name": item.name,
        "price": item.price
    }
    items_db.append(new_item)
    next_id += 1
    return new_item

@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
def delete_item(item_id: int, current_user: str = Depends(authenticate)):
    """Delete a record by ID (DELETE)"""
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            del items_db[i]
            return {"message": f"Item {item_id} deleted successfully"}
    
    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")