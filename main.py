from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import secrets
from typing import List, Optional

app = FastAPI(
    title="Way2Automation Practice API",
    version="1.1",
    description="Enhanced API with GET by ID, PATCH update, and 10 initial records"
)

security = HTTPBasic()

# ====================== MODELS ======================
class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)

class ItemResponse(BaseModel):
    id: int
    name: str
    price: Optional[float]

# ====================== IN-MEMORY DATABASE ======================
items_db: List[dict] = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Smartphone", "price": 699.99},
    {"id": 3, "name": "Headphones", "price": 149.99},
    {"id": 4, "name": "Smart Watch", "price": 299.99},
    {"id": 5, "name": "Tablet", "price": 449.50},
    {"id": 6, "name": "Wireless Mouse", "price": 49.99},
    {"id": 7, "name": "Keyboard", "price": 89.99},
    {"id": 8, "name": "Monitor 27 inch", "price": 399.99},
    {"id": 9, "name": "External SSD 1TB", "price": 129.99},
    {"id": 10, "name": "Webcam", "price": 79.99},
]

next_id = 11

# ====================== AUTHENTICATION ======================
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


# ====================== ENDPOINTS ======================

@app.get("/items", response_model=List[ItemResponse], tags=["Items"])
def get_all_items(current_user: str = Depends(authenticate)):
    """Get all items"""
    return items_db


@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def get_item_by_id(item_id: int, current_user: str = Depends(authenticate)):
    """Get a single item by ID"""
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")


@app.post("/items", response_model=ItemResponse, status_code=201, tags=["Items"])
def create_item(item: Item, current_user: str = Depends(authenticate)):
    """Create a new item"""
    global next_id
    new_item = {
        "id": next_id,
        "name": item.name,
        "price": item.price
    }
    items_db.append(new_item)
    next_id += 1
    return new_item


@app.patch("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def update_item(item_id: int, item_update: ItemUpdate, current_user: str = Depends(authenticate)):
    """Partially update an item (PATCH)"""
    for item in items_db:
        if item["id"] == item_id:
            if item_update.name is not None:
                item["name"] = item_update.name
            if item_update.price is not None:
                item["price"] = item_update.price
            return item
    
    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")


@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
def delete_item(item_id: int, current_user: str = Depends(authenticate)):
    """Delete an item by ID"""
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            del items_db[i]
            return {"message": f"Item {item_id} deleted successfully"}
    
    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")