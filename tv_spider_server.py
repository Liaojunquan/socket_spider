# -*- coding: utf-8 -*-
import time
import requests
from random import randint
import re
from lxml import etree
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import platform
from socket import *
import threading
import signal
from multiprocessing import Queue

if platform.python_version_tuple()[0] == '3' and int(platform.python_version_tuple()[1]) >= 8:  # python 3.8或以上版本
    sys.stdout.reconfigure(encoding='utf-8')    # 使print函数输出utf-8编码的字符串
csv_file_path = './series.csv'

logger = logging.getLogger('tv_spider_server_log')  # 设置日志
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')     # 设置日志输出内容
log_file_handler = TimedRotatingFileHandler(filename='tv_spider_server_log', when='MIDNIGHT', interval=1, backupCount=20)  # 每日产生一个日志文件log，凌晨生成，超过20个自动删除最旧的
log_file_handler.setFormatter(formatter)
log_file_handler.setLevel(logging.INFO)
logger.addHandler(log_file_handler)


USER_AGENTS_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]

season_dist = {'First Season': 'S01', 'Second Season': 'S02', 'Third Season': 'S03', 'Fourth Season': 'S04',
               'Fifth Season': 'S05', 'Sixth Season': 'S06', 'Seventh Season': 'S07', 'Eighth Season': 'S08',
               'Ninth Season': 'S09', 'Tenth Season': 'S10', 'Eleventh Season': 'S11', 'Twelfth Season': 'S12',
               'Thirteenth Season': 'S13', 'Fourteenth Season': 'S14', 'Fifteenth Season': 'S15',
               'Sixteenth Season': 'S16', 'Seventeenth Season': 'S17', 'Eighteenth Season': 'S18',
               'Nineteenth Season': 'S19', 'Twentieth Season': 'S20', 'Twenty-First Season': 'S21',
               'Twenty-Second Season': 'S22', 'Twenty-Third Season': 'S23', 'Twenty-Fourth Season': 'S24',
               'Twenty-Fifth Season': 'S25', 'Twenty-Sixth Season': 'S26', 'Twenty-Seventh Season': 'S27',
               'Twenty-Eighth Season': 'S28', 'Twenty-Ninth Season': 'S29', 'Thirtieth Season': 'S30',
               'Thirty-First Season': 'S31', 'Thirty-Second Season': 'S32', 'Thirty-Third Season': 'S33',
               'Thirty-Fourth Season': 'S34', 'Thirty-Fifth Season': 'S35', 'Thirty-Sixth Season': 'S36',
               'Thirty-Seventh Season': 'S37', 'Thirty-Eighth Season': 'S38', 'Thirty-Ninth Season': 'S39',
               'Fortieth Season': 'S40', 'Forty-First Season': 'S41', 'Forty-Second Season': 'S42',
               'Forty-Third Season': 'S43', 'Forty-Fourth Season': 'S44', 'Forty-Fifth Season': 'S45',
               'Forty-Sixth Season': 'S46', 'Forty-Seventh Season': 'S47', 'Forty-Eighth Season': 'S48',
               'Forty-Ninth Season': 'S49', 'Fiftieth Season': 'S50'
               }

