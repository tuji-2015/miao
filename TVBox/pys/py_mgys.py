#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import hashlib
import urllib

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "蘑菇视频"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电影":"1",
			"剧集":"2",
			"综艺":"4",
			"动漫":"3"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})

		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']	
		return result
	def homeVideoContent(self):
		rsp = self.fetch("https://www.moguys.xyz/",self.headerp)
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='module-items']/div")
		videos = []
		for a in aList:
			name = a.xpath('.//@title')[0]
			pic = a.xpath('.//img/@data-src')[0]
			mark = a.xpath(".//div[@class='module-item-caption']/span/text()")[0]
			sid = a.xpath(".//@href")[0]
			sid = self.regStr(sid,"/voddetail/(\\S+).html")
			videos.append({
				"vod_id":sid,
				"vod_name":name,
				"vod_pic":pic,
				"vod_remarks":mark
			})
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		if 'id' not in extend.keys():
			extend['id'] = tid
		extend['page'] = pg
		filterParams = ["id", "area", "by", "class", "lang", "", "", "", "page", "", "", "year"]
		params = ["", "", "", "", "", "", "", "", "", "", "", ""]
		for idx in range(len(filterParams)):
			fp = filterParams[idx]
			if fp in extend.keys():
				params[idx] = extend[fp]
		suffix = '-'.join(params)
		url = 'https://www.moguys.xyz/vodshow/{0}.html'.format(suffix)
		rsp = self.fetch(url,self.headerp)
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='module-items']/div")
		videos = []
		for a in aList:
			name = a.xpath('.//@title')[0]
			pic = a.xpath('.//@data-src')[0]
			mark = a.xpath(".//div[@class='module-item-text']/text()")[0]
			sid = a.xpath(".//@href")[0]
			sid = self.regStr(sid,"/voddetail/(\\S+).html")
			videos.append({
				"vod_id":sid,
				"vod_name":name,
				"vod_pic":pic,
				"vod_remarks":mark
			})

		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 9999
		result['limit'] = 90
		result['total'] = 999999
		return result
	
	def detailContent(self,array):
		tid = array[0]
		url = 'https://www.moguys.xyz/voddetail/{0}.html'.format(tid)
		rsp = self.fetch(url,self.headerp)
		root = self.html(rsp.text)
		node = root.xpath("//div[@class='video-info']")[0]
		pic = node.xpath("//div[@class='video-cover']/div/div/img/@data-src")[0]
		title = node.xpath('.//h1/text()')[0]
		detail = node.xpath("//div[@class='video-info-item video-info-content vod_content']/span/text()")[0]
		vod = {
			"vod_id":tid,
			"vod_name":title,
			"vod_pic":pic,
			"type_name":"",
			"vod_year":"",
			"vod_area":"",
			"vod_remarks":"",
			"vod_actor":"",
			"vod_director":"",
			"vod_content":detail
		}

		infoArray = node.xpath(".//div[@class='video-info-main']/div")
		for info in infoArray:
			content = info.xpath('string(.)')
			if content.startswith('类型'):
				vod['type_name'] = content
			# if content.startswith('年份'):
			# 	vod['vod_year'] = content
			# if content.startswith('地区'):
			# 	vod['vod_area'] = content
			# if content.startswith('更新'):
			# 	vod['vod_remarks'] = content.replace('\n','').replace('\t','')
			if content.startswith('主演'):
				vod['vod_actor'] = content.replace('\n','').replace('\t','')
			if content.startswith('导演'):
				vod['vod_director'] = content.replace('\n','').replace('\t','')
			# if content.startswith('剧情'):
			# 	vod['vod_content'] = content.replace('\n','').replace('\t','')

		vod_play_from = '$$$'
		playFrom = []
		vodHeader = root.xpath("//div[@class='module-tab-content']/div/span/text()")
		for v in vodHeader:
			playFrom.append(v)
		vod_play_from = vod_play_from.join(playFrom)
		
		vod_play_url = '$$$'
		playList = []
		vodList = root.xpath("//div[@class='scroll-content']")
		for vl in vodList:
			vodItems = []
			aList = vl.xpath('./a')
			for tA in aList:
				href = tA.xpath('./@href')[0]
				name = tA.xpath('./span/text()')[0]
				tId = self.regStr(href,'/vodplay/(\\S+).html')
				vodItems.append(name + "$" + tId)
			joinStr = '#'
			joinStr = joinStr.join(vodItems)
			playList.append(joinStr)
		vod_play_url = vod_play_url.join(playList)

		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list':[
				vod
			]
		}
		return result

	def searchContent(self,key,quick):		
		url = 'https://www.moguys.xyz/index.php/ajax/suggest?mid=1&wd={0}'.format(key)
		# getHeader()
		rsp = self.fetch(url,self.headerp)
		jo = json.loads(rsp.text)
		result = {}
		jArray = []
		if int(jo['total']) > 0:
			for j in jo['list']:
				jArray.append({
					"vod_id": j['id'],
					"vod_name": j['name'],
					"vod_pic": j['pic'],
					"vod_remarks": ""
				})
		result = {
			'list':jArray
		}
		return result

	config = {
		"filter": {"1": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "恐怖", "v": "恐怖"}, {"n": "动作", "v": "动作"}, {"n": "科幻", "v": "科幻"}, {"n": "剧情", "v": "剧情"}, {"n": "战争", "v": "战争"}, {"n": "警匪", "v": "警匪"}, {"n": "犯罪", "v": "犯罪"}, {"n": "动画", "v": "动画"}, {"n": "奇幻", "v": "奇幻"}, {"n": "冒险", "v": "冒险"}, {"n": "恐怖", "v": "恐怖"}, {"n": "悬疑", "v": "悬疑"}, {"n": "惊悚", "v": "惊悚"}, {"n": "青春", "v": "青春"}, {"n": "情色", "v": "情色"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "欧美", "v": "欧美"}, {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"}, {"n": "泰国", "v": "泰国"}, {"n": "印度", "v": "印度"}, {"n": "俄罗斯", "v": "俄罗斯"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "英语", "v": "英语"}, {"n": "韩语", "v": "韩语"}, {"n": "日语", "v": "日语"}, {"n": "法语", "v": "法语"}, {"n": "泰语", "v": "泰语"}, {"n": "德语", "v": "德语"}, {"n": "印度语", "v": "印度语"}, {"n": "国语", "v": "国语"}, {"n": "粤 语", "v": "粤语"}, {"n": "俄语", "v": "俄语"}, {"n": "西班牙语", "v": "西班牙语"}, {"n": "意大利语", "v": "意大利语"}, {"n": "其它", "v": "其它"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "2": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "剧 情", "v": "剧情"}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "动作", "v": "动作"}, {"n": "悬疑", "v": "悬疑"}, {"n": "恐怖", "v": "恐怖"}, {"n": "奇幻", "v": "奇幻"}, {"n": "惊悚", "v": "惊悚"}, {"n": "犯罪", "v": "犯罪"}, {"n": "科幻", "v": "科幻"}, {"n": "音乐", "v": "音乐"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "英语", "v": "英语"}, {"n": "法语", "v": "法语"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "3": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "剧情", "v": "剧情"}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "动 作", "v": "动作"}, {"n": "悬疑", "v": "悬疑"}, {"n": "恐怖", "v": "恐怖"}, {"n": "奇幻", "v": "奇幻"}, {"n": "惊悚", "v": "惊悚"}, {"n": "犯罪", "v": "犯罪"}, {"n": "科幻", "v": "科幻"}, {"n": "音乐", "v": "音乐"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "4": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "剧情", "v": "剧情"}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "动作", "v": "动作"}, {"n": "悬疑", "v": "悬疑"}, {"n": "恐怖", "v": "恐怖"}, {"n": "奇幻", "v": "奇幻"}, {"n": "惊悚", "v": "惊悚"}, {"n": "犯罪", "v": "犯罪"}, {"n": "科幻", "v": "科幻"}, {"n": "音乐", "v": "音乐"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "5": [{"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "6": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "情感", "v": "情感"}, {"n": "科幻", "v": "科幻"}, {"n": "热血", "v": "热血"}, {"n": "推理", "v": " 推理"}, {"n": "搞笑", "v": "搞笑"}, {"n": "冒险", "v": "冒险"}, {"n": "萝莉", "v": "萝莉"}, {"n": "校园", "v": "校园"}, {"n": "动作", "v": "动作"}, {"n": "机战", "v": "机战"}, {"n": "运动", "v": "运动"}, {"n": "战争", "v": "战争"}, {"n": " 少年", "v": "少年"}, {"n": "少女", "v": "少女"}, {"n": "社会", "v": "社会"}, {"n": "原创", "v": "原创"}, {"n": "亲子", "v": "亲子"}, {"n": "益智", "v": "益智"}, {"n": "励志", "v": "励志"}, {"n": "其他", "v": "其他"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "国产", "v": "国产"}, {"n": "日本", "v": "日本"}, {"n": "欧美", "v": "欧美"}, {"n": "其他", "v": "其他"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "日语", "v": "日语"}, {"n": "英语", "v": "英语"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}]}
	}
	headera = {
		    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
	}
	headerp={
		    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
		    "referer": "https://www.moguys.xyz/"
	}
	def playerContent(self,flag,id,vipFlags):
		result = {}
		url = 'https://www.moguys.xyz/vodplay/{0}.html'.format(id)
		rsp = self.fetch(url,self.headerp)
		root = self.html(rsp.text)
		scripts = root.xpath("//script/text()")
		hdt='{0}'.format(root.xpath("//title/text()")[0])
		hdta=self.regStr(hdt,"(.+?)-")
		jo = {}
		for script in scripts:
			if(script.startswith("var player_")):
				target = script[script.index('{'):]
				jo = json.loads(target)
				break;
		# src="(\S+url=)
		# playerConfig = self.config['player']
		# if jo['from'] in self.config['player']:
		# 	playerConfig = self.config['player'][jo['from']]
		# 	parseUrl = playerConfig['pu'] + jo['url']
		nextUrl = '{0}'.format(jo['link_next'])
		if len(nextUrl)>0:
			nexUrl = 'https://www.moguys.xyz'+'{0}'.format(jo['link_next'])
		else:
			nexUrl=''
		parseUrl = '{0}'.format(jo['url'])+'&next='+nexUrl+'&title='+hdta+'&thumb=undefined'
		parseMid = urllib.parse.quote(parseUrl,safe=";/?:@&=+$,")
		parseMd5 = hashlib.md5(parseMid.encode(encoding='UTF-8')).hexdigest()
		realUrl = 'https://json.moguys.work/json/video.php?f='+parseMd5+'.m3u8'
		#scriptRsp = self.fetch(scriptUrl,self.headerp)
		#sroot=self.html(scriptRsp.text)
		#srsCrp=sroot.xpath("//script/text()")[0].strip()
		#parseUrl=self.regStr(srsCrp,"'(.+?)'")
		#realUrl=str(base64.b16decode(parseUrl[::-1]),'utf-8')
		#finaUrl=realUrl[:math.floor((len(realUrl)-7)/2)] + realUrl[-(math.ceil((len(realUrl)-7)/2)):]
		#realUrl='https://media-zjhz-fy-home.zj6oss.ctyunxs.cn/FAMILYCLOUD/b9f9fe26-e272-4e80-8a29-6bf347d86736.mp4?response-content-disposition=attachment%3Bfilename%3D%22%E8%B6%85%E5%BC%82%E8%83%BD%E6%97%8F01.mp4%22%3Bfilename*%3DUTF-8%27%27%25E8%25B6%2585%25E5%25BC%2582%25E8%2583%25BD%25E6%2597%258F01.mp4&x-amz-CLIENTNETWORK=UNKNOWN&x-amz-CLOUDTYPEIN=CORP&x-amz-CLIENTTYPEIN=UNKNOWN&Signature=VeqzzHBvui4BKVDnoVVX0jtuAM0%3D&AWSAccessKeyId=0Lg7dAq3ZfHvePP8DKEU&Expires=1692980387&x-amz-limitrate=102400&response-content-type=video/mp4&x-amz-FSIZE=673435019&x-amz-UID=951609026966715&x-amz-UFID=11348317428886573'
		result["parse"] = 0
		result["playUrl"] = realUrl
		result["url"] = realUrl
		result["header"] = ''
		return result
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]

