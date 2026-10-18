from fastapi import APIRouter, HTTPException, Depends
from mysite.api.auth import pwd_context
from mysite.database.models import UserProfile
from mysite.database.schema import UserProfileInputSchema, UserProfileOutSchema
from mysite.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List

user_router = APIRouter(prefix='/user', tags=['UserProfile'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@user_router.get('/', response_model=List[UserProfileOutSchema])
async def list_user(db: Session = Depends(get_db)):
    return db.query(UserProfile).all()

@user_router.get('/{user_id}/', response_model=UserProfileOutSchema)
async def detail_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail='Мындай колдонуучу жок')
    return user_db


@user_router.put('/{user_id}/')
async def update_user(user_id:int,user:UserProfileInputSchema,db:Session=Depends(get_db)):
    user_db=db.query(UserProfile).filter(UserProfile.id==user_id).first()
    if not user_db:
        raise HTTPException(status_code=404,detail='Мындай колдонуучу жок')
    username_db=db.query(UserProfile).filter(UserProfile.username==user.username,UserProfile.id!=user_id).first()
    email_db=None
    if user.email:
        email_db=db.query(UserProfile).filter(UserProfile.email==user.email,UserProfile.id!=user_id).first()
    if username_db or email_db:
        raise HTTPException(status_code=400,detail='Мындай username же email бар')
    user_data=user.model_dump()
    user_data['password']=pwd_context.hash(user.password)
    for key,value in user_data.items():
        setattr(user_db,key,value)
    db.commit()
    return {"message":"Успешно изменено"}

@user_router.delete('/{user_id}/')
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail='Мындай колдонуучу жок')
    db.delete(user_db)
    db.commit()
    return {'message': 'Колдонуучу өчүрүлдү'}
