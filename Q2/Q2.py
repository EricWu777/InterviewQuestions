import json
import os
import re
import shutil
import threading
import time
import requests
from bs4 import BeautifulSoup


def get_last_page_num(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml') 
    for t in soup.find_all('a'):    
        last_page_num=0
        try:    
            if re.match('最後頁',t['title']):   
                href =  t['href']
                last_page = href.split('=')
                last_page_num =  last_page[-1]
                return int(last_page_num)
        except:
            pass

def get_page_url_list(url):
    page_url_list=[]
    for i in range(1, get_last_page_num(url)+1):
        page_url = url + '&page='+str(i)
        page_url_list.append(page_url)
    return page_url_list

#重整pdf檔案名稱
def get_new_file_name(old_file_name):
    
    if (old_file_name[0]=='0'):
        new_name = old_file_name[3:]
        return  new_name
        
    return  old_file_name

def get_file_url(href):
    
    file_url=''

    if ( href.find('http') == -1 ):
        file_url = 'https://www.ceec.edu.tw' + href
        return file_url
    else:
        file_url = href
        return file_url

#取得檔名年度
def get_year(new_filename):
    file_year=''
    if new_filename[0] == '1':
        file_year = new_filename[:3]
        return file_year
    elif new_filename[0] != '1':
        file_year = new_filename[:2]
        return file_year
  
def get_subject(title, new_filename):
    path = os.getcwd() 
    with open( path + '/resource/subject.json') as f:
        sub = json.load(f)
    sub_keys = list(sub.keys())
    sub_values = list(sub.values())
    
    subject=''
    for key in range(0, len(sub_keys)):
        for i in range(1, len(sub_values[key])):
            if new_filename.find(sub_values[key][i]) != -1:
                subject = sub_keys[key]
                return subject
    if subject =='':
        for sub in range(0, len(sub_keys)-1):
            if title.startswith(sub_values[sub][0]) is True:
                subject = sub_keys[sub]
                return subject
    return subject

def get_subject_bylist():
    path = os.getcwd() 
    with open( path + '/resource/subject.json') as f:
        sub = json.load(f)
    sub_keys = list(sub.keys())
    subj_list = sub_keys[:-1]
    return subj_list

def create_folder_by_year(year):

    path =os.getcwd()
    file_year = str(year)
   
    if (os.path.exists(path+ os.sep + file_year) == False):   
        os.mkdir( path + os.sep + file_year )
    
def create_folder_by_subject(year, subject):
    path =os.getcwd()
    file_year = str(year)
    file_subject = str(subject)
    if (os.path.exists(path + os.sep + file_year + os.sep + file_year +'學年度學科能力測驗-' + file_subject ) == False):
        os.mkdir(path + os.sep + file_year + os.sep + file_year +'學年度學科能力測驗-' + file_subject)     

def create_folder_by_ans():
    path = os.getcwd()
    os.mkdir(path + os.sep + 'ans')

def create_folder_by_exception():
    path = os.getcwd()
    os.mkdir(path + os.sep + 'exception')

def get_path(file_year, file_subject):
    
    path = os.getcwd()
    file_path = path+ os.sep + file_year + os.sep + file_year +'學年度學科能力測驗-' + file_subject
    return file_path    


def download_pdf(file_url, file_path, file_name):

    response = requests.get(file_url)
    file_path = os.path.join(file_path, file_name+ '.pdf')
    with open(file_path, 'wb') as f:
        f.write(response.content)

def copy_file():

    subject_list =get_subject_bylist()
    ans_path = os.getcwd() + os.sep + 'ans'
    filelist = os.listdir(ans_path)
    for i in range(0, len(filelist)):
        for y in range(83, 110):
            if(filelist[i].startswith(str(y)) is True):
                for j in range(0, len(subject_list)): 
                    dest_path = get_path(str(y), subject_list[j])
                    copyname_path = os.getcwd() + os.sep + 'ans' + os.sep + filelist[i]
                    shutil.copy(copyname_path, dest_path)

#subject_list就可以直接從字典取出
subject_list = get_subject_bylist()
# 判斷（取得學年度、學科科目（包含例外與答案）（7類）)
#create folder（若條件沒有符合的資料夾，則建立一個folder)(若條件有符合資料夾，則放入)
# get pdf_dir
# get file_url
# download_pdf(file_url, pdf_dir)

#開始測量時間點
start = time.time()

#先建立一個放入ans的folder
create_folder_by_ans()
#建立一個放入例外處理的folder(subject是'')
create_folder_by_exception()
url = 'https://www.ceec.edu.tw/xmfile?xsmsid=0J052424829869345634'

page_last_num = get_last_page_num(url)

page = requests.get(url)

url_list = get_page_url_list(url)

threads =[]
thread_num = 0
error_record = {}
for url in url_list:

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml') 
    text = soup.find_all('a', class_="file_ext file_pdf")    
    for t in text:
        
        title=t['title']
        href =t['href']

        new_filename = get_new_file_name(title)
        print("New_filename:::::", new_filename)

        file_url = get_file_url(href)
        file_year = get_year(new_filename)
        file_subject = get_subject(title, new_filename)
        #這邊的數字可以用command line arguments的方法
        if int(file_year) >=110 or int(file_year)<83 :
            next       
        else:
            if file_subject == '':
                file_path = os.getcwd() + os.sep + 'exception'
                retries = 0
                while True:
                    try:
                        threads.append(threading.Thread(target=download_pdf, args=(file_url, file_path, new_filename) ))
                        threads[thread_num].start()
                        break
                    except ConnectionError:
                        if retries < 3:
                            retries+=1
                        else:
                            error_msg = ConnectionError.args[0]
                            error_record[title]= error_msg

            elif file_subject !='答案':
                create_folder_by_year(file_year)
                create_folder_by_subject(file_year, file_subject)
                file_path = get_path(file_year, file_subject)
                while True:
                    try:
                        threads.append(threading.Thread(target=download_pdf, args=(file_url, file_path, new_filename) ))
                        threads[thread_num].start()
                        break
                    except ConnectionError:
                        if retries < 3:
                            retries+=1
                        else:
                            error_msg = ConnectionError.args[0]
                            error_record[title]= error_msg


            elif file_subject == '答案' :

                file_path = os.getcwd() + os.sep + 'ans'
                while True:
                    try:
                        threads.append(threading.Thread(target=download_pdf, args=(file_url, file_path, new_filename) ))
                        threads[thread_num].start()
                        break
                    except ConnectionError:
                        if retries < 3:
                            retries+=1
                        else:
                            error_msg = ConnectionError.args[0]
                            error_record[title]= error_msg
            time.sleep(0.1)
            thread_num +=1
    
for td in threads:
    print(td)
    td.join()

print('Error_record:',error_record)

copy_file()

#刪除ans檔案
path_ans = os.getcwd() + '/ans'
shutil.rmtree(path_ans)

#結束測量時間點
end = time.time()
print("執行時間： %f  秒" % (end-start))

#執行時間： 50.93 秒
