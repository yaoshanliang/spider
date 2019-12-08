from spider.db import DBHelper

class SpiderPipeline(object):
    # 连接数据库
    def __init__(self):
        self.db = DBHelper()
    
    def process_item(self, item, spider):
        # 插入数据库
        self.db.insert(item)
        return item

