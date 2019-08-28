#!/user/bin/env python
# -*-coding:utf-8-*-
# author:chensong time:2019/8/25

import re
import base64

import requests
from lxml import html
from threading import Thread

headers = {'Cookie': 'MUSID=cubi9f5q4odknsr8kqhlk8ool4; virtual_device_id=223dd6ed77ea6ed4ec315bdcea6bb6cb; pvid=%2Bww%2FhuKbUPxNuKTl%2BFhXUXd7Q5oiFtAQ; sid=cubi9f5q4odknsr8kqhlk8ool4; UM_distinctid=16cd08f362125-03e5fba9aa6ccb-6353160-144000-16cd08f362253f; CNZZDATA1256786412=147158893-1566865632-%7C1566902216'}


class MeiPai:
    def __init__(self, page):
        self.page = page

    def parse_url_ids(self):
        req = requests.get('https://www.meipai.com/home/hot_timeline?page={}&count=12'.format(self.page), headers=headers).text
        url_ids = re.findall('"id":(\d+),"client_id', req)
        return url_ids

    def parse_video_urls(self):
        for url_id in self.parse_url_ids():
            video_urls = 'https://www.meipai.com/media/{}'.format(url_id)
            yield video_urls

    def parse_video_infos(self):
        for video_url in self.parse_video_urls():
            req = requests.get(video_url).text
            selector = html.etree.HTML(req)
            video_data = selector.xpath('//div[@id="detailVideo"]/@data-video')[0]
            title = selector.xpath('//h1/text()')[0].strip()
            user = selector.xpath('//h3[@class="detail-name pa"]/a/text()')[0].strip()
            yield video_data, title, user

    def parse_decode_urls(self):
        decode_urls = self.parse_video_infos()
        for decode_url in decode_urls:
            try:
                # 得到被编码的字符串的前四位
                video_data = decode_url[0][0:4]
                # 反转字符串
                video_data = video_data[::-1]
                # 将字符串转为16进制
                video_num = str(int(video_data, 16))
                # 得到16进制数前两位解析结果
                l_nums = decode_url[0][4 + int(video_num[0]):4 + int(video_num[0]) + int(video_num[1])]
                # 将得到的结果去掉
                url_1 = decode_url[0].replace(l_nums, '')
                # 得到16进制数后两位解析结果并反转
                r_nums = decode_url[0][-int(video_num[2]) + (-1):-int(video_num[2]) + (-1) + (-int(video_num[3])):-1][::-1]
                url_2 = url_1.replace(r_nums, '')
                url_3 = url_2.replace(decode_url[0][0:4], '')
                # 将编码字符串进行解码
                video_urls = base64.urlsafe_b64decode(url_3)
                yield (video_urls.decode(), decode_url[1], decode_url[2])
            except:
                print('{}解析无效'.format(decode_url[0]))

    def save_videos(self):
        for video_url in self.parse_decode_urls():
            req = requests.get(video_url[0]).content
            if req:
                with open('{}_{}.mp4'.format(video_url[1], video_url[2]), 'ab') as f:
                    f.write(req)


if __name__ == '__main__':
    t_threadings = []
    for page in range(1, 11):
        per_page = MeiPai(page)
        t_threading = Thread(target=per_page.save_videos)
        t_threading.start()
        t_threadings.append(t_threading)
    for t_threading in t_threadings:
        t_threading.join()




