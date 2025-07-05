from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from jwt import decode, encode
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    table_registry.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_overrise():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_overrise
        yield client
    app.dependency_overrides.clear()


@contextmanager
def _datetime_fake_vindo_banco(*, model, time=datetime(2025, 6, 11)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at') and hasattr(target, 'updated_at'):
            target.created_at = time
            target.updated_at = time
            print(f'Inserting: {target}, created_at{target.created_at}, updated_at={target.updated_at}')

    # Registrar evento
    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    # Remover evento
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def datetime_fake_vindo_banco():
    return _datetime_fake_vindo_banco


@pytest.fixture
def user(session: Session):
    password = 'secret'
    user = User(username='Teste', email='test@test.com', password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post('/token', data={'username': user.email, 'password': user.clean_password})
    return response.json()['access_token']


@pytest.fixture
def other_user(session: Session):
    password = 'other_secret'
    user = User(
        username='OtherUser',
        email='other@test.com',
        password=get_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = password
    return user


@pytest.fixture
def other_token(client, other_user):
    response = client.post('/token', data={'username': other_user.email, 'password': other_user.clean_password})
    assert response.status_code == HTTPStatus.OK, f'Failed to get other token: {response.json()}'
    print(f'Other token: {response.json()["access_token"]}')  # Debug
    return response.json()['access_token']


@pytest.fixture
def token_sem_email(token):
    user = decode(token)
    user.username = None
    novo_token = encode(user)

    return novo_token
