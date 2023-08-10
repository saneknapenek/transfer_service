from PIL import Image
import imagehash
import io


class Hasher:

    def image_hash(b_image: bytes) -> str:
        image = Image.open(io.BytesIO(b_image))
        hash = imagehash.average_hash(image)
        return hash
    
    def video_hash(b_video: bytes) -> str:
        pass


class ExifData:

    GPSInfo = ...
    latitude = ...
    longitude = ...

    def get_exif(obj: bytes) -> dict:
        pass