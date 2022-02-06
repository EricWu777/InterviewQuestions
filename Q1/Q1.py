import configparser
import os
import re
import pandas as pd
import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_data_by_configparser():
    config = configparser.ConfigParser()
    path =os.getcwd() 
    new_path = path + '/user.cfg'
    config.read(new_path)
    mysql_config = config['mysql']
    
    return  mysql_config

driverPath = '/Users/ericwu/Downloads/chromedriver 2'
driver = webdriver.Chrome(driverPath)
url = 'http://www.kingbus.com.tw/ticketRoute.php'
driver.get(url)
#選擇起站地區：台北
driver.find_element_by_xpath('//body[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[1]/select[1]/option[3]').click()
#確保上車站欄位有臺北轉運站
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/select[1]/option[2]')))
#選擇上車站：臺北轉運站
driver.find_element_by_xpath('/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]/select[1]/option[2]').click()
#確保下車站欄位有朝馬轉運站
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[3]/select[1]/option[2]')))
#選擇下車站：朝馬轉運站
driver.find_element_by_xpath('/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[3]/select[1]/option[2]').click()
#點擊查詢
driver.find_element_by_xpath('/html[1]/body[1]/div[1]/div[2]/div[1]/div[2]/input[1]').click()
#將selenium取得的網站資料應用到BeautifulSoup
html_source = driver.page_source
soup = BeautifulSoup(html_source, 'lxml')

result = {'route':[], 'description':[]}

for i in range(0, 10):

    li = soup.find(class_ = "routeData").find_all('li')[i]
    li_text = li.find_all('a')[-1].text
    #將text裡的字串做整理，把我們不要的字元清除
    rep = { ' ':'', '\t':'', '\n':''}
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], li_text)
    
    if i>= 9: 

        text_new = text[2:]  #為了避免取到數字

    else:

        text_new = text[1:]

    list_new = text_new.split('\u3000')
    result['route'].append(list_new[0])
    
    if len(list_new) == 3:
        result['description'].append(list_new[1]+list_new[2])
    else:
        result['description'].append(list_new[-1])
    
driver.close()
#做成DataFrame
df_data = pd.DataFrame(result)
print(df_data)

#將路線查詢結果存成CSV檔
df_data.to_csv('./台北轉運站至朝馬轉運站的路線.csv')


mysql_config = get_data_by_configparser()

connection = pymysql.connect(
    host= mysql_config['host'], port = int(mysql_config['port']), 
user = mysql_config['user'], password = mysql_config['password'],db = mysql_config['db']

)
        
    
try:
    cursor = connection.cursor()
    #匯入資料
    # sql_ins = 'INSERT INTO route_line (route, description) VALUES (%s, %s)'
    
    # for i in range(0,10):
    #     cursor.execute(sql_ins,(result['route'][i] , result['description'][i]))
    
    # #確定存入SQL
    # connection.commit()

    #統計route欄位有出現埔里的筆數
    sql_sel = '''SELECT COUNT(route) FROM route_line WHERE route LIKE '%埔里%' '''
    cursor.execute(sql_sel)

    result=cursor.fetchone()
    print('route欄位有出現埔里的筆數:',result[0])


except Exception as ex:

    print("Exception:", ex)

finally:

    connection.close()