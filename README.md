# solavis
An asynchronous python spider library.

# Demo

```
import solavis
class GithubSpider(solavis.Spider):
    start_urls = ['https://github.com/jstzwj']
    def __init__(self):
        pass

    async def parse(self, response:Response):
        html = response.text
        print(html)

if __name__ == "__main__":
    container = solavis.Container()
    container.add_spider(GithubSpider())
    container.run()
```