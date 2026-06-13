from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(prefix="/items", tags=["Items"])

# 1. 获取列表 (Read List)
@router.get("/", response_model=List[ItemSchema])
def read_items(skip: int = 0, limit: int = 10, db=Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit)

# 2. 静态特殊路径 (Must be before /{item_id})
@router.get("/active")
def read_active_items(db=Depends(get_db)):
    return crud.get_active_items(db)

# 3. 获取详情 (Read Detail)
@router.get("/{item_id}", response_model=ItemSchema)
def read_item(item_id: int, db=Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# 4. 创建 (Create)
@router.post("/", response_model=ItemSchema, status_code=201)
def create_item(item: ItemCreate, db=Depends(get_db)):
    return crud.create_item(db=db, item=item)

# 5. 局部更新 (Update)
@router.patch("/{item_id}", response_model=ItemSchema)
def update_item(item_id: int, item: ItemUpdate, db=Depends(get_db)):
    return crud.update_item(db=db, item_id=item_id, item=item)

# 6. 删除 (Delete)
@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db=Depends(get_db)):
    crud.delete_item(db=db, item_id=item_id)
    return None