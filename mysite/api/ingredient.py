from mysite.database.models import Ingredient, UserProfile
from mysite.database.schema import IngredientInputSchema, IngredientOutSchema
from mysite.database.db import SessionLocal
from mysite.api.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from typing import List

ingredient_router = APIRouter(prefix='/ingredient', tags=['Ingredient'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@ingredient_router.post('/', response_model=IngredientOutSchema)
async def create_ingredient(ingredient: IngredientInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    ingredient_db = db.query(Ingredient).filter(Ingredient.name == ingredient.name).first()
    if ingredient_db:
        raise HTTPException(status_code=400, detail='Мындай ингредиент бар')
    ingredient_db = Ingredient(**ingredient.model_dump())
    db.add(ingredient_db)
    db.commit()
    db.refresh(ingredient_db)
    return ingredient_db


@ingredient_router.get('/', response_model=List[IngredientOutSchema])
async def list_ingredient(db: Session = Depends(get_db)):
    return db.query(Ingredient).all()


@ingredient_router.get('/{ingredient_id}/', response_model=IngredientOutSchema)
async def detail_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail='Мындай ингредиент жок')
    return ingredient


@ingredient_router.put('/{ingredient_id}/', response_model=dict)
async def update_ingredient(ingredient_id: int, ingredient: IngredientInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    ingredient_db = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient_db:
        raise HTTPException(status_code=404, detail='Мындай ингредиент жок')
    existing_ingredient = db.query(Ingredient).filter(Ingredient.name == ingredient.name, Ingredient.id != ingredient_id).first()
    if existing_ingredient:
        raise HTTPException(status_code=400, detail='Мындай ингредиент бар')
    for ingredient_key, ingredient_value in ingredient.model_dump().items():
        setattr(ingredient_db, ingredient_key, ingredient_value)
    db.commit()
    db.refresh(ingredient_db)
    return {'message': 'Ингредиент озгорулду'}


@ingredient_router.delete('/{ingredient_id}/', response_model=dict)
async def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    ingredient_db = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient_db:
        raise HTTPException(status_code=404, detail='Мындай ингредиент жок')
    db.delete(ingredient_db)
    db.commit()
    return {'message': 'Ингредиент удалить болду'}
