from datetime import datetime

from celery import Celery
from celery.result import AsyncResult
from httpx import ReadTimeout

from utils.yrequests.requests import SyncDelete, SyncDownloader
from utils.yrequests.auth_yandex import ClientYandex
from schemes import ObjectFromDisk
from env import CELERY_BACKEND, CELERY_BROKER
from utils.sync.sync_db import Session
from utils.sync.hashing import SImage, SVideo
from db.models import Media



clr = Celery("tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)
clr.autodiscover_tasks()


@clr.task(bind=True, acks_late=True)
def task_init_object(self, params_session: dict, link: str, obj: dict, user: dict):

    with ClientYandex(headers={"Authorization": params_session["Authorization"]},
                           base_url=params_session["base_url"],
                           root_directory=params_session["root_directory"]) as session:

        try:
            response = SyncDownloader(session=session).download(link)
        except ReadTimeout as exc:
            self.retry(exc=exc, countdown=2)

        if "image" in obj["content_type"]:
            media = SImage(response)
        else:
            media = SVideo(response)
        hash_obj = media.hash
        exif = media.metadata
        str_date = exif["datetime"].split(" ")[0].split(":")
        str_time = exif["datetime"].split(" ")[1].split(":")
        datetime_created = datetime(int(str_date[0]), int(str_date[1]), int(str_date[2]),
                                    int(str_time[0]), int(str_time[1]), int(str_time[2]))
        gps_latitude = exif["GPSInfo"]["latitude"]
        gps_longitude = exif["GPSInfo"]["longitude"]

        with Session() as db_session:
            new_media = Media(
                hash=hash_obj,
                datetime_created=datetime_created,
                content_type=obj["content_type"],
                name_on_service=obj["name"],
                created_on_service=obj["created_on_service"],
                modified_on_service=obj["modified_on_service"],
                gps_latitude=gps_latitude,
                gps_longitude=gps_longitude,
                service_id=user["service"]["id"]
            )
            db_session.add(new_media)
            db_session.commit()    #if

        response = SyncDelete(session).delete(path=obj["name"],
                                              permanently=True)
        #?


@clr.task
def task_initialization(params_session: dict, objects: list, user: dict):
    
    tasks_id = []
    for obj in objects:
        if "hash" not in obj["exif"].keys():
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

    while len(tasks_id) != 0:
        completed = []
        for task in tasks_id:
            res = AsyncResult(task, app=clr)
            if res.ready():
                completed.append(task)

        tasks_id = list(filter(lambda item: item not in completed, tasks_id))
