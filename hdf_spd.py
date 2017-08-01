# -*- coding:utf-8 -*-
import time
import pymysql
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

base_url = 'http://www.haodf.com/yiyuan/all/list.htm'

db = pymysql.connect('localhost', 'root', 'a555554444', 'DOCTOR', charset='utf8')
# 使用cursor()方法获取操作游标
cursor = db.cursor()

# 使用 execute() 方法执行 SQL，如果表存在则删除
cursor.execute("DROP TABLE IF EXISTS DOCTOR")
# 使用预处理语句创建表
sql = """CREATE TABLE DOCTOR (
            DOCTOR_ID INT NOT NULL AUTO_INCREMENT,
            DOCTOR_NAME CHAR(100),
            TITLE CHAR(100),
            DOCTOR_HREF CHAR(200),
            DEPARTMENT CHAR(100),
            HOSPITAL_NAME CHAR(100),
            HOSPITAL_LEVEL CHAR(50),
            CITY CHAR(100),
            PROVINCE CHAR(100),
            PRIMARY KEY (DOCTOR_ID)
            ) ENGINE=InnoDB;"""

cursor.execute(sql)
# cursor.execute('INSERT INTO DOCTOR(ID) VALUES(0)')
db.close()

def get_page(url):
    ua = UserAgent()
    header = {"User-Agent": ua.random}
    r = requests.get(url, headers=header)
    print(r.status_code)
    return r.content

#解析地区省市页面
def parse_province(province_name, url):
    soup = BeautifulSoup(get_page(url), 'html5lib')
    m_ctt_green_s = soup.select('div[class="m_ctt_green"]')
    for m_ctt_green in m_ctt_green_s:
        #市级名称
        city = m_ctt_green.previous_sibling.previous_sibling.string
        hospitals = m_ctt_green.select('a')
        for hospital in hospitals:
            #医院链接
            hospital_href = 'http://www.haodf.com' + hospital['href']
            #医院简称
            hospital_name1 = hospital.string
            yield [hospital_name1, hospital_href, province_name, city]

#解析科室列表页面
def parse_departmentlist(url):
    department_list_soup = BeautifulSoup(get_page(url), 'html5lib')
    department = department_list_soup.select('a[class="blue"]')[:-1]
    for a in department:
        department_name = a.string
        department_href = a['href']
        yield department_name, department_href

#解析科室页面,获取医生主页
def parse_department(url):
    department_soup = BeautifulSoup(get_page(url), 'html5lib')
    doctor_soup = department_soup.select('td[class="tdnew_a"] > li')
    try:
        next_href = department_soup.find('div', class_='p_bar').find('a', text='下一页')['href']
    except:
        next_href = 0

    if next_href:
        yield from parse_department(next_href)

    for li in doctor_soup:
        doctor_name = li.a['title']
        doctor_title = li.p.string
        doctor_href = li.a["href"]
        yield doctor_name, doctor_title, doctor_href

#保存至数据库
def add_to_sql(doctor_name, title, doctor_href, department, hospital_name, hospital_level, city, province):
    print(doctor_name, title, doctor_href, department, hospital_name, hospital_level, city, province)
    # 打开数据库连接
    db = pymysql.connect('localhost', 'root', 'a555554444', 'DOCTOR', charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = '''INSERT INTO DOCTOR(DOCTOR_NAME,
    TITLE,
    DOCTOR_HREF,
    DEPARTMENT,
    HOSPITAL_NAME,
    HOSPITAL_LEVEL,
    CITY,
    PROVINCE)
VALUES('%s',
    '%s',
    '%s',
    '%s',
    '%s',
    '%s',
    '%s',
    '%s');''' % (doctor_name, title.strip(), doctor_href, department, hospital_name, hospital_level, city, province)

    try:
        # 执行sql语句
        cursor.execute(sql)
        # 执行sql语句
        db.commit()
        print('保存成功！')
    except:
        # 发生错误时回滚
        db.rollback()
        print('数据未录入！！！！！')
    # 关闭数据库连接
    db.close()

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
        print(url)
        city = hospital[3]
        page = get_page(hospital[1])
        hospital_soup = BeautifulSoup(page, 'lxml')
        # 获取医院全名
        hospital_name = hospital_soup.select('div[id="ltb"] span a')[0].string
        hospital.append(hospital_name)
        # 获取医院等级
        p = hospital_soup.select('div[id="contentA"] div[class="toptr"] p')[0]
        if '(' in p.text:
            pattern = re.compile('\((.*)\)')
            hospital_level = pattern.findall(p.text)[0]
            hospital.append(hospital_level)
        else:
            hospital_level = ''
            hospital.append(hospital_level)
        #科室列表页面url
        department_url = hospital[1][:-4] + '/keshi.htm'
        print(department_url)
        #遍历科室列表页面
        for department_name, department_href in parse_departmentlist(department_url):
            #遍历医生列表页面
            for doctor in parse_department(department_href):
                add_to_sql(doctor[0], doctor[1], doctor[2], department_name, hospital_name, hospital_level, city, province)
