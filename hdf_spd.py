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
            yield [hospital_name1, hospital_href, province_name, city]

#解析科室列表页面
def parse_departmentlist(url):
    department_list_soup = BeautifulSoup(get_page(url), 'lxml')
    department = department_list_soup.select('a[class="blue"]')[:-1]
    for a in department:
        department_name = a.string
        department_href = a['href']
        yield department_name, department_href

#解析科室页面,获取医生主页
def parse_department(url):
    department_soup = BeautifulSoup(get_page(url), 'lxml')
    doctor_soup = department_soup.select('td[class="tdnew_a"] > li')
    for li in doctor_soup:
        doctor_name = li.a.string
        doctor_title = li.p.string
        doctor_href = li.a["href"]
        yield doctor_name, doctor_title, doctor_href

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
    #遍历医院
    for hospital in parse_province(province, url):
        page = get_page(hospital[1])
        # time.sleep(1)#续1秒！
        hospital_soup = BeautifulSoup(page, 'lxml')
        # 获取医院全名
        hospital_name = hospital_soup.select('div[id="ltb"] span a')[0].string
        hospital.append(hospital_name)
        # 获取医院等级
        p = hospital_soup.select('div[id="contentA"] div[class="toptr"] p')[0]
        if '(' in p.text:
            pattern = re.compile('\((.*)\)')
            hospital_levle = pattern.findall(p.text)[0]
            hospital.append(hospital_levle)
        else:
            hospital.append('')
        #科室列表页面url
        department_url = hospital[1][:-4] + '/keshi.htm'
        #遍历科室列表页面
        for department_name, department_href in parse_departmentlist(department_url):
            #遍历医生列表页面
            for doctor in parse_department(department_href):
                print(doctor)
