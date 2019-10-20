import solavis

class GithubSpider(solavis.Spider):
    def __init__(self):
        pass

class MongoPipeline(solavis.Pipeline):
    def __init__(self):
        pass

if __name__ == "__main__":
    github_spider = GithubSpider()
    mongo_pipeline = MongoPipeline()
    container = solavis.Container()

    container.addSpider(github_spider)
    container.addPipeline(mongo_pipeline, 1)
    
    container.run()
