from uuid import uuid1
from datetime import datetime

from celery import Celery
from celery.result import AsyncResult
from httpx import ReadTimeout
from sqlalchemy import create_engine, text

from utils.yrequests.sync_requests import ClientYandex, SyncYRequests
from utils.schemes import ObjectFromDisk
from env import CELERY_BACKEND, CELERY_BROKER, DATABASE_SYNC_URL
from utils.hashing import SImage, SVideo



clr = Celery("tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)
clr.autodiscover_tasks()

engine = create_engine(DATABASE_SYNC_URL)


@clr.task(bind=True, acks_late=True)
def task_init_object(self, params_session: dict, link: str, obj: dict, user: dict):

    with ClientYandex(headers={"Authorization": params_session["Authorization"]},
                           base_url=params_session["base_url"],
                           root_directory=params_session["root_directory"]) as session:

        try:
            response = SyncYRequests(session=session).download(link)
        except ReadTimeout as exc:
            self.retry(exc=exc, countdown=2)

        if "image" in obj["content_type"]:
            media = SImage(response)
        else:
            media = SVideo(response)
        hash_obj = media.hash
        exif = media.metadata
        if exif["datetime"] is None:
            datetime_created = obj["created_on_service"]
        else:
            str_date = exif["datetime"].split(" ")[0].split(":")
            str_time = exif["datetime"].split(" ")[1].split(":")
            datetime_created = datetime(int(str_date[0]), int(str_date[1]), int(str_date[2]),
                                        int(str_time[0]), int(str_time[1]), int(str_time[2]))
        gps_latitude, gps_longitude = (exif["GPSInfo"]["latitude"], exif["GPSInfo"]["longitude"])

        with engine.connect() as conn:
            stmt = text(
                f"INSERT INTO media (hash, datetime_created, content_type,\
                                    name_on_service, created_on_service, modified_on_service,\
                                    gps_latitude, gps_longitude, service_id, id)\
                VALUES ('{hash_obj}', '{datetime_created}', '{obj['content_type']}',\
                        '{obj['name']}', '{obj['created_on_service']}', '{obj['modified_on_service']}',\
                        {gps_latitude}, {gps_longitude}, '{user['service']['id']}', '{uuid1(node=datetime.now().second)}');"
            )
            conn.execute(stmt)
            conn.commit()

        response = SyncYRequests(session).add_metadata_resource(
            path=obj["name"],
            add_param={
                "hash": hash_obj,
                "datetime_created": str(datetime_created),
                "content_type": obj["content_type"],
                "gps_latitude": gps_latitude,
                "gps_longitude": gps_longitude
            }
        )


@clr.task
def task_initialization(params_session: dict, objects: list, user: dict):
    
    tasks_id = []
    for obj in objects:
        if "custom_properties" not in obj.keys():
            new_object = ObjectFromDisk(
                name=obj["name"],
                content_type=obj["mime_type"],
                owner=user["id"],
                created_on_service=obj["created"],
                modified_on_service=obj["modified"],
                link_for_downloading=obj["file"],
            )
            result = task_init_object.delay(params_session=params_session,
                                             link=obj["file"],
                                             obj=new_object.model_dump(),
                                             user=user)
            tasks_id.append(result.id)

    # while len(tasks_id) != 0:
    #     completed = []
    #     for task in tasks_id:
    #         res = AsyncResult(task, app=clr)
    #         if res.ready():
    #             completed.append(task)

    #     tasks_id = list(filter(lambda item: item not in completed, tasks_id))

# Warning
# Backends use resources to store and transmit results.
# To ensure that resources are released, you must eventually call get() or forget()
# on EVERY AsyncResult instance returned after calling a task.

    #сделать ограничение на количество создаваемых задач
