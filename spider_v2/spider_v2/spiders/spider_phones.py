from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.selector import HtmlXPathSelector
from scrapy.loader.processors import TakeFirst
from spider_v2.items import SpiderItem
import scrapy


class PhonesLoader(ItemLoader):
    default_output_processor = TakeFirst()


class PhoneSpider(CrawlSpider):
    name = "ph_spider"
    allowed_domains = ["domik.ua"]
    start_urls = ["http://domik.ua/nedvizhimost/kiev/kupit-kvartiry.html"]
    # rules —  http://gis-lab.info/qa/scrapy.html
    rules = (Rule(LxmlLinkExtractor(allow=("/real/kupit-kvartiry-")), follow=True),
             Rule(LxmlLinkExtractor(allow=("/nedvizhimost/kiev-prodam-")), callback='parse_item'))

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        ldr = PhonesLoader(SpiderItem(), hxs)
        ldr.add_xpath('phone', "//*[@id='hContacts']/div[2]/p[2]/text()")
        ldr.add_xpath('user_name', "//*[@id='hContacts']/div[2]/p[1]/a/text()")
        ldr.add_value('url', response.url)
        return ldr.load_item()


class RedirectSpider(CrawlSpider):  # http://stackoverflow.com/questions/35330707/scrapy-handle-302-response-code
    name = "redirect"  # -s REDIRECT_ENABLED=0
    start_urls = ["http://domik.ua/nedvizhimost/kiev/kupit-kvartiry.html"]
    handle_httpstatus_list = [302, 301]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, callback=self.parse_page)

    def parse_page(self, response):
        self.logger.debug("(parse_page) response: status=%d, URL=%s" % (response.status, response.url))
        if response.status in (302, 301) and 'Location' in response.headers:
            self.logger.debug("(parse_page) Location header: %r" % response.headers['Location'])
            yield scrapy.Request(
                response.urljoin(response.headers['Location']),
                callback=self.parse_page)



# scrapy crawl ph_spider -s REDIRECT_ENABLED=0 -o scarped_data_utf8.csv -t csv
