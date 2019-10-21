

class Middleware(object):
    def __init__(self):
        pass

    async def process_spider_input(self, response, spider):
        pass

    async def process_spider_output(self, response, result, spider):
        pass

    async def process_spider_exception(self, response, exception, spider):
        pass

    async def process_start_request(self, start_request, spider):
        pass


class DepthMiddleware(Middleware):
    def __init__(self):
        pass

    async def process_spider_input(self, response, spider):
        pass

    async def process_spider_output(self, response, result, spider):
        pass

    async def process_spider_exception(self, response, exception, spider):
        pass

    async def process_start_request(self, start_request, spider):
        pass

