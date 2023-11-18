from httpx import AsyncClient
import pytest

from src.auth.hashing import Hasher



password = "testUSER1234"
hashed_password = Hasher.get_password_hash(password)
user_data = {
    "login": "test_user_login",
    "name": "testusername",
    "email": "testuser@email.com",
    "password": password
}


@pytest.mark.asyncio
async def test_auth_by_email(client: AsyncClient, create_user):
    db_data = user_data.copy()
    db_data["password"] = hashed_password
    await create_user(db_data)
    auth_data = {
        'username': user_data['email'],
        'password': user_data['password']
    }
    response = await client.post(
        url="/authentication",
        data=auth_data
    )
    assert response.status_code == 200
    assert tuple(response.json().keys()) == ("access_token", "token_type", "refresh_token")


@pytest.mark.asyncio
async def test_auth_by_login(client: AsyncClient, create_user):
    db_data = user_data.copy()
    db_data["password"] = hashed_password
    await create_user(db_data)
    auth_data = {
        'username': user_data['login'],
        'password': user_data['password']
    }
    response = await client.post(
        url="/authentication",
        data=auth_data
    )
    assert response.status_code == 200
    assert tuple(response.json().keys()) == ("access_token", "token_type", "refresh_token")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "form, status_code, body",
    [
        (
            {
                'password': password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "username"],
                    "msg": "Field required"
                }
            }
        ),
        (
            {
                'username': 'testusemacom',
                'password': password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                'username': 'testuser@emailcom',
                'password': password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                'username': 'testuseremail.com',
                'password': password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                'username': '12312321@123124124.12424',
                'password': password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                'username': '',
                'password': password
            },
            422,
            {
                "detail": {
                    'loc': ['body', 'username'],
                    'msg': 'Field required'
                }
            }
        ),
        (
            {
                'username': '@email.com',
                'password': password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                'username': 'asdasas@.com',
                'password': password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                'username': 'asdasas@email.',
                'password': password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
    ]   
)
async def test_auth_invalid_email(client: AsyncClient, create_user,
                                  form, status_code, body):
    db_data = user_data.copy()
    db_data["password"] = hashed_password
    await create_user(db_data)
    response = await client.post(
        url="/authentication",
        data=form
    )
    assert response.status_code == status_code
    assert response.json() == body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "form, status_code, body",
    [
        (
            {
                "username": "",
                "password": password
            },
            422,
            {
                "detail": {
                    'loc': ['body', 'username'],
                    'msg': 'Field required'
                }
            }
        ),
        (
            {
                "password": password
            },
            422,
            {
                "detail": {
                    'loc': ['body', 'username'],
                    'msg': 'Field required'
                }
            }
        ),
        (
            {
                "username": 121321,
                "password": password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                "username": "1",
                "password": password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                "username": "dasda@ada.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                "username": "sdsdasasdasfdsfksdvjlkdfjldasdddddddddddddddfefrfsdsdcdsvlfdkvlkfkfvdasddshjds",
                "password": password
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
    ]   
)
async def test_invalid_login(client: AsyncClient, create_user,
                             form, status_code, body):
    db_data = user_data.copy()
    db_data["password"] = hashed_password
    await create_user(db_data)
    response = await client.post(
        url="/authentication",
        data=form
    )
    assert response.status_code == 422
    assert response.status_code == status_code
    assert response.json() == body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "form, status_code, body",
    [
        (
            {
                'username': 'testuser@email.com',
            },
            422,
            {
                "detail": {
                    'loc': ['body', 'password'],
                    'msg': 'Field required'
                }
            }
        ),
        (
            {
                'username': 'testuser@email.com',
                'password': ''
            },
            422,
            {
                "detail": {
                    'loc': ['body', 'password'],
                    'msg': 'Field required'
                }
            }
        ),
        (
            {
                'username': 'testuser@email.com',
                'password': 'testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234testUSER1234'
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
        (
            {
                'username': 'testuser@email.com',
                'password': 324213412312312432432
            },
            422,
            {
                "detail": {
                    "msg": "Incorrect username or password"
                }
            }
        ),
    ]   
)
async def test_invalid_password(client: AsyncClient, create_user,
                            form, status_code, body):
    db_data = user_data.copy()
    db_data["password"] = hashed_password
    await create_user(db_data)
    response = await client.post(
        url="/authentication",
        data=form
    )
    assert response.status_code == 422
    assert response.status_code == status_code
    assert response.json() == body
