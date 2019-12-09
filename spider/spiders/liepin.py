# -*- coding: utf-8 -*-
import scrapy

from urllib import parse as urlparse
from spider.items import SpiderItem
import sys

class LiepinSpider(scrapy.Spider):
    name = 'liepin'
    # allowed_domains = ['liepin.com']
    # start_urls = ['']
    
    # def __init__(self, keyword=None, *args, **kwargs):
    #     super(LiepinSpider, self).__init__(*args, **kwargs)
    #     self.start_urls = ['https://www.liepin.com/zhaopin/?industries=&dqs=&salary=&jobKind=2&pubTime=&compkind=&compscale=&industryType=&searchType=1&clean_condition=&isAnalysis=&init=1&sortFlag=15&flushckid=0&fromSearchBtn=1&headckid=86e340b5c4d42b08&d_headId=243d5e0a38dfec3c3052f8697268e14d&d_ckId=e0c94c87defa15a17beaf540e76752d7&d_sfrom=search_fp_nvbar&d_curPage=0&d_pageSize=40&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7ENw_YksyhAxvGdx7jL2ZbaQ&key=' + keyword]

    def start_requests(self):
        yield scrapy.Request('https://www.liepin.com/zhaopin/?industries=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&industryType=&searchType=1&clean_condition=&isAnalysis=&init=1&sortFlag=15&flushckid=0&fromSearchBtn=1&headckid=86e340b5c4d42b08&d_headId=243d5e0a38dfec3c3052f8697268e14d&d_ckId=e0c94c87defa15a17beaf540e76752d7&d_sfrom=search_fp_nvbar&d_curPage=0&d_pageSize=100&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7ENw_YksyhAxvGdx7jL2ZbaQ&key=' + self.keyword)

    def parse(self, response):

        job_list = response.css('.sojob-list li')

        item = SpiderItem()

        for job in job_list:

            detail_url = job.css(".job-info h3 a::attr(href)").extract_first()
            item['jobId'] = detail_url.split('/')[-1].split('.')[0]

            if (job.css(".icon b::text").extract_first() == '企'):
                item['jobUrl'] = detail_url
                item['jobType'] = '企业'
                item['industry'] = job.css(".company-info > .field-financing span::text").extract_first().strip()
            else :
                item['jobUrl'] = "https://www.liepin.com" + detail_url
                item['jobType'] = '猎头'
                item['industry'] = job.css(".company-info > .field-financing span a::text").extract_first()

            print(item)

            # 进入课程详情页面
            yield scrapy.Request(
                url=item['jobUrl'], callback=self.detail, meta=item)

        # 下一页地址
        next_page_url = response.css('.pagerbar a:contains("下一页")::attr(href)').extract_first().strip()
        print(next_page_url)
        if next_page_url != 'javascript:;':
            yield scrapy.Request(
                url=urlparse.urljoin(response.url, next_page_url),
                callback=self.parse)

    def detail(self, response):
        item = response.meta

        item['title'] = response.css('.about-position .title-info h1::text').extract_first()
        item['company'] = response.css('.about-position .title-info h3 a::text').extract_first()
        item['companyUrl'] = response.css('.about-position .title-info h3 a::attr(href)').extract_first()
        companyUrlArray = item['companyUrl'].split('/')
        item['companyId'] = companyUrlArray[- 2]

        item['salary'] = response.css('.about-position .job-title-left .job-item-title::text').extract_first().split()[0]
        item['position'] = response.css('.about-position .job-title-left .basic-infor span a::text').extract_first()
        item['qualification'] = response.css('.about-position .job-item .job-qualifications span::text').extract_first()
        item['description'] = response.css('.about-position div:nth-child(3) .content::text').extract_first()
        item['industryDetail'] = response.css('.right-blcok-post .new-compintro li:nth-child(1) a::text').extract_first()
        item['companySize'] = response.css('.right-blcok-post .new-compintro li:nth-child(2)::text').extract_first()[5:]
        item['companyAddress'] = response.css('.right-blcok-post .new-compintro li:nth-child(3)::text').extract_first()

        if response.css('.title-info label::text').extract_first() == '该职位已结束':
            item['isEnd'] = 1
        else:
            item['isEnd'] = 0

        print(item)
        
        yield item
