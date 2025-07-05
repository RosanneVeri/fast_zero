from http import HTTPStatus

from sqlalchemy import select

from fast_zero.models import User
from fast_zero.schemas import UserPublic


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    # Arrange (Organização)
    response = client.get('/')  # Act (ação)
    assert response.status_code == HTTPStatus.OK  # Assert (confirmação)
    assert response.json() == {'message': 'Olá mundo!'}


def test_read_html_retornar_html_e_ola_mundo(client):
    response = client.get('/html/')
    # print(dir(response))
    assert response.status_code == HTTPStatus.OK
    assert (
        response.text
        == """

    <html>
    <head>
   <title>Olá mundo!</title>
    <head>
    <body>
    <h1>Olá mundo</h1>
    <body>
    <html>"""
    )


def teste_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@exemplo.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': 'alice@exemplo.com',
        'username': 'alice',
    }


def test_get_users(client, token, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Maria',
            'email': 'maria@gmail.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Maria',
        'email': 'maria@gmail.com',
        'id': 1,
    }


def test_delete_user(client, user, token):
    response = client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_update_integrity_error(client, user, token):
    # inserindo fausto
    client.post(
        '/users',
        json={
            'username': 'fausto',
            'email': 'fausto@exemple.com',
            'password': 'secret',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@exemple.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT


def test_create_user_duplicate_username(client, user, token):
    response = client.post(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': user.username,
            'email': 'test@test.com',
            'password': 'secret',
        },
    )
    print(response.json())
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_duplicate_email(client, user, token):
    response = client.post(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'newuser',
            'email': user.email,
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_token_sem_email(client, token_sem_email):
    response = client.post('/token', headers={token_sem_email})
    print(response)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_get_user_persistence(client, session, token):
    new_user = User(username='persist', email='persist@test.com', password='secret')
    session.add(new_user)
    session.commit()
    response = client.get(f'/users/{new_user.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': new_user.id,
        'username': 'persist',
        'email': 'persist@test.com',
    }


def test_get_token(client, user):
    response = client.post('/token', data={'username': user.email, 'password': user.clean_password})

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token


def test_delete_user_not_found(client, session):
    user_to_delete = session.scalar(select(User).where(User.id == 1))
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()

    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user_not_found(client, session):
    # Limpa o usuário com id=1 antes do teste, se existir
    user_to_delete = session.scalar(select(User).where(User.id == 1))
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()

    response = client.put(
        '/users/1',
        json={
            'username': 'Maria',
            'email': 'maria@gmail.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}

    def test_get_user_not_found(client, session):
        user_to_delete = session.scalar(select(User).where(User.id == 1))
        if user_to_delete:
            session.delete(user_to_delete)
            session.commit()

    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user(client, user):
    response = client.get(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.OK
    print(response.json())
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }
