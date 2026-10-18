from fastapi import FastAPI
from mysite.api import auth, user, category, recipe, ingredient, recipe_ingredient, favorite, agent
from mysite.database.db import Base, engine
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI(title='SmartRecipe AI')

app.include_router(auth.auth_router)
app.include_router(user.user_router)
app.include_router(category.category_router)
app.include_router(recipe.recipe_router)
app.include_router(ingredient.ingredient_router)
app.include_router(recipe_ingredient.recipe_ingredient_router)
app.include_router(favorite.favorite_router)
app.include_router(agent.agent_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8005, reload=True)
