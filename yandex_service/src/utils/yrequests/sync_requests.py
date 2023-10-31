import typing

from httpx._status_codes import codes
from httpx import  Client
from httpx._client import EventHook
from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG, Limits
from httpx._transports.base import  BaseTransport
from httpx._types import AuthTypes, CertTypes, CookieTypes, HeaderTypes, ProxiesTypes, QueryParamTypes, TimeoutTypes, URLTypes, VerifyTypes



class ClientYandex(Client):

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
                mounts: typing.Mapping[str, BaseTransport] | None = None,
                timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
                follow_redirects: bool = False,
                limits: Limits = DEFAULT_LIMITS,
                max_redirects: int = DEFAULT_MAX_REDIRECTS,
                event_hooks: typing.Mapping[str, typing.List[EventHook]] | None = None,
                base_url: URLTypes = "",
                transport: BaseTransport | None = None,
                app: typing.Callable[..., typing.Any] | None = None,
                trust_env: bool = True,
                default_encoding: str | typing.Callable[[bytes], str] = "utf-8",
                root_directory: str):
        self.root_directory = root_directory
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


class SyncYRequests:
#add HttpException

    def __init__(self, session: ClientYandex) -> None:
        self.session = session
        self.root_directory = session.root_directory.strip('/')
        self.base_url = str(session.base_url).strip('/')

    def download(self, link: str) -> bytes:
        response = self.session.get(url=link)
        if response.headers["content-type"] == "application/octet-stream":
            response = self.session.get(
                url=response.headers["location"]
            )
        return response.content
    
    def delete(self, path: str, permanently: bool = False, fields: tuple = None) -> dict:
        request_url = f"{self.base_url}/?path=/{self.root_directory}/{path.strip('/')}&permanently={permanently}"
        if fields is not None:  #?
            request_url = request_url + "&fields" + str(fields)
        response = self.session.delete(
            url=request_url,
        )
        if response.status_code == codes.NO_CONTENT: #204
            return {"content": {"message": "Success"},
                    "status_code": codes.OK} #200
        else:
            return {"status_code": response.status_code,
                    "detail": response.json()}
        
    def upload():   #?
        pass