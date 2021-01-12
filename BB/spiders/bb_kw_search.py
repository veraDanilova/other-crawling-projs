# -*- encoding: utf-8 -*-
import scrapy
import io
import re
from scrapy.item import Item
from scrapy.http import FormRequest
from scrapy.http import Request
import string
from random import randint
# from scrapy.exporters import JsonItemExporter

class Bb_Spider(scrapy.Spider):
	name = 'bb_kw'
	allowed_domains = [
        "babyblog.ru"
    ]
	start_urls = ['https://www.babyblog.ru/search/all/']
	# одинокая мать 
	# мать одиночка 
	# самомама

	def parse(self, response):
		formxpath='//*[contains(@id, "searchMainForm")]'
		formdata = {'query' : 'мать одиночка'}
		return FormRequest.from_response(response,
			formxpath=formxpath,
			formdata=formdata,
			callback=self.after_post)

	def encode_items(self, xpath):
		encoded = []
		for p in xpath:
			p=str(p.encode('utf-8'))
			encoded.append(p)
		item ='\n'.join(map(str, encoded))
		#item = item.decode('utf-8')
		return item

	def replace_punct(self, withpunct):
		chars=re.escape(string.punctuation)
		nopunct=re.sub(r'['+chars+']', '', withpunct)
		return nopunct

	def after_post(self, response):
		url=response.url
		
		basenodes=response.css('div.blog-entry')
		print "\n START URL:  " + url + "\n"

		for index, node in enumerate(basenodes):
			if not node.css('div.bb-questions-item'):
				titles=node.css('h2 > a.js__objectTitle::text').extract()
				title=self.encode_items(titles)
				dates=node.css('div.post-data > span::text').extract()
				date=self.encode_items(dates)
				texts=node.xpath('div[contains(@class, "blog-text")]/pre/descendant-or-self::node()/text()').extract()
				text_enc=self.encode_items(texts)
				if node.css('div[class="created rel"] div.avatar a::attr(href)'):
					user_ids=node.css('div[class="created rel"] div.avatar a::attr(href)').extract()
					user_ids=str(user_ids)
					if re.search('(?<=/lenta/)(.+)\']', user_ids):
						id_str=re.search('(?<=/lenta/)(.+)\']', user_ids).group(1)
					else:
						id_str="deleted_user"
				else:
					id_str="anonymous_user"

				# args=(index, url, title, date, text_enc, id_str)
				# dataline="\n#-#\n + URL: + %d + \n#-#\n + URL:  + %s + \n#-#\n + Title:  + %s + \n#-#\n + Date:  + %s + \n#-#\n + Text:  + %s + \n#-#\n + User:  + %s + \n#-#\n" % args
				# print "DATALINE: "+ dataline.decode('utf-8')
				if node.css('div.blog-text > p.clear > a::attr(href)'):
					full_comm = node.css('div.blog-text > p.clear > a::attr(href)').extract_first()
					to_next = response.urljoin(full_comm)
					print "\n\n" + "BUILDS THE FULL TEXT LINK" + to_next + 'TEXT:' + text_enc.decode('utf-8') + "\n\n"
					request = Request(url=to_next, callback=self.parse_full_text)
					request.meta['title']=title
					request.meta['date']=date
					request.meta['text']=text_enc
					request.meta['str_id']=id_str
					request.meta['fc_url']=to_next
					yield request
				else:
					print "\n\n IN ELSE \n\n"
					for_title=self.replace_punct(title)
					if id_str=="anonymous_user":
						id_str="anonymous_user_"+str(randint(1000,10000))
					if id_str=="deleted_user":
						id_str="deleted_user_"+str(randint(1000,10000))
					out=io.open('/Users/Nami/Desktop/BB_mothers/keywords/messages/' + "__" + id_str + "__" + for_title + '.txt','w', encoding = 'utf-8')
					rstring="\n#-#\n" + "URL: " + url + "\n#-#\n" + "Title: " + title + "\n#-#\n" + "Date: " + date + "\n#-#\n" + "Text: " + text_enc + "\n#-#\n" + "User: " + id_str + "\n#-#\n"
					result_string = rstring.decode('utf-8')
					out.write(result_string)
					out.close()
			else:
				print "\n\n I CONTINUE \n\n"
				continue

		if response.xpath('//div[@class="created rel"]/a[contains (@class, "user-name")]/@href'):
			user_links=response.xpath('//div[@class="created rel"]/a[contains (@class, "user-name")]/@href').extract()
			for user_link in user_links:
				if re.search('(?<=/lenta/)(.+)', user_link):
					yield response.follow(user_link, self.parse_user_lenta)
				else:
					continue

		next_page_rel_links = response.css('div.pagination2 > div > span > a::attr(href)')
		for link in next_page_rel_links:
			yield response.follow(link, self.after_post)

	def parse_full_text(self, response):
		url = response.url
		print "\n\n\n ENTERS THE FULL TEXT PARSER, PARSES THE URL: " + url
		good_url=response.meta['fc_url']
		# print "\n\n" + "TYPE URL  " + url + good_url + "\n\n"
		if url in str(good_url):
			title=response.meta['title']
			date=response.meta['date']
			text=response.meta['text']
			id_str=response.meta['str_id']
			full_t=response.xpath('//div[contains(@class, "blog-entry")]/div[contains(@class, "blog-text")]/pre/descendant-or-self::node()/text()').extract()
			full_t_enc=self.encode_items(full_t)
			if response.xpath('//div[contains(@class, "js__commentText")]/descendant-or-self::node()/text()'):
				cms_array=[]
				cm_nodes=response.xpath('//div[contains(@class, "js__comment")][@data-level]')
				for index,cm_node in enumerate(cm_nodes, start=1):
					if cm_node.css('div.avatar div.js__avatarPopupComments[data-login] a[title]::attr(href)'):
						user_rel_url_list=cm_node.css('div.avatar div.js__avatarPopupComments[data-login] a[title]::attr(href)').extract()
						# for com_u_link in user_rel_url_list:
						# 	yield response.follow(com_u_link, self.parse_user_lenta)
						user_rel_url=self.encode_items(user_rel_url_list)
					else:
						user_rel_url="No info"

					comment_date_list=cm_node.css('div.posted b[class="_12 _lgr"]::text').extract()
					comment_date=self.encode_items(comment_date_list)
					comment_text=cm_node.xpath('div[contains(@class,"js__commentText")]/descendant-or-self::node()/text()').extract()
					encoded = []
					for p in comment_text:
						p=str(p.encode('utf-8'))
						encoded.append(p)
					each_cm_text ='\n'.join(map(str, encoded))
					args=(index, user_rel_url, comment_date, each_cm_text)
					comment_info="\n - comment info %d - \n comment_user_url: %s \n date_of_comment: %s \n text_of_comment: %s \n -comment info end - " % args

					cms_array.append(comment_info)
				comments='\n'.join(map(str, cms_array))
			else:
				comments="None"
			print "TITLE: "+title
			for_title=self.replace_punct(title)
			if id_str=="anonymous_user":
				id_str="anonymous_user_"+str(randint(1000,10000))
			if id_str=="deleted_user":
						id_str="deleted_user_"+str(randint(1000,10000))
			out=io.open('/Users/Nami/Desktop/BB_mothers/keywords/messages/' + "__" + id_str + "__" + for_title + '.txt','w', encoding = 'utf-8')
			rstring="\n#-#\n" + "URL: " + url + "\n#-#\n" + "Title: " + title + "\n#-#\n" + "Date: " + date + "\n#-#\n" + "Text: " + text + "\n#-#\n" + "User: " + id_str + "\n#-#\n" + "FULL TEXT: " + full_t_enc + "\n#-#\n" + "COMMENTS: " + comments + "\n#-#\n"
			result_string = rstring.decode('utf-8')
			out.write(result_string)
			out.close()

	def parse_user_lenta(self, response):
		#detailed info on: https://www.babyblog.ru/user/info/id2556849
		url = response.url
		print "\n\n\n ENTERS THE PARSE USER LENTA, PARSES THE URL: " + url
		user_info = re.sub('/user/lenta/', '/user/info/', url)
		yield response.follow(user_info, self.parse_user_info)
	def parse_user_info(self, response):
		print "I AM IN USER INFO"
		url=response.url
		user_id = re.search(r'(?<=/info/).+', url).group()
		#city
		cities = response.css('div[class="info oh rel"] > div[class="marks fr"] > div[class="marked fl rel"]::text').extract()
		city=self.encode_items(cities)
		#country
		countries=response.css('div[class="info oh rel"] > div[class="marks fr"] > div[class="marked fl rel"] > u::text').extract()
		country=self.encode_items(countries)
		messages=response.xpath('//div[@class="clearfix mb4"]/descendant-or-self::a/text()').re(r'\d+')[0]
		messages=messages.encode('utf-8')
		friends=response.xpath('//div[@class="clearfix mb4"]/descendant-or-self::a/text()').re(r'\d+')[1]
		friends=friends.encode('utf-8')
		albums=response.xpath('//div[@class="clearfix mb4"]/descendant-or-self::a/text()').re(r'\d+')[2]
		albums=albums.encode('utf-8')
		#birthdate
		bdates=response.css('div[class="clearfix mb4"] > h3::text').extract()
		bdate=self.encode_items(bdates)
		if re.search(r'[0-9]+ .+ [0-9]{4}', bdate):
			bdate = re.search(r' [0-9]+ .+ [0-9]{4} ', bdate).group()
		#childreninfo
		if response.xpath('//div[contains(@class, "profile-child")]/descendant-or-self::node()/text()'):
			cdata=response.xpath('//div[contains(@class, "profile-child")]/descendant-or-self::node()/text()').extract()
			childinfo=self.encode_items(cdata)
		else:
			childinfo = "No info"
		#progress
		if response.css('div.progressbar > span.progress-status >u::text'):
			bbdata=response.css('div.progressbar > span.progress-status >u::text').extract()
			bbinfo=self.encode_items(bbdata)
		else:
			bbinfo = "No info"
		#communities
		if response.css('div[class="clearfix mb4"] ul.list li.mb1 a::attr(href)'):
			community_keys=response.css('div[class="clearfix mb4"] ul.list li.mb1 a::attr(href)').extract()
			community_values=response.css('div[class="clearfix mb4"] ul.list li.mb1 a::text').extract()
			# cvaluescontainer=[]
			# for p in community_values:
			# 	p=str(p.encode('utf-8'))
			# 	cvaluescontainer.append(p)

			def create_dict(keys, values):
				return dict(zip(keys, values + [None] * (len(keys) - len(values))))
			newdict=create_dict(community_keys, community_values)
			dict_str='\n'.join(['%s : %s' % (key, value) for (key, value) in newdict.items()])
			# print "dict_str: "+ dict_str
			dict_str=dict_str.encode('utf-8')
		else:
			dict_str="No info"

		out=io.open('/Users/Nami/Desktop/BB_mothers/keywords/accounts/' + "__" + user_id + "__" + '.txt','w', encoding = 'utf-8')
		rstring="\n#-#\n" + "URL: " + url + "\n#-#\n" + "City: " + city + "\n#-#\n" + "Country: " + country + "\n#-#\n" + "user_id: " + user_id + "\n#-#\n" + "BirthDate or Activity: " + bdate + "\n#-#\n" + "Children: " + childinfo + "\n#-#\n" + "Children in progress: " + bbinfo + "\n#-#\n" + "No of messages: " + messages + "\n#-#\n" + "No of friends: " + friends + "\n#-#\n" + "No of photoalbums: " + albums + "\n#-#\n" + "Communities:\n" + dict_str + "\n#-#\n"
		result_string = rstring.decode('utf-8')
		out.write(result_string)
		out.close()