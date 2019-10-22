import solavis
from solavis.contrib.request import SqliteRequestLoader


class GithubSpider(solavis.Spider):
    def __init__(self):
        super().__init__()
        self.start_urls = ['https://github.com/jstzwj/']
    async def parse(self, response):
        print(response.status)



if __name__ == "__main__":
    container = solavis.Container()
    container.add_spider(GithubSpider())
    container.set_request_loader(SqliteRequestLoader(''))
    container.run()