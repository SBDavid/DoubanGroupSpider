import scrapy

'''
scrapy crawl group_topic -o result/shanghai.xml -a group=558292
'''

class ArticleLink(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()

class DoubanGroupSpider(scrapy.Spider):
    name = "group_topic"
    pageCount = 1

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 0.5,
        'DEFAULT_REQUEST_HEADERS': {
            "Host": "www.douban.com",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Cookie": 'll="108296"; bid=7X-KQZ2FHSI; ps=y; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1502690883%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DRV36u6KGO1E5mDJ6NBxZphOJIrTCZtqFz5B2WLRl3WKQ7yRvJAu4mWxAIGLoMbLT9bsJbmvEatB79i9HW4KrW_%26ck%3D2912.3.79.196.446.380.343.791%26shh%3Dwww.baidu.com%26sht%3Dbaidu%26wd%3D%26eqid%3D9e17334800011425000000055991121c%22%5D; push_noty_num=0; push_doumail_num=0; __utmt=1; ap=1; as="https://www.douban.com/group/topic/105197785/"; _pk_id.100001.8cb4=190ee1ed74ea681f.1502275096.4.1502690948.1502682917.; _pk_ses.100001.8cb4=*; __utma=30149280.1750424429.1502275097.1502679582.1502690884.4; __utmb=30149280.13.5.1502690948183; __utmc=30149280; __utmz=30149280.1502679582.3.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=30149280.11931',
        },
        'ITEM_PIPELINES': {
            'DoubanGroupSpider.pipelines.JsonWriterPipeline': 0
        }
    }

    def start_requests(self):

        urls = []
        for i in range(0, 1):
            urls.append('https://www.douban.com/group/%(groupid)s/discussion?start=%(start)s' % {'groupid': self.group, 'start': i*25})

        print('爬虫初始地址')
        print(urls)

        for url in urls:
            yield scrapy.Request(
                url=url, 
                callback=self.parse
            )

    def parse(self, response):

        for tr in response.xpath('//table[@class="olt"]//tr[@class=""]'):
            ''' yield {
                    'title': tr.css('a::attr(title)').extract_first(),
                    'author':  tr.css('td')[1].css('a::text').extract_first(),
                } '''
            ''' 获取链接地址 '''
            yield response.follow(tr.xpath('td[@class="title"]/a/@href').extract_first(), self.topicParse) 
    
    def topicParse(self, response):
        ''' 取出图片信息 '''
        topicFigures = []
        for topicFigure in  response.xpath('//div[@id="link-report"]/div[@class="topic-content"]/div[@class="topic-figure cc"]'):
            topicFigures.append({
                'img': topicFigure.xpath('img/@src').extract_first(),
                'title': topicFigure.xpath('span/text()').extract_first(default="not found")
            })


        yield {
            'topic-content': '---'.join(response.xpath('//div[@id="link-report"]/div[@class="topic-content"]/p/text()').extract()),
            'fav-num': response.xpath('//div[@class="sns-bar-fav"]/span[@class="fav-num"]/a/text()').extract_first(default="0"),
            'topic-figure': topicFigures
        }
        