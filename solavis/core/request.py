from multiprocessing import Queue

class Request(object):
    def __init__(self, url:str, spider_name:str, method_name:str, state = None):
        self.url = url
        self.spider_name = spider_name
        self.method_name = method_name
        self.state = state

class RequestLoader(object):
    def __init__(self):
        pass

    async def load(self)->Request:
        pass
    
    async def save(self, req:Request):
        pass
    

    