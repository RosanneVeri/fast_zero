from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, datatime_fake_vindo_banco):
    with datatime_fake_vindo_banco(model=User) as time:
        new_user = User(username='test', email='test@test', password='secret')
        session.add(new_user)
        session.commit()
        user = session.scalar(select(User).where(User.username == 'test'))
    assert asdict(user) == {
        id: 1,
        'username': 'test',
        'email': 'test@test',
        'password': 'secret',
        'created_at': time,
    }
