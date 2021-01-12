# -*- encoding: utf-8 -*-

#scrapy startproject tutorial

#scrapy crawl EGmention > res.txt

#ctrl C - stop scrapy in terminal

#pydoc modules - list of python modules installed
#python -c'import gensim'
#just enter python
#comment a block of code - cmd+/
#pico path_to_file - open text editor
#search regex in terminal: grep -lr "" *
#curl -O https://b install frow website
#brew uninstall python ; brew install python

#Error: Could not link:
#/usr/local/share/man/man1/brew.1
#Please delete these paths and run `brew update`.
#Error: Could not link:
#/usr/local/share/doc/homebrew
#find file by name: find / -name scrapy.dmg OR locate filename
# ./ ../ --> relative file paths
#START SCRAPY SHELL: add 
#[settings]
#shell = ipython
#command: scrapy shell <url>

#TERMINAL:
#ctrl+D --> exist a process

#XPath is a language for selecting nodes in XML documents, 
#which can also be used with HTML. CSS is a language for 
#applying styles to HTML documents. 
#It defines selectors to associate those styles with specific HTML 
#elements.

import StringIO # a file-like class that reads and writes a string buffer

from functools import partial

from scrapy.http import Request

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import BaseSpider 
# from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from scrapy.item import Item

from pprint import pprint
import codecs
import io
import csv



class MySpider(BaseSpider):
    #задаем имя, домены, стартовые адреса, правила краулера (), каунты, функция проверки ключевых слов, берущая на вход response

    """ Crawl through web sites you specify """

    name = "LJ_semya"

    # Stay within these domains when crawling
    allowed_domains = [
        "livejournal.com"
    ]

    start_urls = [
        "https://www.livejournal.com/media/semya"
    ]

    # Add our callback which will be called for every found link
    # rules = (
    #     Rule (SgmlLinkExtractor(restrict_xpaths=('//div[contains(@class, "stories__column")]/article/div[@class="story__inner"]/a/@href')), callback='parse_posts', follow=True),
    #     Rule (SgmlLinkExtractor(restrict_xpaths=('//a[contains(@class, "stories__button-nav--next")]')), follow=True)
    #     )

    # How many pages crawled? XXX: Was not sure if CrawlSpider is a singleton
    # class
    crawl_count = 0

    # How many text matches we have found
    key_words = 0   

    def parse(self, response):
        sel = Selector(response)

        #next_page_xpath = '//a[contains(@class, "stories__button-nav--next")]/@href'
        next_page_css = sel.css('a.stories__button-nav--next::attr(href)').extract()
        for nextpage_link in next_page_css:
            yield Request(url=nextpage_link, callback=self.parse)
        #posts_xpath = '//div[contains(@class, "stories__column")]/article/div[@class="story__inner"]/a/@href'
        posts_css = sel.css('div.stories__column > article > div.story__inner > a::attr(href)').extract()
        for new_link in posts_css:
            yield Request(url=new_link, callback=self.parse_posts)

    def parse_posts(self, response):
        """ Check a server response page (file) for possible violations """

        # Do some user visible status reporting
        self.__class__.crawl_count += 1

        crawl_count = self.__class__.crawl_count

        url = response.url

        # # Check response content type to identify what kind of payload this
        # # link target is
        # ct = response.headers.get("content-type", "").lower()

        # if "pdf" in ct:
        #     # Assume a PDF file
        #     # data = self.get_pdf_text(response)
        #     return Item()
        # else:
        #         # Assume it's HTML
        #     data = response.body

        sel = Selector(response)

        body1=sel.xpath('//div[@itemprop="articleBody"]/descendant-or-self::text()').extract()
        body2 = sel.xpath("//p/text()").extract()
        # body3 = sel.xpath('//div/div/span/text()').extract()
        # body4 = sel.xpath('//article/descendant-or-self::span/text()').extract()
        #body3 = sel.xpath('//span/text()').extract()
        #body3 = sel.xpath('//div/div[contains(@class, "asset-body")]/span/text()').extract()
        #body4 = sel.css('div.b-singlepost-bodywrapper > article > p > span > span::text') | ('span::text')).extract()
        
        encodedBody=[]
        
        for p in body1:
            p=str(p.encode("utf-8"))
            encodedBody.append(p)
    
        for p in body2:
            p=str(p.encode("utf-8"))
            encodedBody.append(p)
    
        # for p in body3:
        #     p=str(p.encode("utf-8"))
        #     encodedBody.append(p)

        # for p in body4:
        #     p=str(p.encode("utf-8"))
        #     encodedBody.append(p)

        # for p in body5:
        #     p=str(p.encode("utf-8"))
        #     encodedBody.append(p)

        stringBody='\n'.join(map(str, encodedBody))

        encodedBrief = []
        brief = sel.xpath('//div[@itemprop = "description"]/text()').extract()
        brief2 = sel.xpath('//meta[@name = "description"]/@content').extract()
        for bt in brief:
            bt = str(bt.encode("utf-8")) 
            encodedBrief.append(bt)
        for bt in brief2:
            bt = str(bt.encode("utf-8")) 
            encodedBrief.append(bt)
        stringBrief = ','.join(map(str, encodedBrief))
        stringBrief = stringBrief.decode('utf-8')

        title = sel.xpath("//title/text()").extract()
        if len(title) > 0:
            title = title[0].encode('utf-8')
        else:
            title = ''
        title = title.decode('utf-8')

        pubdate=sel.css('p.aentry-head__date > time::text').extract()
        pubdate=''.join(pubdate)
        # pubdate=pubdate.decode('utf-8')
        

        tagtexts1 = sel.css('div.mdspost-extra__tags > a::text').extract()
        tagtexts2 = sel.css('div.aentry-tags > a::text').extract()
        tagtexts3 = sel.css('span.b-singlepost-tags-items > a::text').extract()
        encodedTags = []
        for tag in tagtexts1:
            tag=str(tag.encode("utf-8"))
            encodedTags.append(tag)
        for tag in tagtexts2:
            tag=str(tag.encode("utf-8"))
            encodedTags.append(tag)
        for tag in tagtexts3:
            tag=str(tag.encode("utf-8"))
            encodedTags.append(tag)
        stringTags = ','.join(map(str, encodedTags))
        stringTags = stringTags.decode('utf-8')

        # datalines = []
        # basenodes=sel.css('div.comment-meta')
        # for index, node in enumerate(basenodes):
        #     args = (index, node.css('div.comment-date > abbr.datetime > span::text').extract(), node.css('span.commenter-name > span.ljuser> a::attr(href)').extract(), node.css('div.comment-body::text').extract())
        #     print "%d, %s, %s, %s" % args
        #     dataline = "%d, %s, %s, %s" % args
        #     datalines.append(dataline)
        # stringLines = '\n'.join(map(str, datalines))

        if len(stringBody) > 0:
            out=io.open('/Users/Nami/Desktop/LJ_semya4/' + title + '.txt','w', encoding = 'utf-8')
            if type(stringBody) != unicode:
                stringBody =  stringBody.decode('utf-8')
                stringBody = stringBody.replace(u'В этом журнале запрещены анонимные комментарии','')
                stringBody = stringBody.replace(u'Автор записи увидит Ваш IP адрес','')
                stringBody = stringBody.replace(u'Зарегистрируйтесь, пишите статьи и делитесь ими со всем миром','')
                stringBody = stringBody.replace(u'Ваш ответ будет скрыт','')
                # out.write('\n#-#\n' + title + pubdate + stringTags + stringBrief)
                out.write('\n#-#\n' + 'Title' + '\n#-#\n' + title + '\n#-#\n' + 'URL' + '\n#-#\n' + url + '\n#-#\n' + 'Pubdate' + '\n#-#\n' + pubdate + '\n#-#\n' + 'Tags' + '\n#-#\n' + stringTags + '\n#-#\n' + 'BriefBody'  + '\n#-#\n' + stringBrief + '\n#-#\n' + 'Body' + '\n#-#\n' + stringBody)
            else:
                # out.write('\n#-#\n' + title + pubdate + stringTags + stringBrief)
                out.write('\n#-#\n' + 'Title' + '\n#-#\n' + title + '\n#-#\n' + 'URL' + '\n#-#\n' + url + '\n#-#\n' + 'Pubdate' + '\n#-#\n' + pubdate + '\n#-#\n' + 'Tags' + '\n#-#\n' + stringTags + '\n#-#\n' + 'BriefBody'  + '\n#-#\n' + stringBrief + '\n#-#\n' + 'Body' + '\n#-#\n' + stringBody)  
            out.close()
        return Item()

