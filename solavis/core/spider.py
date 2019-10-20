import pickle

from solavis.core.container import Container
from solavis.core.request import MemoryRequestLoader, Request

class Spider(object):
    def __init__(self):
        self.start_urls = []
        self.container = None

    def setContainer(self, container:Container) -> None:
        self.container = container

    async def request(self, url, method, state = None):
        if self.container is not None:
            await self.container.request_loader.save(
                Request(url, self.__class__.__name__, method.__name__, pickle.dumps(state))
                )
        else:
            print('The spider is called before added to container!')

    async def save(self, item):
        if self.container is None:
            print('The spider is called before added to container!')
        for each_pipeline, order in self.container.pipelines:
            await each_pipeline.process_item(item)
    
    async def parse(self, response, state):
        pass