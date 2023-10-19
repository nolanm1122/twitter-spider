from scrapy.crawler import CrawlerProcess
from spiders.search_spider import SearchSpider
from scrapy.utils.project import get_project_settings

query = 'apple'
settings = get_project_settings()
settings.update({
    'FEEDS': {
        f'tweets_{query}.json': {'format': 'json', 'overwrite': True}
    }
})
process = CrawlerProcess(settings)
process.crawl(SearchSpider, query=query)
process.start()