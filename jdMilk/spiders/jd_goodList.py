#coding=utf-8

from scrapy.spiders import Spider
from jdMilk.items import goodsItem
from scrapy.selector import Selector
import scrapy
import re
import json

#import sys
#reload(sys)
#sys.path.append("/Users/eileen/PycharmProjects/jdSpiderMilk")
#sys.path.append("/Library/Python/2.7/site-packages/scrapy")
#sys.path.append("/Users/eileen/PycharmProjects/jdSpiderMilk/jdMilk")
class jdSpider(Spider):
    name = 'jd'
    start_urls = []
    for i in range(1,2):#页数，前1页
        url = 'https://search.jd.com/Search?keyword=%E8%BF%9B%E5%8F%A3%E7%89%9B%E5%A5%B6&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E8%BF%9B%E5%8F%A3%E7%89%9B%E5%A5%B6&stock=1&page=' + str(i)
        start_urls.append(url)

    def parse_price(self, response):
        item1 = response.meta['item']
        temp1 = response.body.split('jQuery([')
        s = temp1[1][:-4]  # 获取到需要的json内容
        js = json.loads(str(s))  # js是一个list
        if js.has_key('pcp'):
            item1['price'] = js['pcp']
        else:
            item1['price'] = js['p']
        return item1

    def parse_getCommentnum(self, response):
        item1 = response.meta['item']
        # response.body是一个json格式的
        js = json.loads(str(response.body))
        item1['score1count'] = js['CommentsCount'][0]['Score1Count']
        item1['score5count'] = js['CommentsCount'][0]['Score5Count']
        item1['comment_num'] = js['CommentsCount'][0]['CommentCount']
        num = item1['ID']  # 获得商品ID
        s1 = str(num)
        url = "http://pm.3.cn/prices/pcpmgets?callback=jQuery&skuids=" + s1[3:-2] + "&origin=2"
        yield scrapy.Request(url, meta={'item': item1}, callback=self.parse_price)

    def parse_detail(self, response):
        item1 = response.meta['item']
        sel = Selector(response)

        temp = response.body.split('commentVersion:')
        pattern = re.compile("[\'](\d+)[\']")
        if len(temp) < 2:
            item1['commentVersion'] = -1
        else:
            match = pattern.match(temp[1][:10])
            item1['commentVersion'] = match.group()

        url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds=" + str(item1['ID'][0])
        yield scrapy.Request(url, meta={'item': item1}, callback=self.parse_getCommentnum)

    def parse(self, response):  # 解析搜索页
        sel = Selector(response)  # Xpath选择器
        goods = sel.xpath('//li[@class="gl-item"]')
        for good in goods:
            item1 = goodsItem()
            item1['ID'] = good.xpath('./div/@data-sku').extract()
            item1['name'] = good.xpath('./div/div[@class="p-name"]/a/em/text()').extract()
            item1['shop_name'] = good.xpath('./div/div[@class="p-shop"]/@data-shop_name').extract()
            item1['link'] = good.xpath('./div/div[@class="p-img"]/a/@href').extract()
            url = "http:" + item1['link'][0] + "#comments-list"
            yield scrapy.Request(url, meta={'item': item1}, callback=self.parse_detail)
