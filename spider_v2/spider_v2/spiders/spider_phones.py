from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.selector import HtmlXPathSelector
from scrapy.loader.processors import TakeFirst
from spider_v2.items import SpiderItem
from spider_v2 import settings
import scrapy



class PhonesLoader(ItemLoader):
    default_output_processor = TakeFirst()


class PhoneSpider(CrawlSpider):
    name = "ph_spider"
    allowed_domains = settings.ALLOWED_DOMAINS
    start_urls = settings.START_URLS
    # rules —  http://gis-lab.info/qa/scrapy.html
    rules = (Rule(LxmlLinkExtractor(allow=("/real/kupit-kvartiry-")), follow=True),
             Rule(LxmlLinkExtractor(allow=("/nedvizhimost/kiev-prodam-")), callback='parse_item'))

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        ldr = PhonesLoader(SpiderItem(), hxs)
        ldr.add_xpath('phone', "//*[@id='hContacts']/div[2]/p[2]/text()")
        ldr.add_xpath('user_name', "//*[@id='hContacts']/div[2]/p[1]/a/text()")
        ldr.add_value('url', response.url)
        self.logger.debug("(parse_item) response: status=%d, URL=%s" % (response.status, response.url))
        return ldr.load_item()

    def logger_db(self, response):
        self.logger.debug("(logger_db) response: status=%d, URL=%s" % (response.status, response.url))
        if response.status in (302, 301) and 'Location' in response.headers:
            self.logger.debug("(parse_item) Location header: %r" % response.headers['Location'])
            yield scrapy.Request(
                response.urljoin(response.headers['Location']),
                callback=self.logger_db)

# http://stackoverflow.com/questions/35330707/scrapy-handle-302-response-code
# -s REDIRECT_ENABLED=0


# scrapy crawl ph_spider -s REDIRECT_ENABLED=0 -o ../../parsed_data_utf8.csv -t csv
