import os
import typing
from json import dumps
from datetime import datetime

from fastapi import status
from fastapi.exceptions import HTTPException
from httpx import AsyncClient
from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG, Limits
from httpx._transports.base import AsyncBaseTransport
from httpx._types import AuthTypes, CertTypes, CookieTypes, HeaderTypes, ProxiesTypes, QueryParamTypes, TimeoutTypes, URLTypes, VerifyTypes



class AsyncClientYandex(AsyncClient):
    """
    All files that are images or videos and are automatically uploaded are stored in the root of one directory.
    This directory is "root_directory".
    """

    def __init__(self, 
                *,
                auth: AuthTypes | None = None,
                params: QueryParamTypes | None = None,
                headers: HeaderTypes | None = None,
                cookies: CookieTypes | None = None,
                verify: VerifyTypes = True,
                cert: CertTypes | None = None,
                http1: bool = True,
                http2: bool = False,
                proxies: ProxiesTypes | None = None,
                mounts: typing.Mapping[str, AsyncBaseTransport] | None = None,
                timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
                follow_redirects: bool = False,
                limits: Limits = DEFAULT_LIMITS,
                max_redirects: int = DEFAULT_MAX_REDIRECTS,
                event_hooks: typing.Mapping[str, typing.List[typing.Callable[..., typing.Any]]] | None = None,
                base_url: URLTypes = "",
                transport: AsyncBaseTransport | None = None,
                app: typing.Callable[..., typing.Any] | None = None,
                trust_env: bool = True,
                default_encoding: str | typing.Callable[[bytes], str] = "utf-8",
                root_directory: str,
                user: dict):
        self.root_directory = root_directory
        self.user = user
        super().__init__(auth=auth,
                        params=params,
                        headers=headers,
                        cookies=cookies,
                        verify=verify,
                        cert=cert,
                        http1=http1,
                        http2=http2,
                        proxies=proxies,
                        mounts=mounts,
                        timeout=timeout,
                        follow_redirects=follow_redirects,
                        limits=limits,
                        max_redirects=max_redirects,
                        event_hooks=event_hooks,
                        base_url=base_url,
                        transport=transport,
                        app=app,
                        trust_env=trust_env,
                        default_encoding=default_encoding)
        
    @property
    def custom_params(self) -> dict:
        return {
            "Authorization": self.headers["Authorization"],
            "base_url": str(self.base_url),
            "root_directory": self.root_directory
        }


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
        if fields is not None:
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
        if fields is not None:
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
        if fields is not None:
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
