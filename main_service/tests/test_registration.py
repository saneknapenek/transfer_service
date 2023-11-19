from json import dumps

from httpx import AsyncClient, Response
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
async def test_reg(client: AsyncClient, get_user_by_id):
    response = await client.post(
        url="/registration",
        content=dumps(user_data)
    )
    assert response.status_code == 200
    resp_data = response.json()
    db_user = await get_user_by_id(resp_data["id"])
    assert db_user.login == user_data["login"] == resp_data["login"]
    assert db_user.email == user_data["email"] == resp_data["email"]
    assert db_user.name == user_data["name"] == resp_data["name"]
    assert Hasher.verify_password(password, db_user.password)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, data_db, body",
    [
        (
            {
                "login": "test_user_login",
                "name": "testusedasdrname",
                "email": "testusdasdaer@email.com",
                "password": password
            },
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "testuser@email.com",
                "password": password
            },
            {
                "detail": {
                    "msg": "A user with the same username or email already exists"
                }
            }
        ),
        (
            {
                "login": "test_udasasdser_login",
                "name": "testusersdadname",
                "email": "testuser@email.com",
                "password": password
            },
            {
                "login": "test_usdsjer_login",
                "name": "testudsksername",
                "email": "testuser@email.com",
                "password": password
            },
            {
                "detail": {
                    "msg": "A user with the same username or email already exists"
                }
            }
        ),
    ]   
)
async def test_already_exist(client: AsyncClient,
                             params, data_db, body,
                             create_user):
    data_db["password"] = hashed_password
    await create_user(data_db)
    response = await client.post(
        url="/registration",
        content=dumps(params)
    )
    assert response.status_code == 409
    resp_data = response.json()
    assert resp_data == body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, status_code, body",
    [
        (
            {
                "login": "",
                "name": "testusername",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "login"],
                    "msg": "String should have at least 2 characters"
                }
            }
        ),
        (
            {
                "name": "testusername",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "login"],
                    "msg": "Field required"
                }
            }
        ),
        (
            {
                "login": 121321,
                "name": "testusername",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "login"],
                    "msg": "Input should be a valid string"
                }
            }
        ),
        (
            {
                "login": "1",
                "name": "testusername",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "login"],
                    "msg": "String should have at least 2 characters"
                }
            }
        ),
        (
            {
                "login": "dasda@ada.com",
                "name": "testusername",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "login"],
                    "msg": "Login must contain only latin letters, numbers, and underscores"
                }
            }
        ),
        (
            {
                "login": "sdsdasasdasfdsfksdvjlkdfjldasdddddddddddddddfefrfsdsdcdsvlfdkvlkfkfvdasddshjds",
                "name": "testusername",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "login"],
                    "msg": "String should have at most 50 characters"
                }
            }
        ),
    ]   
)
async def test_invalid_login(client: AsyncClient,
                             params, status_code, body, get_user_by_email):
    response: Response = await client.post(
        url="/registration",
        content=dumps(params)
    )
    assert response.status_code == status_code
    assert response.json() == body
    user_from_db = await get_user_by_email(params["email"])
    assert user_from_db is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, status_code, body",
    [
        (
            {
                "login": "test_user_login",
                "name": "",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "name"],
                    "msg": "String should have at least 2 characters"
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "name"],
                    "msg": "Field required"
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": 234792594,
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "name"],
                    "msg": "Input should be a valid string"
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "47238472837",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "name"],
                    "msg": "Name should contains only letters"
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusernamefsdfjdjsjfdsssssssssssssssssssssssfadfafdvfvddsksdlfdslfdfs",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "name"],
                    "msg": "String should have at most 50 characters"
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "sdfds.askd",
                "email": "testuser@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "name"],
                    "msg": "Name should contains only letters"
                }
            }
        ),
    ]   
)
async def test_invalid_name(client: AsyncClient,
                            params, status_code, body):
    response: Response = await client.post(
        url="/registration",
        content=dumps(params)
    )
    assert response.status_code == status_code
    assert response.json() == body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, status_code, body",
    [
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "Field required"
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "testusemacom",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "testuser@emailcom",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: The part after the @-sign is not valid. It should have a period."
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "testuseremail.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "12312321@123124124.12424",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: The part after the @-sign is not valid. It is not within a valid top-level domain."
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "@email.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: There must be something before the @-sign."
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "asdasas@.com",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: An email address cannot have a period immediately after the @-sign."
                }
            }
        ),
        (
            {
                "login": "test_user_login",
                "name": "testusername",
                "email": "asdasas@email.",
                "password": password
            },
            422,
            {
                "detail": {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address: An email address cannot end with a period."
                }
            }
        ),
    ]   
)
async def test_invalid_email(client: AsyncClient,
                             params, status_code, body, get_user_by_login):
    response: Response = await client.post(
        url="/registration",
        content=dumps(params)
    )
    assert response.status_code == status_code
    assert response.json() == body
    user_from_db = await get_user_by_login(params["login"])
    assert user_from_db is None

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
                'detail': {
                    'loc': ['body', 'password'], 
                    'msg': 'String should have at least 8 characters'
                }
            }
        ),
        (
            {
                'username': 'testuser@email.com',
                'password': 'dsdasdasdasdasdstUSER1234testUSER1234testUSERasda1234testUSER1234testUSER1234testUSER1234testUSER123'
            },
            422,
            {
                'detail': {
                    'loc': ['body', 'password'],
                    'msg': 'String should have at most 30 characters'
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
                'detail': {
                    'loc': ['body', 'password'],
                    'msg': 'Input should be a valid string'
                }
            }
        ),
    ]   
)
async def test_invalid_password(client: AsyncClient, get_user_by_login, 
                                form, status_code, body):
    response: Response = await client.post(
        url="/registration",
        content=dumps(form)
    )
    assert response.status_code == status_code
    assert response.json() == body
    user_from_db = await get_user_by_login(form["username"])
    assert user_from_db is None