session = requests.session()
url_set = set()
server = socket(AF_INET, SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(10)     # 最大连接数
conn_dict = {}        # 存放每个客户端的连接对象
status_dict = {}      # 状态字典，记录每一个客户端是否正在执行下载任务
job_queue = Queue()    # 任务栈
lock = threading.Lock()    # 线程互斥锁


def print_and_log(msg):
    try:
        print(msg)
        logger.info(msg)
    except Exception as err:
        print('Error: Unable to print msg!!!')
        print(err)
        logger.info('Error: Unable to print msg!!!')
        logger.info(err)


def ajax_header():     # ajax请求头
    return {
        'accept-encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'accept': 'application/json, text/plain, */*',
        'Host': 'v2.sg.media-imdb.com',
        'Origin': 'https://www.imdb.com',
        'Referer': 'https://www.imdb.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }


def stander_header():
    return {
        'accept-encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }


def download_header():
    return {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://subscene.com/subtitles/searchbytitle',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }


def get_cookies():
    count = 0
    while count < 3:
        try:
            res = session.get('https://subscene.com', headers=stander_header())     # 获取cookies
        except:
            count += 1
            time.sleep(5)
            continue
        else:
            if res.status_code != 200:
                count += 1
                time.sleep(5)
                continue
            else:
                break


def get_response(url, my_header):
    time.sleep(5)
    res = None
    count = 0
    while count < 3:    # 3次重连机会
        try:
            res = session.get(url, headers=my_header, timeout=10)
        except Exception as err:
            count += 1
            print_and_log(err)
            print_and_log('Retry again!  '+str(count))
            time.sleep(10)
            continue
        else:
            if res.status_code != 200:
                count += 1
                print_and_log('Status code is ' + str(res.status_code) + ' Retry again!  ' + str(count))
                if res.status_code == 403:
                    time.sleep(15)
                elif res.status_code == 409:
                    time.sleep(5)
                else:
                    time.sleep(10)
                continue
        if res != None and res.status_code == 200:
            break
    if res == None or count >= 3:
        return None
    else:
        return res


def post_response(url, my_header, post_data):
    time.sleep(5)
    res = None
    count = 0
    while count < 3:     # 3次重连机会
        try:
            res = session.post(url, headers=my_header, data=post_data, timeout=10)
        except Exception as err:
            count += 1
            print_and_log('Post connect retry again! ' + str(count))
            print_and_log(err)
            time.sleep(10)
            continue
        else:
            if res.status_code != 200:
                count += 1
                print_and_log('Post status code is ' + str(res.status_code) + ' Retry again!  ' + str(count))
                if res.status_code == 403:
                    time.sleep(15)
                elif res.status_code == 409:
                    time.sleep(5)
                else:
                    time.sleep(10)
                continue
        if res != None and res.status_code == 200:
            break
    if res == None or count >= 3:
        return None
    else:
        return res


def release_lock(locker):
    try:
        locker.release()
    except Exception as err:
        print_and_log('error in release lock!')
        print_and_log(err)


def sender():
    while 1:
        time.sleep(5)
        lock.acquire()
        for each_address in conn_dict.keys():
            if not status_dict[each_address] and not job_queue.empty():  # 有客户端正在空闲，并且有任务
                try:
                    conn_dict[each_address].sendall(job_queue.get())  # 获取任务，并发送到客户端
                    status_dict[each_address] = True                  # 客户端变忙
                except Exception as err:
                    print_and_log('Error: Send job error!')
                    print_and_log(err)
        release_lock(lock)


def receiver(sock, address):
    while 1:
        try:
            rec = sock.recv(1024)
            lock.acquire()
            if rec.decode('utf-8') == 'exit' or rec.decode('utf-8') == '':
                conn_dict[address].close()
                conn_dict.pop(address)
                status_dict.pop(address)
                print_and_log(address + ' connection close!')
                release_lock(lock)
                break
        except ConnectionResetError:                    # 客户端强迫关闭连接
            print_and_log(address+' forced to close!')
            time.sleep(1)
            conn_dict.pop(address)
            status_dict.pop(address)
            release_lock(lock)
            break
        except Exception as err:
            print_and_log('Error: receive from '+address)
            print_and_log(err)
            conn_dict[address].sendall('exit'.encode('utf-8'))
            time.sleep(2)
            conn_dict[address].close()
            conn_dict.pop(address)
            status_dict.pop(address)
            print_and_log(address+' connection close by error')
            release_lock(lock)
            break
        else:
            status_dict[address] = False   # 客户端变空闲
            release_lock(lock)


def receiver_maker():
    while 1:
        client_sock, client_address = server.accept()
        if str(client_address) not in conn_dict:
            lock.acquire()
            conn_dict.update({str(client_address): client_sock})
            status_dict.update({str(client_address): False})
            release_lock(lock)
        print_and_log('Connect from: '+str(client_address))
        t = threading.Thread(target=receiver, args=(client_sock, str(client_address)))  # 每连接一个客户端就创建一个线程用于接收
        t.start()


def main():
    t1 = threading.Thread(target=receiver_maker, args=())
    t2 = threading.Thread(target=sender, args=())
    t1.start()
    t2.start()
    get_cookies()
    csv_file = open(csv_file_path, 'r')    # 读取csv文件
    imdb_str = csv_file.read()
    csv_file.close()
    imdb_list = imdb_str.split('\n')    # 获取csv文件中的所有电视剧imdb
    try:
        with open('./schedule', 'r', encoding='utf-8') as f:
            recoder = f.read()            # 读取进度记录文件
        imdb_list_index = int(recoder.split(',')[0])
        li_index = int(recoder.split(',')[1])
    except:
        imdb_list_index = 0
        li_index = 0
    while imdb_list_index < len(imdb_list):
        print_and_log('IMDB now is ' + imdb_list[imdb_list_index])
        print_and_log('IMDB schedule is ' + str(int((imdb_list_index+1) / len(imdb_list) * 100)) + '%')
        imdb_url = 'https://v2.sg.media-imdb.com/suggestion/t/' + imdb_list[imdb_list_index] + '.json'
        tv_name_ajax = None
        res = get_response(imdb_url, my_header=ajax_header())
        if res == None or res.status_code != 200:
            if res != None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log('ERROR: Unable to get IMDB ajax response!')
        else:
            try:
                json_dict = json.loads(res.text)
                tv_name_ajax = json_dict['d'][0]['l']
            except Exception as err:
                print_and_log('ERROR: Unable to get TV name from json response!')
                print_and_log(err)
                tv_name_ajax = None
        time.sleep(1)
        imdb_url = 'https://www.imdb.com/title/' + imdb_list[imdb_list_index] + '/'
        res = get_response(imdb_url, my_header=stander_header())     # 搜索IMDB网站获取imdb对应的电视剧名称
        if res == None or res.status_code != 200:
            if res != None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log('ERROR: Unable to get IMDB page response!')
            imdb_list_index += 1
            continue
        html = etree.HTML(res.text)
        h1 = html.xpath('//h1')
        if h1 == None or len(h1) == 0:
            print_and_log('ERROR: Unable to get this TV name title h1!  ' + imdb_url)
            imdb_list_index += 1
            continue
        h1 = h1[0]
        tv_name = h1.getprevious().xpath('.//text()')  # 获取真正的电视剧名称，非剧集名称
        imdb_true = h1.getprevious().xpath('./a/@href')  # 获取真正的电视剧的imdb
        if tv_name == None or len(tv_name) == 0 or imdb_true == None or len(imdb_true) == 0:
            if tv_name_ajax != None:
                tv_name = [tv_name_ajax]
            else:
                tv_name = h1.xpath('./text()')  # 若无，则该剧集名称就是电视剧名称
            imdb_true = None
        else:
            imdb_t = re.findall(r'.*\D(tt\d{7,8})\D.*', imdb_true[0])     # 有则获取真正电视剧的imdb
            if imdb_t == None or len(imdb_t) == 0:  # 无法获取真正的电视剧的imdb
                if tv_name_ajax != None:
                    tv_name = [tv_name_ajax]
                else:
                    tv_name = h1.xpath('./text()')
                imdb_true = None
            else:
                imdb_true = imdb_t[0]
        if tv_name == None or len(tv_name) == 0:
            print_and_log('ERROR: Unable to get this TV name!  ' + imdb_url)
            imdb_list_index += 1
            continue
        tv_name = ''.join(tv_name).replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').strip()      # 获取imdb对应的电视剧名称
        if tv_name == 'Scream: The TV Series':
            tv_name = 'Scream'
        elif tv_name == 'The Returned':
            tv_name = 'Les revenants'
        elif tv_name == 'Chernobyl: Zone of Exclusion':
            tv_name = 'Chernobyl: Zona otchuzhdeniya'
        elif tv_name == 'Yuki Yuna Is a Hero':
            tv_name = 'Yuuki Yuuna wa yuusha de aru'
        post_data = {'query': tv_name, 'l': ''}
        header_subscene = {
            'referer': 'https://subscene.com/subtitles/searchbytitle',
            'origin': 'https://subscene.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'accept-encoding': 'gzip, deflate',
            'ec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
        }
        h2 = None
        uls = None
        count = 0
        while count < 8:
            res = post_response('https://subscene.com/subtitles/searchbytitle', header_subscene, post_data)     # 使用subscene网站进行搜索
            if res == None or res.status_code != 200:
                if res != None:
                    print_and_log('Status Code is ' + str(res.status_code))
                print_and_log('Error: Unable to search: << ' + tv_name + ' >> in subscene.com  ' + str(count) + '  ' + imdb_list[imdb_list_index])
                session.cookies.clear_session_cookies()
                time.sleep(5)
                get_cookies()
                count += 1
                continue
            html = etree.HTML(res.text)
            h2 = html.xpath('//div[@class="search-result"]/h2/text()')  # 获取标题(电视剧名称)
            uls = html.xpath('//div[@class="search-result"]/ul')  # 获取ul标签
            if h2 == None or uls == None or len(h2) == 0 or len(uls) == 0 or len(h2) != len(uls):
                print_and_log('Error: No Results Found!!!  '+str(count) + '  ' + imdb_list[imdb_list_index])
                time.sleep(5)
                count += 1
                continue
            else:
                break
        if count >= 8 or h2 == None or uls == None:
            imdb_list_index += 1
            continue
        lis = []
        if 'TV-Series' in h2:  # 有电视剧系列
            for i in range(len(h2)):
                if h2[i] == 'TV-Series':  # 仅获取电视剧系列
                    lis = uls[i].xpath('./li')
        else:  # 若无电视剧系列，则获取全部标题
            for i in range(len(h2)):
                lis += uls[i].xpath('./li')
        if len(lis) == 0:
            print_and_log('Error: Unable to get lis!!!  ' + imdb_list[imdb_list_index] + '  << ' + tv_name + ' >>')
            imdb_list_index += 1
            continue
        schedule = li_index         # 每一个电视字幕文件的爬取进度
        is_not_found = True  # 是否找到指定imdb的电视剧，默认为否
        while li_index < len(lis):
            while 1:
                time.sleep(15)
                lock.acquire()
                if job_queue.empty():
                    release_lock(lock)
                    break
                else:
                    print_and_log('Waiting '+str(job_queue.qsize())+' job finish!')
                    release_lock(lock)
            with open('./schedule', 'w', encoding='utf-8') as f:
                f.write(str(imdb_list_index)+','+str(li_index))     # 写入进度记录文件
            schedule += 1
            print_and_log('<< '+tv_name+' >>  schedule now is: '+str(int(schedule/len(lis)*100))+'%')
            href = lis[li_index].xpath('.//a/@href')
            title_name = lis[li_index].xpath('.//a/text()')
            season = 'None'
            if title_name is not None:
                title_name = ''.join(title_name).replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').strip()
                for each_season in season_dist.keys():
                    if each_season in title_name:
                        season = season_dist[each_season]
                        break
            if href == None or len(href) == 0:
                print_and_log('Unable to get subtitles detail page url!  ' + tv_name)
                li_index += 1
                continue
            tv_url = 'https://subscene.com' + href[0]
            if 'TV-Series' not in h2 and tv_url in url_set:      # 检测该url是否已被访问过
                li_index += 1
                continue
            res = get_response(tv_url, my_header=header_subscene)     # 打开该电视剧字幕详情页面
            if res == None or res.status_code != 200:
                if res != None:
                    print_and_log('Status Code is ' + str(res.status_code))
                print_and_log('Unable to open page '+tv_url + '  ' + imdb_list[imdb_list_index])
                li_index += 1
                continue
            url_set.add(tv_url)           # 设置该url已被访问过
            html = etree.HTML(res.text)
            imdb = html.xpath('//h2/a[@class="imdb"]/@href')
            if imdb == None or len(imdb) == 0:
                # print_and_log('Error: Unable to get imdb, jump this!!!')
                li_index += 1
                continue
            imdb = imdb[0].split('/')[-1]
            if 'tt' not in imdb:
                # print_and_log('Error: This TV page no imdb, jump this!!!')
                li_index += 1
                continue
            try:
                imdb_tmp = str(int(imdb.replace('tt', '')))
            except Exception:    # imdb异常或不标准
                li_index += 1
                continue
            else:
                if len(imdb_tmp) > 8:  # imdb位数大于8，非正常imdb
                    li_index += 1
                    continue
                elif len(imdb_tmp) < 7:  # imdb位数小于7，补够7位
                    imdb = 'tt' + '0' * (7 - len(imdb_tmp)) + imdb_tmp
                else:  # 7位或8位，正常imdb
                    imdb = 'tt' + imdb_tmp
            if imdb not in imdb_list and imdb != imdb_true:
                li_index += 1
                continue  # 不是指定imdb的电视剧字幕，跳过
            else:
                is_not_found = False  # 是指定imdb的电视剧字幕
            a_s = html.xpath('//div[@class="content clearfix"]//tr/td[@class="a1"]/a')    # 获取页面上的字幕列表
            a_index = 0
            while a_index < len(a_s):      # 遍历字幕列表每一个字幕
                language = a_s[a_index].xpath('./span[1]/text()')     # 获取字幕语言
                file_page_url = a_s[a_index].xpath('./@href')       # 获取字幕下载详情页地址
                if file_page_url == None or language == None or len(file_page_url) == 0 or len(language) == 0:
                    print_and_log('Error: Unable to get subtitle title!  '+imdb_list[imdb_list_index])
                    a_index += 1
                    continue
                language = language[0].replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '').strip().lower()
                if 'big' in language:
                    a_index += 1
                    continue
                file_page_url = 'https://subscene.com' + file_page_url[0].replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
                subtitle_id = file_page_url.split('/')[-1]        # 获取该字幕的id
                count = 0
                download_url = None
                while count < 8:
                    res = get_response(file_page_url, my_header=stander_header())      # 打开字幕下载详情页面
                    if res == None or res.status_code != 200:
                        if res != None:
                            print_and_log('Status Code is ' + str(res.status_code))
                        print_and_log(str(count)+'  Unable to open subtitles download page!  '+file_page_url + '  ' + imdb_list[imdb_list_index])
                        session.cookies.clear_session_cookies()
                        count += 1
                        time.sleep(5)
                        get_cookies()
                        continue
                    html = etree.HTML(res.text)
                    download_url = html.xpath('//a[@id="downloadButton"]/@href')     # 获取字幕下载地址
                    if download_url == None or len(download_url) == 0:
                        print_and_log(str(count)+'  Unable to get subtitle download url!!!  '+file_page_url + '  ' + imdb_list[imdb_list_index])
                        count += 1
                        time.sleep(5)
                        continue
                    else:
                        break
                if count >= 8 or download_url == None or len(download_url) == 0:
                    a_index += 1
                    continue
                download_url = 'https://subscene.com' + download_url[0]
                if not os.path.exists('/data/series/'+imdb_list[imdb_list_index]):     # 创建该电视剧的文件夹
                    os.mkdir('/data/series/'+imdb_list[imdb_list_index])
                send_msg = imdb_list[imdb_list_index]+'<|>'+tv_name+'<|>'+language+'<|>'+subtitle_id+'<|>'+download_url+'<|>'+season
                lock.acquire()
                job_queue.put(send_msg.encode('utf-8'))
                release_lock(lock)
                a_index += 1
            li_index += 1
        if is_not_found:
            if imdb_true != None:
                print_and_log('Error: << '+tv_name+' >>  '+imdb_list[imdb_list_index]+'  ->  '+imdb_true+' Not Found !!!')
            else:
                print_and_log('Error: << ' + tv_name + ' >>  ' + imdb_list[imdb_list_index] + ' Not Found !!!')
        imdb_list_index += 1
    print_and_log('-----------------Finish All!--------------------')
    while 1:
        time.sleep(15)
        lock.acquire()
        if job_queue.empty():     # 任务已空
            is_finish = True
            for each_address in conn_dict.keys():
                if status_dict[each_address]:     # 客户端为运行状态
                    is_finish = False
                    break
            if is_finish:
                print_and_log('Close all connection!')
                for each_address in conn_dict.keys():
                    conn_dict[each_address].sendall('exit'.encode('utf-8'))
                    time.sleep(1)
                    conn_dict[each_address].close()
                time.sleep(1)
                server.close()
                print_and_log('Close server!')
                os.kill(os.getpid(), signal.SIGTERM)     # 结束程序
        else:
            print_and_log('Waiting '+str(job_queue.qsize())+' job finish!')
        release_lock(lock)


if __name__ == '__main__':
    main()
