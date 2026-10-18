from mysite.database.models import RecipeIngredient, Recipe, Ingredient, UserProfile
from mysite.database.schema import RecipeIngredientInputSchema, RecipeIngredientOutSchema
from mysite.database.db import SessionLocal
from mysite.api.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from typing import List

recipe_ingredient_router = APIRouter(prefix='/recipe-ingredient', tags=['RecipeIngredient'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@recipe_ingredient_router.post('/', response_model=RecipeIngredientOutSchema)
async def create_recipe_ingredient(recipe_ingredient: RecipeIngredientInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    recipe_db = db.query(Recipe).filter(Recipe.id == recipe_ingredient.recipe_id).first()
    if not recipe_db:
        raise HTTPException(status_code=404, detail='Мындай рецепт жок')
    if recipe_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Добавлять ингредиенты может только автор рецепта')
    ingredient_db = db.query(Ingredient).filter(Ingredient.id == recipe_ingredient.ingredient_id).first()
    if not ingredient_db:
        raise HTTPException(status_code=404, detail='Мындай ингредиент жок')
    if recipe_ingredient.quantity <= 0:
        raise HTTPException(status_code=400, detail='Количество должно быть больше нуля')
    if not recipe_ingredient.unit.strip():
        raise HTTPException(status_code=400, detail='Укажите единицу измерения')
    existing_ingredient = db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_ingredient.recipe_id, RecipeIngredient.ingredient_id == recipe_ingredient.ingredient_id).first()
    if existing_ingredient:
        raise HTTPException(status_code=400, detail='Этот ингредиент уже добавлен в рецепт')
    recipe_ingredient_db = RecipeIngredient(**recipe_ingredient.model_dump())
    recipe_ingredient_db.unit = recipe_ingredient.unit.strip()
    db.add(recipe_ingredient_db)
    db.commit()
    db.refresh(recipe_ingredient_db)
    return recipe_ingredient_db


@recipe_ingredient_router.get('/recipe/{recipe_id}/', response_model=List[RecipeIngredientOutSchema])
async def list_recipe_ingredient(recipe_id: int, db: Session = Depends(get_db)):
    recipe_db = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe_db:
        raise HTTPException(status_code=404, detail='Мындай рецепт жок')
    return db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_id).all()


@recipe_ingredient_router.put('/{recipe_ingredient_id}/', response_model=dict)
async def update_recipe_ingredient(recipe_ingredient_id: int, recipe_ingredient: RecipeIngredientInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    recipe_ingredient_db = db.query(RecipeIngredient).filter(RecipeIngredient.id == recipe_ingredient_id).first()
    if not recipe_ingredient_db:
        raise HTTPException(status_code=404, detail='Мындай маалымат жок')
    recipe_db = db.query(Recipe).filter(Recipe.id == recipe_ingredient_db.recipe_id).first()
    if recipe_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Изменить ингредиент может только автор рецепта')
    if recipe_ingredient.recipe_id != recipe_ingredient_db.recipe_id:
        raise HTTPException(status_code=400, detail='Нельзя изменить рецепт для этой записи')
    ingredient_db = db.query(Ingredient).filter(Ingredient.id == recipe_ingredient.ingredient_id).first()
    if not ingredient_db:
        raise HTTPException(status_code=404, detail='Мындай ингредиент жок')
    if recipe_ingredient.quantity <= 0:
        raise HTTPException(status_code=400, detail='Количество должно быть больше нуля')
    if not recipe_ingredient.unit.strip():
        raise HTTPException(status_code=400, detail='Укажите единицу измерения')
    existing_ingredient = db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_ingredient.recipe_id, RecipeIngredient.ingredient_id == recipe_ingredient.ingredient_id, RecipeIngredient.id != recipe_ingredient_id).first()
    if existing_ingredient:
        raise HTTPException(status_code=400, detail='Этот ингредиент уже есть в рецепте')
    for ingredient_key, ingredient_value in recipe_ingredient.model_dump().items():
        setattr(recipe_ingredient_db, ingredient_key, ingredient_value)
    recipe_ingredient_db.unit = recipe_ingredient.unit.strip()
    db.commit()
    db.refresh(recipe_ingredient_db)
    return {'message': 'Ингредиент рецепта озгорулду'}


@recipe_ingredient_router.delete('/{recipe_ingredient_id}/', response_model=dict)
async def delete_recipe_ingredient(recipe_ingredient_id: int, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    recipe_ingredient_db = db.query(RecipeIngredient).filter(RecipeIngredient.id == recipe_ingredient_id).first()
    if not recipe_ingredient_db:
        raise HTTPException(status_code=404, detail='Мындай маалымат жок')
    recipe_db = db.query(Recipe).filter(Recipe.id == recipe_ingredient_db.recipe_id).first()
    if recipe_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Удалить ингредиент может только автор рецепта')
    db.delete(recipe_ingredient_db)
    db.commit()
    return {'message': 'Ингредиент рецепта удалён'}
