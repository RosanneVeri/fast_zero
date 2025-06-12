from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

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
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)

    database.append(user_with_id)
    return user_with_id


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users():
    return {'users': database}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=user_id)
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Deu ruim! Não achei!'
        )
    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado'
        )
    return database.pop(user_id - 1)


@app.get('/users/{id}', response_model=UserPublic)
def get_user(
    id: int,
):
    for user in database:
        print(user.id)
        if int(user.id) == id:
            return user
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado'
    )
