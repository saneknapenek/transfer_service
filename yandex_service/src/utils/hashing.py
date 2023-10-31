from abc import ABC, abstractmethod
import io

from PIL import Image
import imagehash



class Media(ABC):

    GPSINFO = ...
    DATETIME = ...

    def __init__(self, obj: bytes):
        self.__obj = io.BytesIO(obj)

    @abstractmethod
    def _get_metadata(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def _get_hash(self) -> str:
        raise NotImplementedError
    
    @property
    def hash(self):
        if f"_{self.__class__.__name__}__hash" in self.__dict__:
            return self.__hash
        else:
            self.__hash = self._get_hash()
            return self.__hash

    @property
    def metadata(self):
        if f"_{self.__class__.__name__}__metadata" in self.__dict__:
            return self.__metadata
        else:
            self.__metadata = self._get_metadata()
            return self.__metadata


class SImage(Media):

    GPSINFO = 34853
    DATETIME = 306

    def _get_hash(self) -> str:
        image = Image.open(self.__obj)
        hash = imagehash.average_hash(image)
        return str(hash)
    
    def _get_metadata(self) -> dict:
        img = Image.open(self.__obj)
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
        return super()._get_hash()
    
    def _get_metadata(self) -> dict:
        return super()._get_metadata()