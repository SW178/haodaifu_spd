# -*- coding:utf-8 -*-
import time
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

base_url = 'http://www.haodf.com/yiyuan/all/list.htm'

def get_page(url):
    ua = UserAgent()
    header = {"User-Agent": ua.random}
    r = requests.get(url, headers=header)
    print(r.status_code)
    return r.content

#解析地区省市页面
def parse_province(province, url):
    soup = BeautifulSoup(get_page(url), 'lxml')
    m_ctt_green_s = soup.select('div[class="m_ctt_green"]')
    hospital_list = []
    for m_ctt_green in m_ctt_green_s:
        city = m_ctt_green.previous_sibling.previous_sibling.string
        hospitals = m_ctt_green.select('a')
        for hospital in hospitals:
            hospital_href = 'http://www.haodf.com/' + hospital['href']
            hospital_name1 = hospital.string
            hospital_list.append((hospital_name1, hospital_href, province, city))
    return hospital_list


r = get_page(base_url)
soup = BeautifulSoup(r, 'lxml')

province = []
bj = soup.select('div[class="kstl2"]')[0].a.string
bj_href = soup.select('div[class="kstl2"]')[0].a['href']
province.append((bj, bj_href))

#获取各省链接
for kstl in soup.select('div[class="kstl"]'):
    province_name = kstl.a.string
    province_href = kstl.a['href']
    province.append((province_name, province_href))

#遍历各省链接
for province, url in province:
    for hospital in parse_province(province, url):
        page = get_page(hospital[1])
        time.sleep(1)#续1秒！
        hospital_soup = BeautifulSoup(page, 'lxml')
        p = hospital_soup.select('div[id="contentA"] div[class="toptr"] p')[0]
        if p.text.find('('):
            compile = re.compile('.*?\(()\)')
