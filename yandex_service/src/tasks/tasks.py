from celery import Celery
from celery.result import AsyncResult

from utils.yrequests.requests import SyncDownloader
from utils.yrequests.auth_yandex import ClientYandex
from schemes import ObjectToInitialize
from env import CELERY_BACKEND, CELERY_BROKER
from .sync_db import Session
from db.models import Media



clr = Celery("tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)
clr.autodiscover_tasks()


@clr.task
def task_initialization(params_session: dict, objects: list, quantity: int, user: dict):
    non_init_objects = {}
    tasks_id = []
    for obj in objects:

        if "hash" not in obj["exif"].keys():
            result = task_download_objects.delay(params_session=params_session,
                                                link=obj["file"])
            task_id = result.id

            if ("gps_longitude", "gps_latitude") in obj["exif"].keys():
                gps_latitude = obj["exif"]["gps_latitude"]
                gps_longitude = obj["exif"]["gps_longitude"]
            else:
                gps_latitude = gps_longitude = None

            new_object = ObjectToInitialize(
                name=obj["name"],
                content_type=obj["mime_type"],
                owner="test_owner",
                created_on_service=obj["created"],
                modified_on_service=obj["modified"],
                # gps_latitude=0.0,
                # gps_longitude=0.0,
                link_for_downloading=obj["file"],
                id_tasks_for_download=task_id
            )
            non_init_objects[task_id] = new_object
            tasks_id.append(task_id)

    while True:
        completed = []
        new = []
        for task in tasks_id:
            res = AsyncResult(task, app=clr)
            if res.ready():
                if res.successful():
                    b_obj: bytes = res.result

                else:
                    obj = non_init_objects["task"]
                    link = obj.link_for_downloading
                    new_task = task_download_objects.delay(params_session=params_session, link=link)
                    new_id = new_task.id
                    non_init_objects.pop(task)
                    non_init_objects[new_id] = obj
                    new.append(new_task)
                completed.append(task)

        tasks_id = list(filter(lambda item: item not in completed, tasks_id))
        tasks_id.extend(new)
        completed.clear()
        new.clear()
        if tasks_id is None:
            break

    return {"objects": non_init_objects, "quantity": quantity}


@clr.task
def task_download_objects(params_session: dict, link: str):

    with ClientYandex(headers={"Authorization": params_session["Authorization"]},
                           base_url=params_session["base_url"],
                           root_directory=params_session["root_directory"]) as session:
    
        yrequests = SyncDownloader(session=session)

        response = yrequests.download(link)
        return {"byte_object": response}
    

# @clr.task
# def task_insert_obj_in_db(data: dict, download_id: str):
    
    

#     with Session() as session:
#         session.add(Media(
#             hash=...,
#             datetime_created=...,
#             content_type=data["content_type"],
#             name_on_service=data["name_on_service"],
#             created_on_service=data["created_on_service"],
#             modified_on_service=data["modified_on_service"],
#             gps_latitude=...,
#             gps_longitude=...,
#             service_id=...,
#         ))
#         session.commit()
