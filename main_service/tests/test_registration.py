from json import dumps

from httpx import AsyncClient, Response

from src.auth.hashing import Hasher



password = "testUSER1234"
hashed_password = Hasher.get_password_hash(password)
user_data = {
    "login": "test_user_login",
    "name": "testusername",
    "email": "testuser@email.com",
    "password": password
}

async def test_reg(client: AsyncClient, get_user_by_id):
    response = await client.post(
        url="/registration",
        data=dumps(user_data)
    )
    assert response.status_code == 200
    resp_data = response.json()
    db_user = await get_user_by_id(resp_data["id"])
    assert db_user.login == user_data["login"] == resp_data["login"]
    assert db_user.email == user_data["email"] == resp_data["email"]
    assert db_user.name == user_data["name"] == resp_data["name"]
    assert Hasher.verify_password(password, db_user.password)

# async def test_already_exist(client: AsyncClient, get_user_by_id):
#     async def test_reg(client: AsyncClient, get_user_by_id):
#     password = "testUSER1234"
#     user_data = {
#         "login": "test_user_login",
#         "name": "testusername",
#         "email": "testuser@email.com",
#         "password": password
#     }
#     response = await client.post(
#         url="/registration",
#         data=dumps(user_data)
#     )
#     assert response.status_code == 200
#     resp_data = response.json()
#     db_user = await get_user_by_id(resp_data["id"])
#     assert db_user.login == user_data["login"] == resp_data["login"]
#     assert db_user.email == user_data["email"] == resp_data["email"]
#     assert db_user.name == user_data["name"] == resp_data["name"]
#     assert Hasher.verify_password(password, db_user.password)


async def test_login(client: AsyncClient, get_user_by_id, create_user):
    data = user_data.copy()
    data["password"] = hashed_password
    new_data = {
        "login": "test_user_login",
        "name": "Qtestusername",
        "email": "Qtestuser@email.com",
        "password": password
    }
    created_user = await create_user(data)
    response: Response = await client.post(
        url="/registration",
        data=dumps(new_data)
    )
    assert response.status_code == 409
    # assert response.json()
    raise ValueError(response.headers)