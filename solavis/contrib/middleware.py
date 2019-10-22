from solavis.core.middleware import Middleware
from solavis.core.request import Request

class DepthMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_request(self, request, spider):
        if request.meta is None:
            request.meta = {}
            request.meta['depth'] = 0
        else:
            request.meta['depth'] += 1
            print("url: " + request.url + "\n depth: "+ request.meta['depth'])
        
        return request

class HttpProxyMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_request(self, request, spider):
        pass

class RedirectMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_request(self, request, spider):
        pass

class BloomfilterMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_request(self, request, spider):
        pass

