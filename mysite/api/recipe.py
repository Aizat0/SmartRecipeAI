from mysite.database.models import Recipe, Category, UserProfile
from mysite.database.schema import RecipeInputSchema, RecipeOutSchema
from mysite.database.db import SessionLocal
from mysite.api.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from typing import List

recipe_router = APIRouter(prefix='/recipe', tags=['Recipe'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@recipe_router.post('/', response_model=RecipeOutSchema)
async def create_recipe(recipe: RecipeInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    category_db = db.query(Category).filter(Category.id == recipe.category_id).first()
    if not category_db:
        raise HTTPException(status_code=404, detail='Мындай категория жок')
    recipe_db = Recipe(**recipe.model_dump(), user_id=current_user.id)
    db.add(recipe_db)
    db.commit()
    db.refresh(recipe_db)
    return recipe_db


@recipe_router.get('/', response_model=List[RecipeOutSchema])
async def list_recipe(db: Session = Depends(get_db)):
    return db.query(Recipe).all()


@recipe_router.get('/{recipe_id}/', response_model=RecipeOutSchema)
async def detail_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail='Мындай рецепт жок')
    return recipe


@recipe_router.put('/{recipe_id}/', response_model=dict)
async def update_recipe(recipe_id: int, recipe: RecipeInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    recipe_db = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe_db:
        raise HTTPException(status_code=404, detail='Мындай рецепт жок')
    if recipe_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Изменить рецепт может только его автор')
    category_db = db.query(Category).filter(Category.id == recipe.category_id).first()
    if not category_db:
        raise HTTPException(status_code=404, detail='Мындай категория жок')
    for recipe_key, recipe_value in recipe.model_dump().items():
        setattr(recipe_db, recipe_key, recipe_value)
    db.commit()
    db.refresh(recipe_db)
    return {'message': 'Рецепт озгорулду'}


@recipe_router.delete('/{recipe_id}/', response_model=dict)
async def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    recipe_db = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe_db:
        raise HTTPException(status_code=404, detail='Мындай рецепт жок')
    if recipe_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Удалить рецепт может только его автор')
    db.delete(recipe_db)
    db.commit()
    return {'message': 'Рецепт удалить болду'}
