import asyncio
import solavis
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import time

from solavis.core.response import Response

from solavis.contrib.middleware import DepthMiddleware
from solavis.contrib.request import SqliteRequestLoader

async def parse_html(html):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda :etree.HTML(html))
    return result

async def xpath(tree, path):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda :tree.xpath(path))
    return result

class GithubSpider(solavis.Spider):
    start_urls = ['https://github.com/jstzwj']
    def __init__(self):
        pass

    async def parse(self, response:Response):
        html = response.text
        # print(response.status)
        page = parse_html(html)
        following_href = await xpath(await page, "//a[@class='UnderlineNav-item mr-0 mr-md-1 mr-lg-3 ' and contains(text(), 'Following')]/@href")
        if len(following_href) > 0:
            following_url = following_href[0]
            await self.request("https://github.com" + following_url, self.parse_following)
            # print("add user to queue: " + following_url)

    async def parse_following(self, response):
        html = response.text
        page = parse_html(html)
        following_hrefs = await xpath(await page, "//a[@class='d-inline-block' and @data-hovercard-type='user']/@href")
        
        tasks = []
        for each_following_href in following_hrefs:
            tasks.append(
                asyncio.create_task(self.save(each_following_href[1:]))
                )
            tasks.append(
                asyncio.create_task(self.request("https://github.com" + each_following_href, self.parse))
                )
            # print("add following to queue: " + each_following_href)
        if len(tasks) > 0:
            await asyncio.wait(tasks)

class MongoPipeline(solavis.Pipeline):
    def __init__(self):
        pass

    async def open_spider(self):
        pass

    async def close_spider(self):
        pass

    async def process_item(self, item):
        # print(item)
        pass

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    github_spider = GithubSpider()
    mongo_pipeline = MongoPipeline()
    container = solavis.Container()

    container.set_delay(1)
    container.set_random_delay(True)
    container.add_spider(github_spider)
    container.add_pipeline(mongo_pipeline, 1)
    # container.add_middleware(DepthMiddleware(), 1)
    container.set_request_loader(SqliteRequestLoader(''))
    
    container.run()