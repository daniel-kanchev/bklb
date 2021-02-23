import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bklb.items import Article


class BklbSpider(scrapy.Spider):
    name = 'bklb'
    start_urls = ['https://www.blkb.ch/die-blkb/medien/medienmitteilungen']

    def parse(self, response):
        links = response.xpath('//td//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('(//h1)[3]//text()').get()
        if title:
            title = title.strip()
        else:
            return

        date = response.xpath('//p[@class="small"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="clearfix journal-content-article"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
