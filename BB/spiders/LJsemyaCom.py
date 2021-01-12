# -*- encoding: utf-8 -*-
import scrapy
from scrapy.item import Item
from scrapy.http import FormRequest
from scrapy.http import Request
import io
import re
import json
import urllib2
    
class LjLoginSpider(scrapy.Spider):

    name = 'lj_com'
    # start_urls = ['https://www.livejournal.com/login.bml']
    start_urls = ['https://www.livejournal.com/media/semya']

    # def parse(self, response):
    #     # contains the CSRF token value
    #     csrftok_value = response.xpath('//form[contains(@action, "/login.bml")]/input[@type = "hidden"]/@value').extract_first()
    #     # contains the name 'csrftok'
    #     csrftok_name = response.xpath('//form[contains(@action, "/login.bml")]/input[@type = "hidden"]/@name').extract_first()
    #     # contains the name 'email'
    #     email_name = 'user'
    #     # The email you will use to login into yelp
    #     email = 'arabian_gothic'

    #     # contains the name 'password'
    #     password_name = 'password'
    #     #the password you'll be using to log into your yelp account
    #     password = 'mamasBlog1988'

    #     # formxpath and formdata are used as arguments for the Scrapy post request

    #     # formxpath specifies which form to post to (in this case the login form)
    #     # and formdata builds a dictionary of name and value pairs for each field
    #     formxpath = '//*[contains(@class, "lj_login_form")]'
    #     formdata = {csrftok_name : csrftok_value, email_name : email, password_name : password}

    #     #call scrapy post request with after_login as callback
    #     return FormRequest.from_response(
    #         response,
    #         formxpath=formxpath,
    #         formdata=formdata,
    #         callback=self.after_login
    #         )

    # def after_login(self, response):
    #     #check login succeed before going on
    #     #phrase = sel.xpath('//a[contains (@class, "s-header-item__link--user")]/@title').extract()
    #     phrase = response.xpath('//title/text()').extract()
    #     presence = response.css('a.s-header-item__link--user::attr(title)').extract()
    #     for p in presence:
    #         print p
    #     for p in phrase:
    #         print p
    #         logged = u"Главное — Живой Журнал"
    #         if p == logged:
    #             print('Logged in succesfully.\n')
    #             yield Request('https://www.livejournal.com/media/semya', callback=self.parse_blogs)
    #             # Now you can continue scraping yelp while logged in using Scrapys request function and a new callback function

    #         elif p == "Log in":
    #             print('Unsuccessful login\n')
            
    #         else:
    #             print "Other cause"

    def parse(self, response):
        #posts_xpath = '//div[contains(@class, "stories__column")]/article/div[@class="story__inner"]/a/@href'
        if response.css('div.stories__column > article > div.story__inner > a.story-link::attr(href)'):
            story_links=response.css('div.stories__column > article > div.story__inner > a.story-link::attr(href)').extract()
            for st_link in story_links:
                yield response.follow(st_link, self.parse_stories)

        #https://fomaru.livejournal.com/fomaru/__rpc_get_thread?journal=fomaru&itemid=19061&flat=&skip=&media=1&page=2&_=1534173977188'  
        #next_page_xpath = '//a[contains(@class, "stories__button-nav--next")]/@href'
        next_page_css = response.css('a.stories__button-nav--next::attr(href)').extract()
        for nextpage_link in next_page_css:
            yield response.follow(url=nextpage_link, callback=self.parse)

    def parse_stories(self, response):
        url=response.url
        journal_users=False
        if response.css('div.b-grove div.svgpreloader-30'):
            if re.search(r'https://www\.livejournal\.com/media/', url):
                journal="medius"
                itemid = re.search(r'livejournal\.com/media/(\d*)\.html', url).group(1)
            # elif re.search(r'https://www\.livejournal\.com/', url):
            elif re.search(r'https://users\.livejournal', url):
                journal = re.search(r'livejournal\.com/(.+)/', url).group(1)
                itemid = re.search(r'livejournal\.com/'+journal+r'/(\d*)\.html', url).group(1)
                journal_users=True
            else:
                journal=re.search(r'https://(.*?)\.livejournal', url).group(1)
                itemid = re.search(r'livejournal\.com/(\d*)\.html', url).group(1)
                # https://users.livejournal.com/-niece/1215574.html?media
            sub_journal=re.sub('^-', '', journal)
            if response.xpath('//ul[@class="b-pager-pages"]'):
                    print "\n\nBPAGER\n\n"
                    pagenum=len(response.css('div.mdspost-comments-controls--first div.b-pager-first ul.b-pager-pages li.b-pager-page').extract())
                    new_links=[]
                    if journal == "medius":
                        for num in range(1, pagenum+1):
                            num=str(num)
                            args=(sub_journal,journal,itemid,num)
                            new_link = re.sub('(?<=/)media/\d+\.html', "%s/__rpc_get_thread?journal=%s&itemid=%s&flat=&skip=&media=&page=%s"%args, url)
                            # https://www.livejournal.com/media/696198.html
                            # https://www.livejournal.com/medius/__rpc_get_thread?journal=medius&itemid=721199&flat=&skip=&media=&page=
                            new_links.append(new_link)
                    elif journal_users==True:
                        for num in range(1, pagenum+1):
                            num=str(num)
                            args=(sub_journal,journal,journal,itemid,num)
                            new_link = re.sub('(?<=/)users\.livejournal\.com/.+/\d+\.html\?media', "%s.livejournal.com/%s/__rpc_get_thread?journal=%s&itemid=%s&flat=&skip=&media=&page=%s"%args, url)
                            # https://users.livejournal.com/-niece/1215574.html?media
                            # https://niece.livejournal.com/-niece/__rpc_get_thread?journal=-niece&itemid=1215574&flat=&skip=&media=&page=
                            new_links.append(new_link)
                    else:
                        for num in range(1, pagenum+1):
                            num=str(num)
                            args=(sub_journal,journal,itemid,num)
                            new_link = re.sub('(?<=/)(\d+)\.html\?media', "%s/__rpc_get_thread?journal=%s&itemid=%s&flat=&skip=&media=&page=%s"%args, url)
                            new_links.append(new_link)
                    for lnk in new_links:
                        print "\n\n NEW LINKS: "+lnk+"\n\n"
                        request=Request(lnk, self.parse_post_comments)
                        request.meta['journal']=journal
                        request.meta['itemid']=itemid
                        yield request

                            
            else:
                if journal == "medius":
                    args=(sub_journal,journal,itemid)
                    new_link = re.sub('(?<=/)media/\d+\.html', "%s/__rpc_get_thread?journal=%s&itemid=%s&flat=&skip=&media=&page="%args, url)
                elif journal_users==True:
                    args=(sub_journal,journal,journal,itemid)
                    new_link = re.sub('(?<=/)users\.livejournal\.com/.+/\d+\.html\?media', "%s.livejournal.com/%s/__rpc_get_thread?journal=%s&itemid=%s&flat=&skip=&media=&page="%args, url)
                else:
                    args=(sub_journal,journal,itemid)
                    new_link = re.sub('(?<=/)(\d+)\.html\?media', "%s/__rpc_get_thread?journal=%s&itemid=%s&flat=&skip=&media=&page="%args, url)
                print "\n NEW LINK WITHOUT PAGES \n"

                request=Request(new_link, self.parse_post_comments)
                request.meta['journal']=journal
                request.meta['itemid']=itemid
                yield request

        else:
            print "LOOKING FOR SOURCE"
            # https://www.livejournal.com/media/721199.html
            if response.xpath('//div[@itemprop="articleBody"]/p[@align="center"]/following-sibling::p/descendant-or-self::a/@href'):
                source=response.xpath('//div[@itemprop="articleBody"]/p[@align="center"]/following-sibling::p/descendant-or-self::a/@href').extract()
                # yield response.follow(source, self.parse_stories)
                for unit_source in source:
                    yield response.follow(unit_source, self.parse_source)
            else:
                pass

    def parse_source(self, response):
        url=response.url
        journal = re.search(r'https://(.*?)\.livejournal', url).group(1)
        itemid = re.search(r'\.com/(\d+)\.html', url).group(1)
        

    def parse_post_comments(self, response):
        # print "\n\n I AM HERE POST COMMENTS \n\n"
        url = response.url
        print "\n PARSED_URL: " + url + "\n"
        journal=response.meta['journal']
        itemid=response.meta['itemid']
        # journal = re.search(r'https://(.*?)\.livejournal', url).group(1)
        # itemid = re.search(r'itemid=(\d*)&', url).group(1)
        respobj = json.loads(response.body_as_unicode())
        # print "\n json loaded \n"
        respstr = json.dumps(respobj, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        # url = urllib2.urlopen(url)
        # obj = json.load(url)

        # if re.search(r'page=(\d)', url):
        #     page = re.search(r'page=(\d)', url).group(1)
        #     out=io.open('/Users/Nami/Desktop/LJ_semya_comments_test2/' + journal + "__" + itemid + "__" + page + '.txt','w', encoding = 'utf-8')
        #     out.write(respstr)
        #     out.close()

        # else:
        #     out=io.open('/Users/Nami/Desktop/LJ_semya_comments_test2/' + journal + "__" + itemid + "__" + '.txt','w', encoding = 'utf-8')
        #     out.write(respstr)
        #     out.close()

        
# form_links = map((new_link+"{}").format, pages_listed)
# print "\n\n" + form_links + " form links " + "\n\n"