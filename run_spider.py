import asyncio
import solavis
from lxml import etree

from solavis.core.container import Response

class GithubSpider(solavis.Spider):
    start_urls = ['https://github.com/jstzwj']
    def __init__(self):
        pass

    async def parse(self, response:Response, state):
        html = response.text
        page = etree.HTML(html)
        following_href = page.xpath("//a[@class='UnderlineNav-item mr-0 mr-md-1 mr-lg-3 ' and contains(text(), 'Following')]/@href")
        if len(following_href) > 0:
            following_url = following_href[0]
            await self.request("https://github.com" + following_url, self.parse_following)
            print("add user to queue: " + following_url)

    async def parse_following(self, response, state):
        html = response.text
        page = etree.HTML(html)
        following_hrefs = page.xpath("//a[@class='d-inline-block' and @data-hovercard-type='user']/@href")
        
        tasks = []
        for each_following_href in following_hrefs:
            tasks.append(
                asyncio.create_task(self.save(each_following_href[1:]))
                )
            tasks.append(
                asyncio.create_task(self.request("https://github.com" + each_following_href, self.parse))
                )
            print("add following to queue: " + each_following_href)
        
        await asyncio.gather(tasks)

class MongoPipeline(solavis.Pipeline):
    def __init__(self):
        pass

    async def open_spider(self):
        pass

    async def close_spider(self):
        pass

    async def process_item(self, item):
        print(item)

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    github_spider = GithubSpider()
    mongo_pipeline = MongoPipeline()
    container = solavis.Container()

    container.addSpider(github_spider)
    container.addPipeline(mongo_pipeline, 1)
    
    container.run()