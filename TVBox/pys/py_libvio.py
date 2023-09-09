# coding=utf-8
# !/usr/bin/python
import sys

sys.path.append('..')
from base.spider import Spider
import json


class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "Libvio"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "电影": "1",
            "剧集": "2",
            "动漫": "4",
            "即将上线": "27",
            "日韩剧": "15",
            "欧美剧": "16"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })

        result['class'] = classes
        if (filter):
            result['filters'] = self.config['filter']
        return result

    def homeVideoContent(self):
        rsp = self.fetch("https://www.libvio.pro")
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//div[@class='stui-pannel__bd']/ul/li/div/a")

        videos = []
        for a in aList:
            name = a.xpath('./@title')[0]
            pic = a.xpath('./@data-original')[0]
            mark = a.xpath("./span[2]/text()")[0]
            sid = a.xpath("./@href")[0]
            sid = self.regStr(sid, "/detail/(\\d+).html")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result = {
            'list': videos
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
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
        url = 'https://www.libvio.pro/show/{0}.html'.format(suffix)
        print(url)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//div[@class='stui-pannel__bd clearfix']/ul/li/div/a")
        videos = []
        for a in aList:
            name = a.xpath('./@title')[0]
            pic = a.xpath('./@data-original')[0]
            mark = a.xpath("./span[2]/text()")[0]
            sid = a.xpath("./@href")[0]
            sid = self.regStr(sid, "/detail/(\\d+).html")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })

        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'https://www.libvio.pro/detail/{0}.html'.format(tid)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        node = root.xpath("//div[@class='stui-pannel__bd']")[0]
        pic = node.xpath(".//img/@data-original")[0]
        title = node.xpath('.//h1/text()')[0]
        detail = node.xpath(".//span[@class='detail-content']/text()")[0]
        douban = node.xpath(".//span[@class='douban']/text()")[0]

        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_douban_score": format(douban.rstrip("分")),
            "vod_content": detail
        }

        infoArray = node.xpath(".//div[@class='stui-content__detail']/p")
        for info in infoArray:
            content = info.xpath('string(.)')
            if content.startswith('类型'):
                vod['type_name'] = content
            if content.startswith('主演'):
                vod['vod_actor'] = content.replace('\n', '').replace('\t', '')
            if content.startswith('导演'):
                vod['vod_director'] = content.replace('\n', '').replace('\t', '')

        vod_play_from = '$$$'
        playFrom = []
        vodHeader = root.xpath("//div[@class='stui-pannel__head clearfix']/h3/text()")
        for v in vodHeader:
            playFrom.append(v)
        vod_play_from = vod_play_from.join(playFrom)

        vod_play_url = '$$$'
        playList = []
        vodList = root.xpath("//div[@class='stui-vodlist__head']")
        for vl in vodList:
            vodItems = []
            aList = vl.xpath('./ul/li/a')
            for tA in aList:
                href = tA.xpath('./@href')[0]
                name = tA.xpath('./text()')[0]
                tId = self.regStr(href, '/play/(\\S+).html')
                vodItems.append(name + "$" + tId)
            joinStr = '#'
            joinStr = joinStr.join(vodItems)
            playList.append(joinStr)
        vod_play_url = vod_play_url.join(playList)

        vod['vod_play_from'] = vod_play_from
        vod['vod_play_url'] = vod_play_url

        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        url = 'https://www.libvio.pro/index.php/ajax/suggest?mid=1&wd={0}'.format(key)
        # getHeader()
        rsp = self.fetch(url,headers=self.header)
        jo = json.loads(rsp.text)
        result = {}
        jArray = []
        if jo['total'] > 0:
            for j in jo['list']:
                jArray.append({
                    "vod_id": j['id'],
                    "vod_name": j['name'],
                    "vod_pic": j['pic'],
                    "vod_remarks": ""
                })
        result = {
            'list': jArray
        }
        return result

    config = {
        "player":{"aliyunline3":{"show":"bd3播放","des":"","ps":"0","parse":""},"line405":{"show":"hd播放","des":"更多极速线路请访问app","ps":"0","parse":""},"line500":{"show":"hd3播放","des":"","ps":"0","parse":""},"line400":{"show":"hd2播放","des":"","ps":"0","parse":""},"aliyunline":{"show":"bd播放","des":"","ps":"0","parse":""},"aliyunline2":{"show":"bd2播放","des":"","ps":"0","parse":""},"aliyunpan":{"show":"ai","des":"","ps":"0","parse":""},"tianyi":{"show":"bd3播放","des":"","ps":"0","parse":""},"tianyi_625":{"show":"bd4播放","des":"","ps":"0","parse":""},"ali":{"show":"ai播放","des":"","ps":"0","parse":""},"line407":{"show":"line400","des":"","ps":"0","parse":""},"line408":{"show":"line408","des":"","ps":"0","parse":""},"p300":{"show":"line300","des":"","ps":"0","parse":""},"p301":{"show":"line301","des":"","ps":"0","parse":""},"duoduozy":{"show":"line100","des":"","ps":"0","parse":""},"line402-日语":{"show":"line402","des":"","ps":"0","parse":""},"line401":{"show":"line401","des":"","ps":"0","parse":""},"iframe296":{"show":"line296","des":"","ps":"0","parse":""},"iframe297":{"show":"line297","des":"","ps":"0","parse":""},"iframe307":{"show":"line307","des":"","ps":"0","parse":""},"iframe308":{"show":"line308","des":"","ps":"0","parse":""},"iframe309":{"show":"line309","des":"","ps":"0","parse":""},"line301":{"show":"line333","des":"","ps":"0","parse":""},"line302":{"show":"line302","des":"","ps":"0","parse":""},"iframe268":{"show":"line268","des":"","ps":"0","parse":""},"iframe290":{"show":"line290","des":"","ps":"0","parse":""},"iframe291":{"show":"line291","des":"","ps":"0","parse":""},"line409":{"show":"line409","des":"","ps":"0","parse":""},"banquan":{"show":"已下架","des":"","ps":"0","parse":""},"iframe261":{"show":"line261","des":"","ps":"0","parse":""},"iframe265":{"show":"line265","des":"","ps":"0","parse":""},"iframe278":{"show":"line278","des":"","ps":"0","parse":""},"iframe306":{"show":"line306","des":"","ps":"0","parse":""},"iframe317":{"show":"line317","des":"","ps":"0","parse":""},"iframe257":{"show":"line257","des":"","ps":"0","parse":""},"iframe263":{"show":"line263","des":"","ps":"0","parse":""},"iframe258":{"show":"line258","des":"","ps":"0","parse":""},"iframe267":{"show":"line267","des":"","ps":"0","parse":""},"iframe":{"show":"line200","des":"","ps":"0","parse":""},"iframe262":{"show":"line262","des":"","ps":"0","parse":""},"iframe266":{"show":"line266","des":"","ps":"0","parse":""},"line406":{"show":"line406","des":"","ps":"0","parse":""},"dplayer3":{"show":"播放线路3","des":"","ps":"0","parse":""},"dplayer2":{"show":"播放线路2","des":"","ps":"0","parse":""},"dplayer":{"show":"播放线路1","des":"","ps":"0","parse":""},"xunlei1":{"show":"百度云盘","des":"","ps":"0","parse":""},"aliyun":{"show":"阿里云盘","des":"","ps":"0","parse":""},"xunlei2":{"show":"迅雷云盘","des":"","ps":"0","parse":""},"yc":{"show":"隐藏","des":"","ps":"0","parse":""},"line1080":{"show":"line1080","des":"","ps":"0","parse":""},"yr":{"show":"libvio","des":"","ps":"0","parse":""},"app":{"show":"lineapp","des":"","ps":"0","parse":""},"kuake":{"show":"视频下载 (夸克网盘)","des":"","ps":"0","parse":""},"zanwu":{"show":"暂无资源","des":"","ps":"0","parse":""}},
        "filter":{"1":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"爱情","v":"爱情"},{"n":"恐怖","v":"恐怖"},{"n":"动作","v":"动作"},{"n":"科幻","v":"科幻"},{"n":"剧情","v":"剧情"},{"n":"战争","v":"战争"},{"n":"警匪","v":"警匪"},{"n":"犯罪","v":"犯罪"},{"n":"动画","v":"动画"},{"n":"奇幻","v":"奇幻"},{"n":"武侠","v":"武侠"},{"n":"冒险","v":"冒险"},{"n":"枪战","v":"枪战"},{"n":"恐怖","v":"恐怖"},{"n":"悬疑","v":"悬疑"},{"n":"惊悚","v":"惊悚"},{"n":"经典","v":"经典"},{"n":"青春","v":"青春"},{"n":"文艺","v":"文艺"},{"n":"微电影","v":"微电影"},{"n":"古装","v":"古装"},{"n":"历史","v":"历史"},{"n":"运动","v":"运动"},{"n":"农村","v":"农村"},{"n":"儿童","v":"儿童"},{"n":"网络电影","v":"网络电影"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"中国大陆"},{"n":"香港","v":"中国香港"},{"n":"台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"意大利","v":"意大利"},{"n":"西班牙","v":"西班牙"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":"by","name":"排序","value":[{"n":"默认","v":""},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],"2":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"战争","v":"战争"},{"n":"青春偶像","v":"青春偶像"},{"n":"喜剧","v":"喜剧"},{"n":"家庭","v":"家庭"},{"n":"犯罪","v":"犯罪"},{"n":"动作","v":"动作"},{"n":"奇幻","v":"奇幻"},{"n":"剧情","v":"剧情"},{"n":"历史","v":"历史"},{"n":"经典","v":"经典"},{"n":"乡村","v":"乡村"},{"n":"情景","v":"情景"},{"n":"商战","v":"商战"},{"n":"网剧","v":"网剧"},{"n":"其他","v":"其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"中国大陆"},{"n":"台湾","v":"中国台湾"},{"n":"香港","v":"中国香港"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"美国","v":"美国"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":"by","name":"排序","value":[{"n":"默认","v":""},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],"3":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"情感","v":"情感"},{"n":"访谈","v":"访谈"},{"n":"播报","v":"播报"},{"n":"旅游","v":"旅游"},{"n":"音乐","v":"音乐"},{"n":"美食","v":"美食"},{"n":"纪实","v":"纪实"},{"n":"曲艺","v":"曲艺"},{"n":"生活","v":"生活"},{"n":"游戏互动","v":"游戏互动"},{"n":"财经","v":"财经"},{"n":"求职","v":"求职"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"内地","v":"内地"},{"n":"港台","v":"港台"},{"n":"日韩","v":"日韩"},{"n":"欧美","v":"欧美"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":"by","name":"排序","value":[{"n":"默认","v":""},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],"4":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"科幻","v":"科幻"},{"n":"热血","v":"热血"},{"n":"推理","v":"推理"},{"n":"搞笑","v":"搞笑"},{"n":"冒险","v":"冒险"},{"n":"萝莉","v":"萝莉"},{"n":"校园","v":"校园"},{"n":"动作","v":"动作"},{"n":"机战","v":"机战"},{"n":"运动","v":"运动"},{"n":"战争","v":"战争"},{"n":"少年","v":"少年"},{"n":"少女","v":"少女"},{"n":"社会","v":"社会"},{"n":"原创","v":"原创"},{"n":"亲子","v":"亲子"},{"n":"益智","v":"益智"},{"n":"励志","v":"励志"},{"n":"其他","v":"其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"中国","v":"中国"},{"n":"日本","v":"日本"},{"n":"欧美","v":"欧美"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":"by","name":"排序","value":[{"n":"默认","v":""},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],"15":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"爱情","v":"爱情"},{"n":"恐怖","v":"恐怖"},{"n":"动作","v":"动作"},{"n":"科幻","v":"科幻"},{"n":"剧情","v":"剧情"},{"n":"战争","v":"战争"},{"n":"警匪","v":"警匪"},{"n":"犯罪","v":"犯罪"},{"n":"动画","v":"动画"},{"n":"奇幻","v":"奇幻"},{"n":"武侠","v":"武侠"},{"n":"冒险","v":"冒险"},{"n":"枪战","v":"枪战"},{"n":"恐怖","v":"恐怖"},{"n":"悬疑","v":"悬疑"},{"n":"惊悚","v":"惊悚"},{"n":"经典","v":"经典"},{"n":"青春","v":"青春"},{"n":"文艺","v":"文艺"},{"n":"微电影","v":"微电影"},{"n":"古装","v":"古装"},{"n":"历史","v":"历史"},{"n":"运动","v":"运动"},{"n":"农村","v":"农村"},{"n":"儿童","v":"儿童"},{"n":"网络电影","v":"网络电影"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"中国大陆"},{"n":"香港","v":"中国香港"},{"n":"台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"意大利","v":"意大利"},{"n":"西班牙","v":"西班牙"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":"by","name":"排序","value":[{"n":"默认","v":""},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],"16":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"爱情","v":"爱情"},{"n":"恐怖","v":"恐怖"},{"n":"动作","v":"动作"},{"n":"科幻","v":"科幻"},{"n":"剧情","v":"剧情"},{"n":"战争","v":"战争"},{"n":"警匪","v":"警匪"},{"n":"犯罪","v":"犯罪"},{"n":"动画","v":"动画"},{"n":"奇幻","v":"奇幻"},{"n":"武侠","v":"武侠"},{"n":"冒险","v":"冒险"},{"n":"枪战","v":"枪战"},{"n":"恐怖","v":"恐怖"},{"n":"悬疑","v":"悬疑"},{"n":"惊悚","v":"惊悚"},{"n":"经典","v":"经典"},{"n":"青春","v":"青春"},{"n":"文艺","v":"文艺"},{"n":"微电影","v":"微电影"},{"n":"古装","v":"古装"},{"n":"历史","v":"历史"},{"n":"运动","v":"运动"},{"n":"农村","v":"农村"},{"n":"儿童","v":"儿童"},{"n":"网络电影","v":"网络电影"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"美国","v":"美国"},{"n":"英国","v":"英国"},{"n":"德国","v":"德国"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":"by","name":"排序","value":[{"n":"默认","v":""},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]}
    }
    header = {
        "Referer": "https://www.libvio.pro",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    def playerContent(self, flag, id, vipFlags):
        result = {}
        url = 'https://www.libvio.pro/play/{0}.html'.format(id)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        scripts = root.xpath("//script/text()")
        jo = {}
        for script in scripts:
            if (script.startswith("var player_")):
                target = script[script.index('{'):]
                jo = json.loads(target)
                break;
        nid = str(jo['nid'])
        scriptUrl = 'https://www.libvio.pro/static/player/{0}.js'.format(jo['from'])
        scriptRsp = self.fetch(scriptUrl)
        parseUrl = self.regStr(scriptRsp.text, 'src="(\\S+url=)')
        if len(parseUrl) > 0:
            path = jo['url'] + '&next=' + jo['link_next'] + '&id=' + jo['id'] + '&nid=' + nid
            parseRsp = self.fetch(parseUrl + path,headers=self.header)
            realUrl = self.regStr(parseRsp.text, "(?<=urls\\s=\\s').*?(?=')", 0)
            if len(realUrl) > 0:
                result["parse"] = 0
                result["playUrl"] = ""
                result["url"] = realUrl
                result["header"] = ""
            else:
                result["parse"] = 1
                result["playUrl"] = ""
                result["url"] = jo['url']
                result["header"] = json.dumps(self.header)
        return result

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        return [200, "video/MP2T", action, ""]
