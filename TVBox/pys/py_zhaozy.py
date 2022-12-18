#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
from requests import session, utils

class Spider(Spider):
	def getDependence(self):
		return ['py_ali']
	def getName(self):
		return "py_zhaozy"
	def init(self,extend):
		self.ali = extend[0]
		print("============py_zhaozy============")
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		return result

	def homeVideoContent(self):
		result = {}
		return result

	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		return result

	header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
		"Referer": "https://zhaoziyuan.la/"
	}

	cookies = ''
	def getCookie(self):
		header = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
			"Referer": "https://zhaoziyuan.la/login.html",
			"Origin": "https://zhaoziyuan.la/"
		}
		data = {
			'username': '用户名',
			'password': '密码'
		}
		rsp = self.post('https://zhaoziyuan.la/logiu.html', data=data, headers=header)
		self.cookies = rsp.cookies
		return rsp.cookies

	def detailContent(self,array):
		tid = array[0]
		pattern = '(https://www.aliyundrive.com/s/[^\"]+)'
		url = self.regStr(tid,pattern)
		if len(url) > 0:
			return self.ali.detailContent(array)
		if len(self.cookies) <= 0:
			self.getCookie()
		rsp = self.fetch('https://zhaoziyuan.la/'+tid, cookies=self.cookies)
		url = self.regStr(rsp.text,pattern)
		if len(url) == 0:
			return ""
		newArray = [url]
		return self.ali.detailContent(newArray)

	def searchContent(self,key,quick):
		map = {
			'7':'文件夹',
			'1':'视频'
		}
		ja = []
		for tKey in map.keys():
			url = "https://zhaoziyuan.la/so?filename={0}&t={1}".format(key, tKey)
			if len(self.cookies) <= 0:
				self.getCookie()
			rsp = self.fetch(url, headers=self.header, cookies=self.cookies)
			root = self.html(self.cleanText(rsp.text))
			aList = root.xpath("//li[@class='clear']/div/div[@class='news_text']/a")
			for a in aList:
				title = self.xpText(a,'./h3/text()')
				pic = 'https://inews.gtimg.com/newsapp_bt/0/13263837859/1000'
				remark = self.xpText(a,'./p/text()').split('|')[1].strip()
				jo = {
					'vod_id': self.xpText(a,'@href'),
					'vod_name': title,
					'vod_pic': pic,
					"vod_remarks": remark
				}
				ja.append(jo)
		result = {
			'list':ja
		}
		return result

	def playerContent(self,flag,id,vipFlags):
		return self.ali.playerContent(flag,id,vipFlags)

	config = {
		"player": {},
		"filter": {}
	}
	header = {}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]