from fastapi import APIRouter, Form, HTTPException
from . import auth, db_models
from fastapi import Depends
router = APIRouter()

@router.post('/token')
def login_for_access_token(username: str = Form(...), password: str = Form(...)):
    user = db_models.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    if not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    token = auth.create_access_token({'sub': username})
    return {'access_token': token, 'token_type': 'bearer'}

@router.post('/signup')
def signup(payload: dict):
    u = payload.get('username'); p = payload.get('password')
    if not u or not p: raise HTTPException(status_code=400, detail='Missing')
    existing = db_models.get_user_by_username(u)
    if existing: raise HTTPException(status_code=400, detail='Exists')
    db_models.create_user(u,p)
    return {'ok': True}
