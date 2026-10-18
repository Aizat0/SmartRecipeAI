from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from typing import Optional
from mysite.database.db import SessionLocal
from mysite.database.models import UserProfile, RefreshToken
from mysite.database.schema import UserProfileInputSchema, UserProfileOutSchema, CurrentUserSchema
from mysite.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login/')
auth_router = APIRouter(prefix='/auth', tags=['Auth'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'access':
            raise HTTPException(status_code=401, detail='Access token туура эмес')
        user_id = int(payload.get('sub'))
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Access token мөөнөтү бүттү')
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail='Access token туура эмес')
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=401, detail='Мындай колдонуучу базада жок')
    return user_db

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_LIFETIME))
    to_encode.update({'exp': expire, 'type': 'access'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_LIFETIME)
    to_encode.update({'exp': expire, 'type': 'refresh'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@auth_router.post('/register/', response_model=dict)
async def register(user: UserProfileInputSchema, db: Session = Depends(get_db)):
    username_db = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    email_db = db.query(UserProfile).filter(UserProfile.email == user.email).first()
    if username_db or email_db:
        raise HTTPException(status_code=400, detail='Мындай username же почта бар')
    user_data = UserProfile(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        age=user.age,
        phone_number=user.phone_number,
        password=get_password_hash(user.password)
    )
    db.add(user_data)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail='Мындай username же почта бар')
    db.refresh(user_data)
    return {'message': 'Сиз регистрация болдуңуз'}

def get_token_data(user: UserProfile):
    return {'sub': str(user.id), 'username': user.username}

@auth_router.post('/login/', response_model=dict)
async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(status_code=401, detail='Сиз жазган маалымат туура эмес')
    token_data = get_token_data(user_db)
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    token_db = RefreshToken(user_id=user_db.id, token=refresh_token)
    db.add(token_db)
    db.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@auth_router.post('/logout/', response_model=dict)
async def logout(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Refresh token туура эмес')
    db.delete(stored_token)
    db.commit()
    return {'message': 'Системадан чыктыңыз'}

@auth_router.post('/refresh/', response_model=dict)
async def refresh(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Refresh token туура эмес')
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'refresh':
            raise HTTPException(status_code=401, detail='Refresh token туура эмес')
        user_id = int(payload.get('sub'))
    except ExpiredSignatureError:
        db.delete(stored_token)
        db.commit()
        raise HTTPException(status_code=401, detail='Refresh token мөөнөтү бүттү')
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail='Refresh token туура эмес')
    if stored_token.user_id != user_id:
        raise HTTPException(status_code=401, detail='Refresh token колдонуучуга туура келбейт')
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(status_code=401, detail='Мындай колдонуучу базада жок')
    return {
        'access_token': create_access_token(get_token_data(user_db)),
        'token_type': 'bearer'
    }

@auth_router.get('/verify/', response_model=CurrentUserSchema)
async def verify_access_token(current_user: UserProfile = Depends(get_current_user)):
    return current_user

@auth_router.get('/me/', response_model=UserProfileOutSchema)
async def user_me(profile: UserProfile = Depends(get_current_user)):
    return profile
