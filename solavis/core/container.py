import asyncio
import aiohttp
import pickle
import sys
import time

from solavis.core.pipeline import Pipeline
from solavis.core.request import MemoryRequestLoader, Request
from solavis.core.middleware import Middleware

class Response(object):
    text = None

    def __init__(self):
        pass

async def fetch(session, url:str) -> Response:
    ret = Response()
    async with session.get(url) as response:
        ret.text = await response.text()
        return ret

class Container(object):
    def __init__(self):
        self.spiders = {}
        self.pipelines = []
        self.middlewares = []
        self.request_loader = MemoryRequestLoader()
        self.is_exit = False
        self.crawl_counter = 0
        self.crawl_time = time.time()
        self.scrape_counter = 0
        self.scrape_time = time.time()

    def addSpider(self, spider):
        self.spiders[spider.__class__.__name__] = spider

    def addPipeline(self, pipeline:Pipeline, order:int) -> None:
        for i in range(len(self.pipelines)):
            if self.pipelines[i][1] >= order:
                self.pipelines.insert(i, (pipeline, order))
                break

        self.pipelines.append((pipeline, order))

    def addMiddleware(self, middleware:Middleware, order:int) -> None:
        for i in range(len(self.middlewares)):
            if self.middlewares[i][1] >= order:
                self.middlewares.insert(i, (middleware, order))
                break

        self.middlewares.append((middleware, order))

    async def dispatch_request(self, request, session):
        if not request.spider_name in self.spiders.keys():
            print('spider name no found')
            return

        # middleware start request
        for each_middleware, order in self.middlewares:
            await each_middleware.process_start_requests(request, self.spiders[request.spider_name])
        
        response = await fetch(session, request.url)
        spider_method = getattr(self.spiders[request.spider_name], request.method_name)

        # middleware spider input
        for each_middleware, order in self.middlewares:
            await each_middleware.process_spider_input(response, self.spiders[request.spider_name])
        
        print("fetch: " + request.url)
        self.spiders[request.spider_name].setResponse(response)
        try:
            crawl_coro = spider_method(response, pickle.loads(request.state) if request.state is not None else None)
            await crawl_coro
        except Exception as e:
            # middleware spider exception
            for each_middleware, order in self.middlewares:
                await each_middleware.process_spider_exception(response, e, self.spiders[request.spider_name])


        # print crawl speed
        self.crawl_counter += 1
        if self.crawl_counter == 10:
            print(f"crawl speed: {str(10/(time.time() - self.crawl_time + 0.0001))}q/s")
            self.crawl_counter = 0
            self.crawl_time = time.time()
    
    async def crawl(self):
        # register spider to container
        for spider_name, each_spider in self.spiders.items():
            each_spider.setContainer(self)

        # preload urls
        for spider_name, each_spider in self.spiders.items():
            for each_url in each_spider.start_urls:
                await self.request_loader.save(Request(each_url, spider_name, 'parse', None))

        # pipeline init
        for each_pipeline, order in self.pipelines:
            await each_pipeline.open_spider()

        # run spiders
        async with aiohttp.ClientSession() as session:

            while True:
                request = await self.request_loader.load()
                if request is None:
                    await asyncio.sleep(1)
                    print('no new requests')
                    continue

                asyncio.create_task(self.dispatch_request(request, session))

            print('Spider container stopped.')
        # pipeline close
        for each_pipeline, order in self.pipelines:
            await each_pipeline.close_spider()
    
    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl())
        
