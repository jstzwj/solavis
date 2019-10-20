import asyncio
import aiohttp
import pickle
import sys
import time

from solavis.core.pipeline import Pipeline
from solavis.core.request import MemoryRequestLoader, Request

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
        self.request_loader = MemoryRequestLoader()
        self.is_exit = False
        self.crawl_counter = 0
        self.crawl_time = time.time()

    def addSpider(self, spider):
        self.spiders[spider.__class__.__name__] = spider
    
    def addPipeline(self, pipeline:Pipeline, order:int) -> None:
        for i in range(len(self.pipelines)):
            if self.pipelines[i][1] >= order:
                self.pipelines.insert(i, (pipeline, order))
                break

        self.pipelines.append((pipeline, order))
        
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
                if not request.spider_name in self.spiders.keys():
                    print('spider name no found')
                    continue
                
                response = fetch(session, request.url)
                spider_method = getattr(self.spiders[request.spider_name], request.method_name)
                
                crawl_coro = spider_method(await response, pickle.loads(request.state) if request.state is not None else None)
                asyncio.create_task(crawl_coro)
                
                # print speed
                self.crawl_counter += 1
                if self.crawl_counter == 10:
                    print(f"crawl speed: {str(10/(time.time() - self.crawl_time))}r/s")
                    self.crawl_counter = 0
                    self.crawl_time = time.time()

                

            print('Spider container stopped.')
        # pipeline close
        for each_pipeline, order in self.pipelines:
            await each_pipeline.close_spider()
    
    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl())
        