# for div in sel.css('.mdspost-entry__wrapper'):
        #     if str(div.css('span[class = " mdspost-furtherdata__item mdspost-furtherdata__item--category "] > a::attr(href)').extract()) == "[u'https://www.livejournal.com/media/semya']":
        #         print "I AM HERE"

    # def _requests_to_follow(self, response):

    #     if getattr(response, "encoding", None) != None:
    #             # Server does not set encoding for binary files
    #             # Do not try to follow links in
    #             # binary data, as this will break Scrapy
    #             return CrawlSpider._requests_to_follow(self, response)
    #     else:
    #             return []

 # root_cat=sel.xpath('//ul[contains(@class, "categories-list")]')
        # domain_marker = sel.xpath('//li[@class=" categories-list-item js-collapse-item  "]/a/@href="https://www.livejournal.com/media/semya/"')
        
        # for domain_marker in root_cat:
        #     print "yes"
#import scrapy
# from scrapy_LJ.items import ScrapyLjItem
# item = ScrapyLjItem()
# item["title"] = sel.xpath("//title/text()").extract()
# item["text_body"] = sel.xpath('//div[@itemprop = "articleBody"]/text()').extract()

# yield item

# items.append(item)
# with open('log.txt', 'a') as f:
#   f.write('name: {0}, link: {1}\n'.format(item['title'], item['link']))

#sel.xpath("//title/text()")[0].extract()

# def start_requests(self):
#     requests = []
#     for item in start_urls:
#       requests.append(Request(url=item, headers={'Referer':'http://www.example.com/'}))
#     return requests    

# root_cat=sel.xpath('//ul[contains(@class, "categories-list")]')
        # domain_marker = sel.xpath('//li[@class=" categories-list-item js-collapse-item  "]/a/@href="https://www.livejournal.com/media/semya/"')
        
        # for domain_marker in root_cat:
        #     print "YAHOOOOOOOOO"
   # def follow_links(self, response):
    #     sel = Selector(response)
    #     links = sel.xpath('//h3[contains(@class, "story__title")]/a/@href').extract()
    #     for link in links:
    #         print "YAHOOOOOOOOO"
    #         yield scrapy.Request(url = link, callback = self.parse_attr) 

