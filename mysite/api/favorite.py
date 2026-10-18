from mysite.database.models import FavoriteRecipe, Recipe, UserProfile
from mysite.database.schema import FavoriteRecipeInputSchema, FavoriteRecipeOutSchema
from mysite.database.db import SessionLocal
from mysite.api.auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Depends
from typing import List

favorite_router = APIRouter(prefix='/favorite', tags=['FavoriteRecipe'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@favorite_router.post('/', response_model=FavoriteRecipeOutSchema)
async def create_favorite(favorite: FavoriteRecipeInputSchema, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    recipe_db = db.query(Recipe).filter(Recipe.id == favorite.recipe_id).first()
    if not recipe_db:
        raise HTTPException(status_code=404, detail='Мындай рецепт жок')
    favorite_db = db.query(FavoriteRecipe).filter(FavoriteRecipe.user_id == current_user.id, FavoriteRecipe.recipe_id == favorite.recipe_id).first()
    if favorite_db:
        raise HTTPException(status_code=400, detail='Этот рецепт уже есть в избранном')
    favorite_db = FavoriteRecipe(user_id=current_user.id, recipe_id=favorite.recipe_id)
    db.add(favorite_db)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Этот рецепт уже есть в избранном')
    db.refresh(favorite_db)
    return favorite_db


@favorite_router.get('/', response_model=List[FavoriteRecipeOutSchema])
async def list_favorite(db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    return db.query(FavoriteRecipe).filter(FavoriteRecipe.user_id == current_user.id).all()


@favorite_router.delete('/{recipe_id}/', response_model=dict)
async def delete_favorite(recipe_id: int, db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    favorite_db = db.query(FavoriteRecipe).filter(FavoriteRecipe.recipe_id == recipe_id, FavoriteRecipe.user_id == current_user.id).first()
    if not favorite_db:
        raise HTTPException(status_code=404, detail='Рецепт не найден в вашем избранном')
    db.delete(favorite_db)
    db.commit()
    return {'message': 'Рецепт удалён из избранного'}
