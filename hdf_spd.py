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
def parse_province(province_name, url):
    soup = BeautifulSoup(get_page(url), 'lxml')
    m_ctt_green_s = soup.select('div[class="m_ctt_green"]')
    hospital_list = []
    for m_ctt_green in m_ctt_green_s:
        #市级名称
        city = m_ctt_green.previous_sibling.previous_sibling.string
        hospitals = m_ctt_green.select('a')
        for hospital in hospitals:
            #医院链接
            hospital_href = 'http://www.haodf.com/' + hospital['href']
            #医院简称
            hospital_name1 = hospital.string
            hospital_list.append((hospital_name1, hospital_href, province_name, city))
    return hospital_list


r = get_page(base_url)
bj_soup = BeautifulSoup(r, 'lxml')

province = []
bj = bj_soup.select('div[class="kstl2"]')[0].a.string
bj_href = bj_soup.select('div[class="kstl2"]')[0].a['href']
province.append((bj, bj_href))

#获取各省链接
for kstl in bj_soup.select('div[class="kstl"]'):
    province_name = kstl.a.string
    province_href = kstl.a['href']
    province.append((province_name, province_href))

#遍历各省链接
for province, url in province:
    for hospital in parse_province(province, url):
        page = get_page(hospital[1])
        time.sleep(1)#续1秒！
        hospital_soup = BeautifulSoup(page, 'lxml')
        # 获取医院全名
        hospital_name = hospital_soup.select('div[id="ltb"] span a')[0].string
        print(hospital_name)
        # 获取医院等级
        p = hospital_soup.select('div[id="contentA"] div[class="toptr"] p')[0]
        if '(' in p.text:
            pattern = re.compile('\((.*)\)')
            hospital_levle = pattern.findall(p.text)[0]

