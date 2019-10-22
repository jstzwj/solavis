
import asyncio
import aiohttp

from solavis.core.pipeline import Pipeline
from solavis.core.request import Request, RequestLoader
from solavis.core.response import Response

from solavis.contrib.request import MemoryRequestLoader

async def fetch(session, url:str, meta) -> Response:
    ret = Response()
    proxy_info = None
    if meta is not None:
        proxy_info = meta['proxy']
    async with session.get(url, proxy=proxy_info) as response:
        ret.status = response.status
        ret.reason = response.reason
        ret.url = response.url
        ret.content_type = response.content_type
        ret.charset = response.charset
        ret.text = await response.text()
        return ret

class Middleware(object):
    def __init__(self):
        pass

    async def process_open(self):
        pass

    async def process_close(self):
        pass

    async def process_request(self, request:Request, spider):
        pass

    async def process_response(self, request:Request, response:Response, spider):
        return response

    async def process_exception(self, response:Response, exception: Exception, spider):
        pass


class HttpMiddleware(Middleware):
    def __init__(self):
        pass
    
    async def process_open(self):
        self.session = await aiohttp.ClientSession().__aenter__()

    async def process_close(self):
        await self.session.__aexit__()
    
    async def process_request(self, request:Request, spider):
        response = await fetch(self.session, request.url, request.meta)

        # crawl page
        # print(f'fetch: {request.url}')
        response.meta = request.meta
        return response

    async def process_response(self, request:Request, response:Response, spider):
        pass

    async def process_exception(self, response:Response, exception: Exception, spider):
        pass
