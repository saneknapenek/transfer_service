import enum

from schemes import ObjectFromDisk, ObjectToInitialize, ListObjects
from utils.yrequests.requests import YRequests, SyncDownloader
from utils.yrequests.auth_yandex import AsyncClientYandex, ClientYandex
from tasks.tasks import task_initialization



async def get_objects_for_page(quantity_on_page: int, page: int, session: AsyncClientYandex) -> list:
    response = await YRequests(session).get_resource(
        limit=quantity_on_page,
        offset=quantity_on_page*(page-1),
        fields="_embedded.items",
        sort="-name"
    )
    return response["_embedded"]["items"]

async def get_object_for_path(path: str, session: AsyncClientYandex) -> dict:
    response = await YRequests(session).get_resource(
        session=session,
        path=path,
    )
    return response

async def get_link_for_download(name: str, session: AsyncClientYandex) -> str:
    link = await YRequests(session).download_object(path=name)
    return link

async def delete_object_for_name(name: str, session: AsyncClientYandex) -> dict:
    res = await YRequests(session).delete_object(path=name)
    return res

async def get_all_objects(session: AsyncClientYandex) -> dict[list, int]:
    yrequests = YRequests(session=session)
    quantity = await yrequests.get_resource(
        fields="_embedded.total"
    )
    total_quantity = quantity["_embedded"]["total"]
    all_objects = await yrequests.get_resource(
        limit=quantity["_embedded"]["total"],
        fields="_embedded.items",
        sort="-name"
    )
    return {"objects": all_objects["_embedded"]["items"], "quantity": total_quantity}


from celery.result import AsyncResult
from tasks.tasks import clr
async def disk_initialization(session: AsyncClientYandex) -> dict[list, int]:
    all_objects = await get_all_objects(session=session)

    task = task_initialization.delay(params_session=session.custom_params,
                              objects=all_objects["objects"],
                              quantity=all_objects["quantity"],
                              user={"user": 1})

    # res = AsyncResult(task.id, app=clr)

    # if res.ready():
    # # Задача выполнена
    #     if res.successful():
    #         res_value = res.result
    #     else:
    #         # Задача выполнена с ошибкой

    #         res_value = res.result

    # while not res.ready():
    #     pass
    # return res.result
    return 1