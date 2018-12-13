# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http.response.html import HtmlResponse

#  用selenium重写请求过程，实现去爬取一些用ajax加载的页面
#  一些点赞数，评论数，喜欢数，推荐阅读的文章链接都是ajax加载的。
class SeleniumDownloadMiddleware(object):
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('headless')   # 隐藏浏览器选项
        self.browser = webdriver.Chrome(chrome_options=self.option)
        self.wait = WebDriverWait(self.browser, 10)

    def process_request(self, request, spider):
        # YES = request.url.endswith('.html')   # 用来判断哪些页面需要调用浏览器
        # if YES:
        self.browser.get(request.url)
        print('我正在用selenium自动化工具下载url')
        time.sleep(1)
        try:
            while  True:
                #  这里因为有些文章下方有许多加载更多，在文章被一下专栏收录里，所以要重复点击
                showmore = self.browser.find_element_by_class_name('show-more')
                showmore.click()
                time.sleep(0.3)
                if not showmore:   # 当没有加载更多可点击时退出循环
                    break
        except:
            pass
        source = self.browser.page_source
        response = HtmlResponse(url=self.browser.current_url, request=request, body=source, encoding='utf-8')
        return response  # 将结果返回给爬虫处理
