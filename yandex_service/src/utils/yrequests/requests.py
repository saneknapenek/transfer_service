from json import dumps
from datetime import datetime
import os
import base64

from fastapi import status
from fastapi.exceptions import HTTPException

from .auth_yandex import AsyncClientYandex, ClientYandex



class YRequests:
    """
    In all methods, the "path" parameter is essentially the name of the file on the disk.
    """

    def __init__(self, session: AsyncClientYandex) -> None:
        self.session = session
        self.root_directory = session.root_directory.strip('/')
        self.base_url = str(session.base_url).strip('/')
    
    async def get_resource(self, path: str = "", **kwargs) -> dict:
        """
        Request meta information about a file or folder on disk.
        """
        request_url = f"{self.base_url}/?path=/{self.root_directory}/{path.strip('/')}"
        keys = ("limit", "fields", "sort", "offset")
        for key in keys:
            if key in kwargs.keys():
                request_url += f"&{key}={kwargs[key]}"
        response = await self.session.get(
            url=request_url
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
        return response.json()
    
    async def add_metadata_resource(self, path: str, add_param: dict, fields: tuple = None) -> dict:
        """
        Add custom meta information to a file or folder on disk.
        """
        request_url = f"{self.base_url}/?path=/{self.root_directory}/{path.strip('/')}"
        if not fields is None:
            request_url = request_url + "&fields" + str(fields)
        response = await self.session.patch(
            url=request_url,
            data=dumps({
                "custom_properties": add_param
            })
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
        return response.json()
    
    async def delete_object(self, path: str, permanently: bool = False, fields: tuple = None) -> dict:
        """
        Delete a file or folder on a disk.
        """
        request_url = f"{self.base_url}/?path=/{self.root_directory}/{path.strip('/')}&permanently={permanently}"
        if not fields is None:
            request_url = request_url + "&fields" + str(fields)
        response = await self.session.delete(
            url=request_url,
        )
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return {"content": {"message": "Success"}, "status_code": status.HTTP_200_OK}
        else:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
    
    async def download_object(self, path: str) -> str:
        """
        Download link from disk server.
        """
        request_url = f"{self.base_url}/download/?path=/{self.root_directory}/{path.strip('/')}"
        response = await self.session.get(
            url=request_url
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
        link_for_download = response.json()['href']
        return link_for_download

    async def downloader(self, link: str, save: bool = False, path_save: str = "./binary_objects") -> dict[dict, bytes]:
        """
        Download from the link.
        The "save" option determines whether to save the file or not.
        "path_save" - save path
        """
        response = await self.session.get(
            url=link
        )
        if save:
            try:
                now_date = f"{datetime.now().date()}"
                os.mkdir(f"{path_save}/{now_date}")
            except FileExistsError:
                pass
        
        if response.status_code != status.HTTP_200_OK and response.status_code != status.HTTP_302_FOUND:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
        if response.headers["content-type"] == "application/octet-stream":
            response = await self.session.get(
                url=response.headers["location"]
            )
        return {"headers": response.headers, "content": response.content}

    async def upload_object(self,
                            object: bytes, name_on_disk: str,
                            overwrite: bool = False, fields: tuple = None):
        """
        Upload a new or update an existing file.
        """
        request_url = f"{self.base_url}/upload/?path=/{self.root_directory}/{name_on_disk}"
        if overwrite is True:
            request_url += "&overwrite=true"
        if not fields is None:
            request_url = request_url + "&fields" + str(fields)
        
        response = await self.session.get(
            url=request_url,
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
        return await self.uploader(self.session, response.json()["href"], object)
    
    async def uploader(self, link_on_upload: str, byte_object: bytes) -> dict:
        response = await self.session.put(
            url=link_on_upload,
            data=byte_object
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code,
                                detail=response.json())
        return response.headers
    


class SyncDownloader:

    def __init__(self, session: ClientYandex) -> None:
        self.session = session
        self.root_directory = session.root_directory.strip('/')
        self.base_url = str(session.base_url).strip('/')

    def download(self, link: str) -> bytes:

        response = self.session.get(
            url=link
        )
        
        if response.headers["content-type"] == "application/octet-stream":
            response = self.session.get(
                url=response.headers["location"]
            )
        
        return response.content