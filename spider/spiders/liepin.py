# -*- coding: utf-8 -*-
import scrapy

from urllib import parse as urlparse
from spider.items import LiepinItem
from spider.pipelines import SpiderPipeline
from scrapy.utils.project import get_project_settings  #导入seetings配置
import pymysql
from twisted.enterprise import adbapi
from twisted.internet import defer
import sys
from datetime import datetime
import random


class LiepinSpider(scrapy.Spider):
    name = 'liepin'

    def start_requests(self):
        self.project = 'it'

        settings = get_project_settings()  #获取settings配置，设置需要的信息
        self.db = pymysql.connect(settings['MYSQL_HOST'], settings['MYSQL_USER'], settings['MYSQL_PASSWD'], settings['MYSQL_DBNAME'])
        self.cursor = self.db.cursor()

        sql = "SELECT `title` FROM title_" + self.project + " ORDER BY RAND()"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        self.keyword = result[0]
        print(self.keyword)
        # self.keyword = ' '.join(self.keyword.split('+'))

        

        yield scrapy.Request('https://www.liepin.com/zhaopin/?industries=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&industryType=&searchType=1&clean_condition=&isAnalysis=&init=1&sortFlag=15&flushckid=0&fromSearchBtn=1&headckid=86e340b5c4d42b08&d_headId=243d5e0a38dfec3c3052f8697268e14d&d_ckId=e0c94c87defa15a17beaf540e76752d7&d_sfrom=search_fp_nvbar&d_curPage=27&d_pageSize=40&siTag=1B2M2Y8AsgTpgAmY7PhCfg%7ENw_YksyhAxvGdx7jL2ZbaQ&key=' + self.keyword)

    def parse(self, response):

        job_list = response.css('.sojob-list li')

        item = LiepinItem()
        item['keywords'] = self.keyword
        item['spiderUrl'] = response.url

        for job in job_list:
            detail_url = job.css(".job-info h3 a::attr(href)").extract_first()
            item['jobId'] = detail_url.split('/')[-1].split('.')[0]
    
            sql = "SELECT `keywords` FROM position_" + self.project + " where `jobId` = '%s'"
            self.cursor.execute(sql % (item['jobId']))
            result = self.cursor.fetchone()
            # print(result)

            if result :
                if item['keywords'] in result[0].split('|'):
                    print("跳过: ", item['keywords'], item['jobId'])
                else:
                    newKeywords = result[0] + '|' + item['keywords']
                    sql = "UPDATE position_" + self.project + " SET `keywords` = '%s', `updatedTime` = '%s' where `jobId` = '%s'"
                    self.cursor.execute(sql % (newKeywords, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), item['jobId']))
                    self.db.commit()
                    print("更新成功: ", item['keywords'], item['jobId'], newKeywords)

                continue

            jobType = job.css(".icon b::text").extract_first()

            if ((jobType == '企') | (jobType == '急')):
                item['jobUrl'] = detail_url
                item['jobType'] = '企业'
                
            else :
                item['jobUrl'] = "https://www.liepin.com" + detail_url
                item['jobType'] = '猎头'

            yield scrapy.Request(url=item['jobUrl'], callback=self.detail, meta=item)

        # 下一页地址
        next_page_url = response.css('.pagerbar a:contains("下一页")::attr(href)').extract_first().strip()
        # print(next_page_url)
        if next_page_url != 'javascript:;':
            yield scrapy.Request(
                url=urlparse.urljoin(response.url, next_page_url),
                callback=self.parse)

    def detail(self, response):

        if (response.css('.job-offline-container p::text').extract_first() == '该职位已暂停招聘'):
            print('该职位已暂停招聘')
            return;

        item = response.meta
        print(item['jobUrl'])


        item['jobTitle'] = response.css('.about-position .title-info h1::text').extract_first()

        if (item['jobType'] == '企业'):
            item['companyName'] = response.css('.about-position .title-info h3 a::text').extract_first()
            item['companyUrl'] = response.css('.about-position .title-info h3 a::attr(href)').extract_first()
            companyUrlArray = item['companyUrl'].split('/')
            item['companyId'] = companyUrlArray[- 2]
            item['industry'] = response.css('.right-blcok-post .new-compintro li:nth-child(1) a::text').extract_first()

            companySize = response.css('.right-blcok-post .new-compintro li:nth-child(2)::text').extract_first()
            if (companySize):
                if (companySize[0:4] == '公司规模'):
                    item['companySize'] = companySize[5:]
                    item['companyAddress'] = response.css('.right-blcok-post .new-compintro li:nth-child(3)::text').extract_first()[5:]
                if (companySize[0:4] == '公司地址'):
                    item['companySize'] = ''
                    item['companyAddress'] = companySize[5:]
            else:
                item['companySize'] = ''
                item['companyAddress'] = ''

            item['salary'] = response.css('.about-position .job-title-left .job-item-title::text').extract_first().split()[0]
            item['position'] = response.css('.about-position .job-title-left .basic-infor span a::text').extract_first()
            item['qualification'] = response.css('.about-position .job-item .job-qualifications span::text').extract_first()
            item['pubTime'] = response.css('.about-position .job-item .basic-infor time::attr(title)').extract_first()

        else:
            item['companyName'] = ''
            item['companyUrl'] = ''
            item['companyId'] = ''
            item['companySize'] = response.css('.content-word li:nth-child(6)::text').extract_first()
            item['companyAddress'] = ''
            item['industry'] = response.css('.content-word li:nth-child(3) a::attr(title)').extract_first()
            item['salary'] = response.css('.about-position .job-title-left .job-main-title::text').extract_first().split()[0]
            item['position'] = response.css('.about-position .job-title-left .basic-infor span::text').extract_first()
            item['qualification'] = response.css('.about-position .resume span::text').extract_first()
            item['pubTime'] = response.css('.about-position  .basic-infor time::attr(title)').extract_first()

        item['description'] = response.css('.about-position div:nth-child(3) .content::text').extract_first().strip()
        

        if response.css('.title-info label::text').extract_first() == '该职位已结束':
            item['isEnd'] = 1
        else:
            item['isEnd'] = 0

        # print(item)
        
        # yield item

        sql = "insert into position_" + self.project + "(keywords,spiderUrl,jobId,jobTitle,jobType,jobUrl,companyId,companyUrl,companyName,salary,position,pubTime,qualification,description,industry,companySize,companyAddress,isEnd,createdTime,updatedTime) \
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        item['createdTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['updatedTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        params = (item['keywords'], item['spiderUrl'], item['jobId'], item['jobTitle'], item['jobType'],item['jobUrl'],item['companyId'],item['companyUrl'],
        item['companyName'],item['salary'],item['position'],item['pubTime'],item['qualification'],item['description'],item['industry'],
        item['companySize'],item['companyAddress'],item['isEnd'],item['createdTime'],item['updatedTime'])
        # print(sql)
        # print(params)
        self.cursor.execute(sql, params)
        self.db.commit()

        print("新增成功: ", item['keywords'], item['jobId'])


