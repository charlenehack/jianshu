# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy

import pymysql
from twisted.enterprise import adbapi  #  使用异步数据库处理连接池
from pymysql import cursors  #  数据库游标类

#########################同步插入数据库############################

class JianshuSpiderPipeline(object):
    def __init__(self):
        params = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '1326628437',
            'database': 'jianshu',
            'charset': 'utf8'
        }
        self.conn = pymysql.connect(**params)
        self.sursor = self.conn.cursor()
        self._sql = None

    @property   #  属性操作，可直接调用
    def sql(self):
        if not self._sql:
            self._sql = '''
              insert into article (title,author,avatar,publish_time,article_id,origin_url,content) values (%s,%s,%s,%s,%s,%s,%s)
              '''
            return self._sql
        return self._sql

    def process_item(self, item, spider):
        self.sursor.execute(self.sql, (item['title'], item['author'], item['avatar'], item['publish_time'],
                                      item['article_id'], item['origin_url'], item['content']))
        self.conn.commit()
        return item

##############异步实现插入数据库，插入操作是io操作，数据量大时，会出现堵塞，异步插入很有必要######################

class  JianshuTwistedPipeline(object):
    def __init__(self):
        params = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '1326628437',
            'database': 'jianshu',
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }
      #  调用异步连接池实现异步插入数据库
        self.dbpool = adbapi.ConnectionPool("pymysql", **params)
        self._sql = None

    @property
    def sql(self):
        if   not  self._sql:
            self._sql = '''
              insert into article (title,author,avatar,publish_time,article_id,origin_url,content) values (%s,%s,%s,%s,%s,%s,%s)
              '''
            return self._sql
        return self._sql

    def process_item(self, item, spider):
          #  异步插入数据
        defer = self.dbpool.runInteraction(self.insert_item, item)
          #  错误处理
        defer.addErrback(self.handle_error, item, spider)
        return item

    def insert_item(self, cursor, item):
        cursor.execute(self.sql, (item['title'], item['author'], item['avatar'], item['publish_time'],
                                      item['article_id'], item['origin_url'], item['content']))

    def handle_error(self, item, error, spider):   # 获取错误信息
        print('=' * 30 + 'error' + '=' * 30)
        print(error)
        print('=' * 30 + 'error' + '=' * 30)
