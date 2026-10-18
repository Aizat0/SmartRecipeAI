from mysite.database.models import Category, UserProfile
from mysite.database.schema import CategoryInputSchema, CategoryOutSchema
from mysite.database.db import SessionLocal
from mysite.api.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from typing import List

category_router = APIRouter(prefix='/category', tags=['Category'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@category_router.post('/', response_model=CategoryOutSchema)
async def create_category(category: CategoryInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    category_db = Category(**category.model_dump())
    db.add(category_db)
    db.commit()
    db.refresh(category_db)
    return category_db


@category_router.get('/', response_model=List[CategoryOutSchema])
async def list_category(db: Session = Depends(get_db)):
    return db.query(Category).all()


@category_router.get('/{category_id}/', response_model=CategoryOutSchema)
async def detail_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(detail='Мындай маалымат жок', status_code=404)
    return category


@category_router.put('/{category_id}/', response_model=dict)
async def update_category(category_id: int, category: CategoryInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(detail='Мындай категория жок', status_code=404)
    for category_key, category_value in category.model_dump().items():
        setattr(category_db, category_key, category_value)
    db.commit()
    db.refresh(category_db)
    return {'message': 'Категория озгорулду'}


@category_router.delete('/{category_id}/', response_model=dict)
async def delete_category(category_id: int, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(detail='Мындай категория жок', status_code=404)
    db.delete(category_db)
    db.commit()
    return {'message': 'Категория удалить болду'}
