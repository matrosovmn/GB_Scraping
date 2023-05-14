import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from LabirintRuScraper.spiders.labirint_spider import LabirintRuSpider

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(LabirintRuSpider)
    process.start()
