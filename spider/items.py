import scrapy


class LiepinItem(scrapy.Item):
    keywords = scrapy.Field()
    spiderUrl = scrapy.Field()
    jobId = scrapy.Field()
    jobUrl = scrapy.Field()
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
    companySize = scrapy.Field()
    companyAddress = scrapy.Field()
    isEnd = scrapy.Field()
    createdTime = scrapy.Field()
    updatedTime = scrapy.Field()
    pass

class LinkedinItem(scrapy.Item):
    keywords = scrapy.Field()
    spiderUrl = scrapy.Field()
    jobId = scrapy.Field()
    jobUrl = scrapy.Field()
    jobType = scrapy.Field()
    jobTitle = scrapy.Field()
    companyName = scrapy.Field()
    companyUrl = scrapy.Field()
    jobFunction = scrapy.Field()
    description = scrapy.Field()
    industry = scrapy.Field()
    seniorityLevel = scrapy.Field()
    companyAddress = scrapy.Field()
    employmentType = scrapy.Field()
    createdTime = scrapy.Field()
    updatedTime = scrapy.Field()
    pass