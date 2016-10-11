from scrapy import Field, Item


class SpiderItem(Item):
    user_name = Field()
    phone = Field()
    url = Field()
    pass
