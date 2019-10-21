import pickle

from solavis.core.container import Container
from solavis.core.request import Request
from solavis.core.response import Response

from solavis.contrib.request import MemoryRequestLoader

class Spider(object):
    def __init__(self):
        self.start_urls = []
        self.container = None
        self.response = None

    def setContainer(self, container:Container) -> None:
        self.container = container

    def setResponse(self, response:Response) -> None:
        self.response = response

    async def request(self, url, method, state=None):
        if self.container is not None:
            req = Request(url, self.__class__.__name__, method.__name__, state)
            # middleware spider output
            for each_middleware, order in self.container.middlewares:
                req = await each_middleware.process_spider_output(self.response, req, self)

            # save request
            await self.container.request_loader.save(req)
        else:
            print('The spider is called before added to container!')

    async def save(self, item):
        if self.container is None:
            print('The spider is called before added to container!')

        # middleware spider output
        for each_middleware, order in self.container.middlewares:
            item = await each_middleware.process_spider_output(self.response, item, self)

        # pipeline
        for each_pipeline, order in self.container.pipelines:
            await each_pipeline.process_item(item)

    async def parse(self, response, state):
        pass