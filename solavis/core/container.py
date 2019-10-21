import asyncio
import aiohttp
import pickle
import sys
import time
import random

from solavis.core.pipeline import Pipeline
from solavis.core.request import Request, RequestLoader
from solavis.core.middleware import Middleware
from solavis.core.response import Response

from solavis.contrib.request import MemoryRequestLoader

async def fetch(session, url:str, meta) -> Response:
    ret = Response()
    proxy_info = None
    if meta is not None:
        proxy_info = meta['proxy']
    async with session.get(url, proxy=proxy_info) as response:
        ret.status = response.status
        ret.reason = response.reason
        ret.url = response.url
        ret.content_type = response.content_type
        ret.charset = response.charset
        ret.text = await response.text()
        return ret

class Container(object):
    def __init__(self):
        self.spiders = {}
        self.pipelines = []
        self.middlewares = []
        self.request_loader = MemoryRequestLoader()
        self.is_exit = False

        self.delay = 0
        self.random_delay = False

        self.crawl_counter = 0
        self.crawl_time = time.time()
        self.scrape_counter = 0
        self.scrape_time = time.time()

    def add_spider(self, spider):
        self.spiders[spider.__class__.__name__] = spider

    def add_pipeline(self, pipeline:Pipeline, order:int) -> None:
        for i in range(len(self.pipelines)):
            if self.pipelines[i][1] >= order:
                self.pipelines.insert(i, (pipeline, order))
                break

        self.pipelines.append((pipeline, order))

    def add_middleware(self, middleware:Middleware, order:int) -> None:
        for i in range(len(self.middlewares)):
            if self.middlewares[i][1] >= order:
                self.middlewares.insert(i, (middleware, order))
                break

        self.middlewares.append((middleware, order))

    def set_request_loader(self, loader:RequestLoader) -> None:
        self.request_loader = loader

    def set_delay(self, t:int) -> None:
        self.delay = t

    def set_random_delay(self, cond:bool) -> None:
        self.random_delay = cond

    async def dispatch_request(self, request, session):
        if not request.spider_name in self.spiders.keys():
            print('spider name no found')
            return

        if self.delay != 0:
            if self.random_delay:
                await asyncio.sleep(random.randint(0, self.delay))
            else:
                await asyncio.sleep(self.delay)

        # middleware start request
        for each_middleware, order in self.middlewares:
            request = await each_middleware.process_start_request(request, self.spiders[request.spider_name])
        
        response = await fetch(session, request.url, request.meta)
        spider_method = getattr(self.spiders[request.spider_name], request.method_name)

        # middleware spider input
        for each_middleware, order in self.middlewares:
            await each_middleware.process_spider_input(response, self.spiders[request.spider_name])
        
        # crawl page
        print("fetch: " + request.url)
        response.meta = request.state
        self.spiders[request.spider_name].setResponse(response)
        try:
            crawl_coro = spider_method(response)
            await crawl_coro
        except Exception as e:
            # middleware spider exception
            for each_middleware, order in self.middlewares:
                await each_middleware.process_spider_exception(response, e, self.spiders[request.spider_name])

        # print crawl speed
        self.crawl_counter += 1
        if self.crawl_counter == 100:
            print(f"crawl speed: {str(100/(time.time() - self.crawl_time + 0.00001))}q/s")
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
        
