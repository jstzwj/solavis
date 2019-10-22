from multiprocessing import Queue

from solavis.core.request import RequestLoader

class MemoryRequestLoader(RequestLoader):
    def __init__(self):
        super().__init__()
        self.reqs = Queue()

    async def load(self):
        if not self.reqs.empty():
            return self.reqs.get()
        else:
            return None

    async def save(self, req):
        self.reqs.put(req)


class FileRequestLoader(RequestLoader):
    def __init__(self, dir_name):
        super().__init__()

    async def load(self):
        if not self.reqs.empty():
            return self.reqs.get()
        else:
            return None

    async def save(self, req):
        self.reqs.put(req)

    