# -*- coding: utf-8 -*-
# Russia Today Kodi Video Addon
#
import json
import re
import os
import urllib
import xbmc
import xbmcplugin
import xbmcgui
import HTMLParser
import sys
from .t1mlib import t1mAddon

import datetime
import time

#fix for datatetime.strptime returns None after second use
class proxydt(datetime.datetime):
    def __init__(self, *args, **kwargs):
        super(proxydt, self).__init__(*args, **kwargs)

    @classmethod
    def strptime(cls, date_string, format):
        return datetime(*(time.strptime(date_string, format)[0:6]))

datetime.datetime = proxydt
from datetime import datetime

h = HTMLParser.HTMLParser()
qp  = urllib.quote_plus
uqp = urllib.unquote_plus
UTF8     = 'utf-8'
RTBASE_URL  = 'https://www.rt.com'

class myAddon(t1mAddon):

    def getAddonMenu(self,url,ilist):
        ilist = self.addMenuItem('RT Live','GS', ilist, 'abc' , self.addonIcon, self.addonFanart, None, isFolder=True)
        page = self.getRequest(RTBASE_URL+"/shows/")
        match = re.compile('<li class="card-rows__item.+?src="(http.+?)".+?href="(.+?)">(.+?)<.+?class="link link_disabled".+?>(.+?)</a',re.DOTALL).findall(page)
        for img,url,name,plot in match:
            url = url.strip()
            thumb = img
            fanart = img
            infoList = {}
            name = name.strip()
            infoList['title'] = name
            infoList['mediatype'] = 'tvshow'
            infoList['plot'] = h.unescape(plot.strip().replace('<p>','').replace('</p>','').decode(UTF8))
            ilist = self.addMenuItem(name,'GE', ilist, url, thumb, fanart, infoList, isFolder=True)
        return(ilist)


    def getAddonEpisodes(self,url,ilist):
        page = self.getRequest(RTBASE_URL+url)
        match = re.compile('static-three_med-one">.+?src="(.+?)".+?class="link link_hover" href="(.+?)" >(.+?)<.+?class="card__summary ">(.+?)</.+?date">(.+?)</',re.DOTALL).findall(page)
        for img,url,name,plot,pdate in match:
            thumb = img
            fanart = img
            name = name.strip()
            infoList = {}
            infoList['title'] = name
            infoList['mediatype'] = 'episode'
            infoList['plot'] = h.unescape(plot.strip().replace('<p>','').replace('</p>','').decode(UTF8))
            if pdate:
                infoList['premiered'] = datetime.strptime(pdate.strip(), '%b %d, %Y %H:%M').strftime('%Y-%m-%d')
            ilist = self.addMenuItem(name,'GV', ilist, url, thumb, fanart, infoList, isFolder=False)
        return(ilist)

    def getAddonShows(self,url,ilist):
        rlist = [("https://www.rt.com/on-air/", 'Global'),
                 ("https://www.rt.com/on-air/rt-america-air", 'US'),
                 ("https://www.rt.com/on-air/rt-uk-air", 'UK'),
                 ("https://rtd.rt.com/on-air/", 'Doc'),
                 ("https://actualidad.rt.com/en_vivo2", 'ESP'),
                 ("https://francais.rt.com/en-direct", "FR"),
                 ("https://arabic.rt.com/live/", "ARAB")]
        for url, name in rlist:
            name = name.strip()
            infoList = {}
            infoList['title'] = name
            infoList['mediatype'] = 'episode'
            ilist = self.addMenuItem(name,'GV', ilist, url, self.addonIcon, self.addonFanart, infoList, isFolder=False)
        return(ilist)



    def getAddonVideo(self,url):
        if not url.startswith('http'):
            url = RTBASE_URL + url
        html = self.getRequest(url)
        if 'rtd.rt.com' not in url:
            m = re.compile("file: '(.+?)'",re.DOTALL).search(html)
            if m != None:
                url = m.group(1)
            else:
                m = re.compile('file: "(.+?)"',re.DOTALL).search(html)
                if m != None:
                    url = m.group(1)
                else:
                    m = re.compile('url: "(.+?\.m3u8)"',re.DOTALL).search(html)
                    if m != None:
                        url = m.group(1)
                    else:
                        m = re.compile('<div class="rtcode"><iframe.+?src="(.+?)"', re.DOTALL).search(html)
                        if m != None:
                            url = m.group(1)
                            if not url.startswith('http'):
                                url = 'http:'+url
                            html = self.getRequest(url)
                            m = re.compile('<source src="(.+?)"', re.DOTALL).search(html)
                            if m != None:
                                url = m.group(1)
                            else:
                                return
                        else:
                            m = re.compile('\/\/www.youtube.com\/embed\/(.+?)"', re.DOTALL).search(html)
                            if m != None:
                                url = 'plugin://plugin.video.youtube/play/?video_id=%s' % (m.group(1).split("?")[0])
                            else:
                                return
        else:
            m = re.compile('streams_hls.+?url: "(.+?)"',re.DOTALL).search(html)
            if m != None:
                url = m.group(1)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=url))
