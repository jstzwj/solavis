
from solavis.core.request import Request
from solavis.core.response import Response

class Middleware(object):
    def __init__(self):
        pass

    async def process_spider_input(self, response:Response, spider):
        pass

    async def process_spider_output(self, response:Response, result, spider):
        return result

    async def process_spider_exception(self, response:Response, exception: Exception, spider):
        pass

    async def process_start_request(self, start_request:Request, spider) -> Request:
        return start_request
