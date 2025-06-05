from http import HTTPStatus


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


def test_get_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'email': 'alice@exemplo.com',
                'username': 'alice',
            },
        ]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'Mario',
            'email': 'mario@example.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Mario',
        'email': 'mario@example.com',
        'id': 1,
    }


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Mario',
        'email': 'mario@example.com',
        'id': 1,
    }
