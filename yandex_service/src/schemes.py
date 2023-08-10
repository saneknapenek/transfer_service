from datetime import date, datetime, time
from typing_extensions import Unpack

from pydantic import BaseModel, Base64Bytes, Field
from pydantic import field_validator



class ObjectFromDisk(BaseModel):
    """
    Model for sending objects to synchronous service for disk initialization
    """
    name: str
    content_type: str
    owner: str

    created_on_service: datetime
    modified_on_service: datetime
    link_for_downloading: str

    @field_validator("created_on_service", "modified_on_service", mode='before')
    def validate_datetime(cls, val):
        str_date = val[:10].split("-")
        str_time = val[11:19:1].split(":")
        date_time = datetime(int(str_date[0]), int(str_date[1]), int(str_date[2]), int(str_time[0]), int(str_time[1]), int(str_time[2]))
        return date_time


class InitObjectFromDisk(ObjectFromDisk):
    """
    Model for already initialized objects
    """
    hash: str
    datetime_created: str

    @field_validator("datetime_created", mode="before")
    def validate_datetime_created(cls, val: datetime | str): #2023:10:16T12:30:45
        if type(val) == str:
            str_date = val.split("T")[0].split(":")
            str_time = val.split("T")[1].split(":")
            return datetime(int(str_date[0]), int(str_date[1]), int(str_date[2]),
                            int(str_time[0]), int(str_time[1]), int(str_time[2]))
        return val


# class ObjectToInitialize(ObjectFromDisk):
#     id_tasks_for_download: str


class ListObjects(BaseModel):
    objects: list[InitObjectFromDisk]

    @field_validator("objects", mode='before')
    def parsing_list(cls, val: list):
        list_objects = []
        for item in val:
            obj = InitObjectFromDisk(
                name=item["name"],
                content_type=item["mime_type"],
                owner="user",
                created_on_service=["created"],
                modified_on_service=["modified"],
                link_for_downloading=["file"],
                hash=item["custom_propertis"]["hash"],
                datetime_created=item["custom_propertis"]["datetime_created"]
            )
            list_objects.append(obj)
        return list_objects


class ListNames(BaseModel):
    names: list