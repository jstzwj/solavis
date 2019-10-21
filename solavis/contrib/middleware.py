from solavis.core.middleware import Middleware
from solavis.core.request import Request

class DepthMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_start_request(self, start_request, spider) -> Request:
        if start_request.state is None:
            start_request.state = {}
            start_request.state['depth'] = 0
        else:
            start_request.state['depth'] += 1
            print("url: " + start_request.url + "\n depth: "+ start_request.state['depth'])
        
        return start_request
