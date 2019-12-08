import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    # cate = scrapy.Field()
    image = scrapy.Field()
    # desc = scrapy.Field()
    brief = scrapy.Field()
    # cate = scrapy.Field()
    course_url = scrapy.Field()
    pass