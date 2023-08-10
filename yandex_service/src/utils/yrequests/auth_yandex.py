import typing
from httpx import AsyncClient, Client
from httpx._client import EventHook
from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG, Limits
from httpx._transports.base import AsyncBaseTransport, BaseTransport
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
