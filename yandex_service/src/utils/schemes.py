from datetime import datetime

from pydantic import BaseModel
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