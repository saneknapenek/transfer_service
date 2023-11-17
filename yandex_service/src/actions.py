from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from utils.yrequests.requests import YRequests, AsyncClientYandex
from tasks.tasks import task_initialization
from db.repositories.media import MediaAlchemy
from db.repositories.service import ServiceAlchemy
from db.models import SERVICES


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

async def delete_object_for_name(name: str, session: AsyncClientYandex, db_session: AsyncSession) -> dict:
    obj = await get_object_for_path(path=name, session=session)
    if "custom_properties" in obj.keys():
        await MediaAlchemy(session=db_session).delete(id=obj["custom_properties"]["id"])
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

async def del_media_db(id: UUID, current_user: dict, db_session: AsyncSession):
    media = await MediaAlchemy(db_session).get(id)
    if current_user["service"].id == media.id:
        return await MediaAlchemy(db_session).delete(id)
    else:
        return False
    

async def disk_initialization(session: AsyncClientYandex) -> dict[list, int]:
    all_objects = await get_all_objects(session=session)
    task = task_initialization.delay(params_session=session.custom_params,
                              objects=all_objects["objects"],
                              user={"id": session.user["id"],
                                    "service": {"id": str(session.user["service"].id)}})
    return task.id
    # yield task.id
    #закрывать task
