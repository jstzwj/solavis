from solavis.core.middleware import Middleware
from solavis.core.request import Request

class DepthMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_start_request(self, start_request, spider) -> Request:
        if start_request.meta is None:
            start_request.meta = {}
            start_request.meta['depth'] = 0
        else:
            start_request.meta['depth'] += 1
            print("url: " + start_request.url + "\n depth: "+ start_request.meta['depth'])
        
        return start_request

class BloomfilterMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_start_request(self, start_request, spider) -> Request:
        pass

