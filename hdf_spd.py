# -*- coding:utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

base_url = 'http://www.haodf.com/yiyuan/all/list.htm'

def get_page(url):
    ua = UserAgent()
    header = {"User-Agent": ua.random}
    r = requests.get(url, headers=header)
    r.coding = 'utf-8'
    return r.content

r = get_page(base_url)
soup = BeautifulSoup(r, 'lxml')

province = []
bj = soup.select('div[class="kstl2"]')[0].a.string
bj_href = soup.select('div[class="kstl2"]')[0].a['href']
province.append((bj, bj_href))

for kstl in soup.select('div[class="kstl"]'):
    province_name = kstl.a.string
    province_href = kstl.a['href']
    province.append((province_name, province_href))

print(province)
