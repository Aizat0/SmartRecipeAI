from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserProfileInputSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    age: int
    phone_number: str


class UserProfileLoginSchema(BaseModel):
    username: str
    password: str


class UserProfileOutSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    age: int
    phone_number: str
    created_at: datetime
    updated_at: datetime
    model_config = {'from_attributes': True}


class CategoryInputSchema(BaseModel):
    category_name: str


class CategoryOutSchema(BaseModel):
    id: int
    category_name: str
    model_config = {'from_attributes': True}


class RecipeInputSchema(BaseModel):
    title: str
    description: str
    instructions: str
    cooking_time: int
    servings: int
    category_id: int


class RecipeOutSchema(BaseModel):
    id: int
    title: str
    description: str
    instructions: str
    cooking_time: int
    servings: int
    created_at: datetime
    updated_at: datetime
    category_id: int
    user_id: int
    model_config = {'from_attributes': True}


class IngredientInputSchema(BaseModel):
    name: str


class IngredientOutSchema(BaseModel):
    id: int
    name: str
    model_config = {'from_attributes': True}


class RecipeIngredientInputSchema(BaseModel):
    recipe_id: int
    ingredient_id: int
    quantity: float
    unit: str


class RecipeIngredientOutSchema(BaseModel):
    id: int
    recipe_id: int
    ingredient_id: int
    quantity: float
    unit: str
    model_config = {'from_attributes': True}


class FavoriteRecipeInputSchema(BaseModel):
    recipe_id: int


class FavoriteRecipeOutSchema(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    created_at: datetime
    model_config = {'from_attributes': True}


class CurrentUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
