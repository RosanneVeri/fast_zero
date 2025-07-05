from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    JWToken,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fast_zero.security import create_access_token, get_current_user, get_password_hash, verify_password

database = [
    # UserPublic(id=1, username='Maria', email='maria@gmail.com'),
    # UserPublic(id=2, username='Alice', email='maria@gmail.com'),
    # UserPublic(id=3, username='Robert', email='maria@gmail.com'),
    # UserPublic(id=4, username='João', email='maria@gmail.com'),
    # UserPublic(id=5, username='Felipe', email='maria@gmail.com'),
]

app = FastAPI(title='Minha API TOP')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}


@app.get('/html/', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_html():
    return """

    <html>
    <head>
   <title>Olá mundo!</title>
    <head>
    <body>
    <h1>Olá mundo</h1>
    <body>
    <html>"""


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    user_db = session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))
    if user_db:
        if user_db.username == user.username:
            raise HTTPException(
                detail='Username already exists',
                status_code=HTTPStatus.CONFLICT,
            )
        elif user_db.email == user.email:
            raise HTTPException(detail='Email already exists', status_code=HTTPStatus.CONFLICT)

    user_db = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(limit: int = 10, offset: int = 0, session: Session = Depends(get_session), current_user=Depends(get_current_user)):
    users_db = session.scalars(select(User).limit(limit).offset(offset))

    return {'users': users_db}


@app.put('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    try:
        # validação
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists',
            status_code=HTTPStatus.CONFLICT,
        )


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')
    session.delete(user)
    session.commit()
    return {'message': 'User deleted'}


@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if user_db is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado')

    return user_db


@app.post('/token', response_model=JWToken)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect email or password')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Incorrect email or password')

    access_token = create_access_token({'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}
