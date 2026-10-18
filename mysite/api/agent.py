import json
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from mysite.database.db import SessionLocal
from mysite.database.models import UserProfile, Recipe, FavoriteRecipe
from mysite.api.auth import get_current_user
from mysite.chain.chain_ai import model, search_answer

agent_router = APIRouter(prefix='/agent', tags=['Agent'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@agent_router.post('/chat/')
async def chat(data: dict = Body(...), db: Session = Depends(get_db), current_user: UserProfile = Depends(get_current_user)):
    message = data.get('message')
    if not isinstance(message, str) or not message.strip() or len(message) > 2000:
        raise HTTPException(status_code=422, detail='Некорректный message')

    message = message.strip()
    message_lower = message.lower()

    @tool
    def search_recipe(title: str = '') -> list[dict]:
        """Найти рецепты в SQLite по названию. Пустое название означает все рецепты."""
        recipes = db.query(Recipe)
        if title:
            recipes = recipes.filter(Recipe.title.ilike(f'%{title}%'))
        return [
            {
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'instructions': recipe.instructions,
                'cooking_time': recipe.cooking_time,
                'servings': recipe.servings
            }
            for recipe in recipes.limit(20).all()
        ]

    @tool
    def add_favorite(recipe_id: int) -> dict:
        """Добавить существующий рецепт из SQLite в избранное пользователя по его числовому ID."""
        recipe_db = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe_db:
            return {'message': 'Рецепт не найден'}
        favorite_db = db.query(FavoriteRecipe).filter(FavoriteRecipe.user_id == current_user.id,FavoriteRecipe.recipe_id == recipe_id).first()
        if favorite_db:
            return {'message': 'Рецепт уже находится в избранном'}
        favorite_db = FavoriteRecipe(
            user_id=current_user.id,
            recipe_id=recipe_id
        )
        db.add(favorite_db)
        db.commit()
        return {'message': 'Рецепт добавлен в избранное'}

    try:
        if 'избранн' not in message_lower and 'баз' not in message_lower and 'sqlite' not in message_lower:
            return {'answer': search_answer(message)}
        tools = [search_recipe, add_favorite]
        tools_dict = {item.name: item for item in tools}
        favorite_request = (
            'избранн' in message_lower
            and ('добав' in message_lower or 'сохрани' in message_lower)
        )

        if favorite_request:
            tools = [add_favorite]
        else:
            tools = [search_recipe]
        messages = [
            SystemMessage(content=(
                'Ты помощник SmartRecipe AI. '
                'Отвечай кратко на русском языке. '
                'Для поиска рецептов в SQLite используй search_recipe. '
                'Для добавления в избранное используй add_favorite. '
                'Передавай recipe_id как целое число. '
                'Не придумывай ID рецептов. '
                'Не выполняй действия, которые пользователь не запрашивал.'
            )),
            HumanMessage(content=message)
        ]
        response = await model.bind_tools(tools).ainvoke(messages)
        if response.invalid_tool_calls:
            return {'answer': 'Не удалось распознать действие'}
        if not response.tool_calls:
            return {'answer': response.content or 'Уточните запрос'}
        if len(response.tool_calls) != 1:
            return {'answer': 'Отправьте одно действие за запрос'}
        call = response.tool_calls[0]
        if call['name'] not in [item.name for item in tools]:
            return {'answer': 'Такое действие недоступно'}
        if call['name'] == 'add_favorite':
            recipe_id = call['args'].get('recipe_id')
            if not isinstance(recipe_id, int) or isinstance(recipe_id, bool):
                return {'answer': 'Укажите числовой ID рецепта'}
        result = await tools_dict[call['name']].ainvoke(call['args'])
        if call['name'] == 'add_favorite':
            return {'answer': result['message']}
        return {'answer': json.dumps(result, ensure_ascii=False)}
    except ValidationError:
        db.rollback()
        return {'answer': 'AI неправильно передал параметры инструмента'}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Конфликт данных в базе')
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        print('ОШИБКА АГЕНТА:', type(exc).__name__, str(exc))
        raise HTTPException(status_code=503, detail='Ошибка агента') from exc
