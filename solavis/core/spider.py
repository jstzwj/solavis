import pickle

from solavis.core.container import Container
from solavis.core.request import Request
from solavis.core.response import Response

from solavis.contrib.request import MemoryRequestLoader

class Spider(object):
    def __init__(self):
        self.start_urls = []
        self.container = None

    def setContainer(self, container:Container) -> None:
        if type(container) != Container:
            raise RuntimeError("setContainer: container shall be type of Container")
        self.container = container

    async def request(self, url, method, meta=None):
        if self.container is not None:
            req = Request(url, self.__class__.__name__, method.__name__, meta)

            # save request
            await self.container.request_loader.save(req)
        else:
            print('The spider is called before added to container!')

    async def save(self, item):
        if self.container is None:
            print('The spider is called before added to container!')
        # pipeline
        for each_pipeline, order in self.container.pipelines:
            await each_pipeline.process_item(item)

    async def parse(self, response, meta):
        pass