import scrapy


class SpiderItem(scrapy.Item):
    keywords = scrapy.Field()
    url = scrapy.Field()
    jobId = scrapy.Field()
    jobTitle = scrapy.Field()
    jobType = scrapy.Field()
    companyId = scrapy.Field()
    companyUrl = scrapy.Field()
    companyName = scrapy.Field()
    salary = scrapy.Field()
    position = scrapy.Field()
    pubTime = scrapy.Field()
    qualification = scrapy.Field()
    description = scrapy.Field()
    industry = scrapy.Field()
    industryDetail = scrapy.Field()
    companySize = scrapy.Field()
    companyAddress = scrapy.Field()
    isEnd = scrapy.Field()
    createdTime = scrapy.Field()
    updatedTime = scrapy.Field()
    pass