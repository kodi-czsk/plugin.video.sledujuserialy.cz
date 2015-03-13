# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2012 Libor Zoubek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import urllib2
import re
import cookielib
import util
from provider import ContentProvider
from bs4 import BeautifulSoup


class SledujuserialyContentProvider(ContentProvider):
    def __init__(self, username=None, password=None, filter=None, tmp_dir='.'):
        ContentProvider.__init__(self, 'sledujuserialy.cz', 'http://www.sledujuserialy.cz', username, password, filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['resolve', 'categories', 'download']

    def parse_page(self, url=''):
        return BeautifulSoup(util.request(self._url(url)))

    def categories(self):
        result = []
        for series in self.parse_page().select('#seznam_vyber .menu_vyber .menu_click'):
            url = None
            if series.a:
                url = series.a.get('href')
            item = self.dir_item()
            item['title'] = series.text.encode('utf-8').strip('» ')
            item['url'] = url if url else '/'
            result.append(item)
        return result

    def list(self, url):
        if url.count('/') > 1:
            return self.list_episodes(url)
        return self.list_seasons(url)

    def list_seasons(self, url):
        result = []
        for season in self.parse_page(url).select('.levy_blok .serie'):
            item = self.dir_item()
            item['title'] = season.text
            item['url'] = re.search(r'\'([^\']*)\'', season.get('onclick')).group(1)
            result.append(item)
        return result

    def list_episodes(self, url):
        result = []
        has_next = True
        while has_next:
            tree = self.parse_page(url)
            for episode in tree.select('.pravy_blok .uvodni_video'):
                item = self.video_item()
                item['title'] = episode.a.img.get('title')
                item['url'] = episode.a.get('href')
                item['img'] = self._url(re.search(r'url\(([^\)]+)\)', episode.get('style')).group(1))
                result.append(item)
            for next_page in tree.select('.pravy_blok .strankovanicko .strank_bg.vice_pad a'):
                if next_page.get('title').encode('utf-8') == 'Dále':
                    url = next_page.get('href')
                    has_next = True
                    break
                has_next = False
        result.reverse()
        return result

    def resolve(self, item, captcha_cb=None, select_cb=None):
        streams = []
        for stream in self.parse_page(item['url']).select('.pravy_blok .posun_video div')[0].find_all(
                ['embed', 'object', 'iframe']):
            src = stream.get('src')
            if src:
                streams.append(src)
            data = stream.get('data')
            if data:
                streams.append(data)
        result = self.findstreams('\n'.join(streams), ['(?P<url>[^\n]+)'])
        if len(result) == 1:
            return result[0]
        elif len(result) > 1 and select_cb:
            return select_cb(result)
        return None
