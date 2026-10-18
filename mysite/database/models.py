from .db import Base
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime

class UserProfile(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    age: Mapped[int] = mapped_column(Integer)
    phone_number: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_token: Mapped[List['RefreshToken']] = relationship(back_populates='token_user',
                                                            cascade='all, delete-orphan')
    recipes: Mapped[List['Recipe']] = relationship(back_populates='user',
                                                   cascade='all, delete-orphan')
    favorites: Mapped[List['FavoriteRecipe']] = relationship(back_populates='user',
                                                              cascade='all, delete-orphan')


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    token_user: Mapped[UserProfile] = relationship(UserProfile, back_populates='user_token')
    token: Mapped[str] = mapped_column(String)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(150), unique=True)
    recipes: Mapped[List['Recipe']] = relationship(back_populates='category')


class Recipe(Base):
    __tablename__ = 'recipe'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    instructions: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    servings: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    category: Mapped[Category] = relationship(Category, back_populates='recipes')
    user: Mapped[UserProfile] = relationship(UserProfile, back_populates='recipes')
    ingredients: Mapped[List['RecipeIngredient']] = relationship(back_populates='recipe',
                                                                  cascade='all, delete-orphan')
    favorites: Mapped[List['FavoriteRecipe']] = relationship(back_populates='recipe',
                                                              cascade='all, delete-orphan')


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    recipes: Mapped[List['RecipeIngredient']] = relationship(back_populates='ingredient',
                                                              cascade='all, delete-orphan')


class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredient'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipe.id'))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredient.id'))
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    recipe: Mapped[Recipe] = relationship(Recipe, back_populates='ingredients')
    ingredient: Mapped[Ingredient] = relationship(Ingredient, back_populates='recipes')


class FavoriteRecipe(Base):
    __tablename__ = 'favorite_recipe'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipe.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped[UserProfile] = relationship(UserProfile, back_populates='favorites')
    recipe: Mapped[Recipe] = relationship(Recipe, back_populates='favorites')
