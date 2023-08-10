from abc import ABC, abstractmethod

from PIL import Image
import imagehash
import io



class Media(ABC):

    GPSINFO = ...
    DATETIME = ...

    def __init__(self, obj: bytes):
        self.obj = io.BytesIO(obj)

    @abstractmethod
    def _get_metadata(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def _get_hash(self) -> str:
        raise NotImplementedError
    
    @property
    def hash(self):
        return self._get_hash()
    
    @property
    def metadata(self):
        return self._get_metadata()


class SImage(Media):

    GPSINFO = 34853
    DATETIME = 306

    def _get_hash(self) -> str:
        image = Image.open(self.obj)
        hash = imagehash.average_hash(image)
        return str(hash)
    
    def _get_metadata(self) -> dict:
        img = Image.open(self.obj)
        exif_data = img._getexif()
        try:
            gps = exif_data[self.GPSINFO]
            latitude = (2 / 3) * (gps[2][0] + gps[2][1] / 60 + gps[2][2] / 3600)
            longitude = (2 / 3) * (gps[4][0] + gps[4][1] / 60 + gps[4][2] / 3600)
        except KeyError:
            latitude = None
            longitude = None
        return {
            "GPSInfo": {
                "latitude": latitude,
                "longitude": longitude
            },
            "datetime": exif_data[self.DATETIME]
        }


class SVideo(Media):
    
    def _get_hash(self) -> str:
        return super().get_hash()
    
    def _get_metadata(self) -> dict:
        return super().get_metadata()