# -*- coding: utf-8 -*-
import time
import requests
from random import randint
import re
import pymysql
import hashlib
import os
import sys
import logging
import zipfile
import chardet
from logging.handlers import TimedRotatingFileHandler
import paramiko
import rarfile
import platform
from socket import *
import threading
import signal
from multiprocessing import Queue
import ass2srt

if platform.python_version_tuple()[0] == '3' and int(platform.python_version_tuple()[1]) >= 8:  # python 3.8或以上版本
    sys.stdout.reconfigure(encoding='utf-8')    # 使print函数输出utf-8编码的字符串

logger = logging.getLogger('tv_spider_client_log')  # 设置日志
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')     # 设置日志输出内容
log_file_handler = TimedRotatingFileHandler(filename='tv_spider_client_log', when='MIDNIGHT', interval=1, backupCount=20)  # 每日产生一个日志文件log，凌晨生成，超过20个自动删除最旧的
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

language_dict = {
        "english": 'en', "spanish": 'es', "greek": 'el', "arabic": 'ar', "chinese": 'zh', "dutch": 'nl',
        "serbian": 'sr', "brazilian portuguese": 'pt', "croatian": 'hr', "french": 'fr',
        "portuguese-br": 'pt', "portuguese": 'pt', "turkish": 'tr', "indonesian": 'id', "romanian": 'ro',
        "norwegian": 'no', "bulgarian": 'bg', "farsi/persian": 'fa', "hebrew": 'he', "danish": 'da',
        "hungarian": 'hu', "finnish": 'fi', "italian": 'it', "swedish": 'sv', "malay": 'ms', "slovenian": 'ls',
        "polish": 'pl', "bengali": 'bn', "vietnamese": 'vi', "czech": 'cs', "german": 'de', "russian": 'ru',
        "macedonian": 'mk', "thai": 'th', "urdu": 'ur', "japanese": 'ja', "albanian": 'sq', "korean": 'ko',
        "lithuanian": 'lt', "farsi_persia": 'fa', "farsi_persian": 'fa', "persian": 'fa', "bosnian": 'bs',
        "malayalam": 'ml', "brazilian": 'br', "icelandic": 'is', "estonian": 'et', "brazillian-portuguese": 'pt',
        "chinese-bg-code": 'zh', "sundanese": 'su', "sinhala": 'si', "portuguese (br)": 'pt',
        "hindi": 'hi', "telugu": 'te', "br": 'br', "(br)": 'br', "galician": 'gl', "afrikaans": 'af',
        "armenian": 'hy', "uzbek": 'uz', "xhosa": 'xh', "yiddish": 'yi', "zulu": 'zu', "brazillian portuguese": 'pt',
        "assamese": 'as', "azeri (latin)": 'az', "azeri (cyrillic)": 'az', "azeri-latin": 'az', "myanmar": 'mm',
        "azeri-cyrillic": 'az', "azeri": 'az', "basque": 'eu', "belarusian": 'be', "catalan": 'ca',
        "chinese (china)": 'zh', "chinese (hong kong sar)": 'zh', "chinese (macau sar)": 'zh', 'cambodian/khmer': 'kh',
        "chinese (taiwan)": 'zh', "chinese-china": 'zh', "chinese-hong kong sar": 'zh', "chinese-macau sar": 'zh',
        "chinese-taiwan": 'zh', "chech": 'cs', "faeroese": 'fo', "farsi": 'fa', "gaelic": 'gd', "georgian": 'ka',
        "gujarati": 'gu', "italian (switzerland)": 'it', "italian (italy)": 'it', "italian-switzerland": 'it',
        "italian-italy": 'it', "kannada": 'kn', "kazakh": 'kk', "konkani": 'kok', "kyrgyz": 'kz', "latvian": 'lv',
        "malay (brunei)": 'ms', "malay (malaysia)": 'ms', "malay-brunei": 'ms', "malay-malaysia": 'ms',
        "maltese": 'mt', "marathi": 'mr', "mongolian (cyrillic)": 'mn', "nepali (india)": 'ne', "burma": 'mm',
        "norwegian (bokmal)": 'no', "norwegian (nynorsk)": 'no', "norwegian-bokmal": 'no', "burmese": 'mm',
        "norwegian-nynorsk": 'no', "oriya": 'or', "punjabi": 'pa', "serbian-latin": 'sr', "sanskrit": 'sa',
        "rhaeto-romanic": 'rm', "serbian-cyrillic": 'sr', "slovak": 'sk', "sorbian": 'sb', "sutu": 'sx',
        "swahili": 'sw', "syriac": 'syr', "tamil": 'tt', "tsonga": 'ts', "tswana": 'tn', "ukrainian": 'uk',
        'khmer': 'kh', 'cambodian': 'kh', "chinese bg code": 'zh', 'kurdish': 'ku', 'yoruba': 'yo', 'nepali': 'ne',
        'tagalog': 'tl', 'occitan': 'oc', 'ukranian': 'uk'
}

conn = pymysql.connect(host='127.0.0.1', port=3336, user='root', password='xxxxxxxxxxxxx',
                       charset='utf8', database='subtitles')
cursor = conn.cursor()
insert_sql = "insert into series(imdb_id,episodes,moviename,language,languageShort,path) VALUES(%s,%s,%s,%s,%s,%s);"
select_sql = "select path from series where imdb_id=%s and language=%s and episodes=%s;"
select_all_sql = "select id from series where imdb_id=%s and language=%s and episodes=%s and path=%s;"

session = requests.session()
client = socket(AF_INET, SOCK_STREAM)
client.connect(('109.236.82.140', 9999))
job_queue = Queue()         # 任务栈
lock = threading.Lock()    # 线程互斥锁

host = '109.236.82.140'     # 字幕服务器，需要向字幕服务器上传字幕文件
port = 22                   # SSH端口
user = 'root'
password = 'xxxxxxxxxxxxxx'
transport = paramiko.Transport((host, port))
transport.connect(username=user, password=password)   # 连接字幕服务器
sftp = paramiko.SFTPClient.from_transport(transport)
is_close_transport = False       # 连接是否已关闭


def print_and_log(msg):
    try:
        print(msg)
        logger.info(msg)
    except Exception as err:
        print('Error: Unable to print msg!!!')
        print(err)
        logger.info('Error: Unable to print msg!!!')
        logger.info(err)


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


def scp_file(source_file, target_file):
    global transport
    global sftp
    global is_close_transport
    try:
        if is_close_transport:   # 如果已断开连接，则需要重连
            transport = paramiko.Transport((host, port))
            transport.connect(username=user, password=password)  # 连接字幕服务器
            sftp = paramiko.SFTPClient.from_transport(transport)
            is_close_transport = False
        sftp.put(source_file, target_file)
    except Exception as err:
        print_and_log('Error: Unable use SCP to transfer files!!!')
        print_and_log(err)
        is_close_transport = True
        return False
    else:
        return True


def scp_folder(remote_folder):
    global transport
    global sftp
    global is_close_transport
    try:
        if is_close_transport:    # 如果已断开连接，则需要重连
            transport = paramiko.Transport((host, port))
            transport.connect(username=user, password=password)  # 连接字幕服务器
            sftp = paramiko.SFTPClient.from_transport(transport)
            is_close_transport = False
        sftp.mkdir(remote_folder)
    except Exception as err:
        print_and_log('Error: Unable use SCP to transfer folder!!!')
        print_and_log(err)
        is_close_transport = True
        return False
    else:
        return True


def get_md5_response(url):
    time.sleep(0.5)
    md5_header = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }
    res = None
    count = 0
    while count < 3:  # 3次重连机会
        try:
            res = requests.get(url, headers=md5_header, timeout=10)
        except Exception as err:
            count += 1
            print_and_log(err)
            print_and_log('get MD5 Retry again!  ' + str(count))
            time.sleep(10)
            continue
        else:
            if res.status_code != 200:
                if res.status_code == 404:
                    print_and_log('MD5 response status code is 404!!!')
                    count = 3
                    res = None
                    break
                count += 1
                print_and_log('get MD5 Status code is ' + str(res.status_code) + ' Retry again!  ' + str(count))
                time.sleep(10)
                continue
        if res != None and res.status_code == 200:
            break
    if res == None or count >= 3:
        return None
    else:
        return res


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


def transform_encode(data):      # 字幕文件转码为utf-8
    try:
        encode = chardet.detect(data)
        str_encode = encode['encoding']
        if str_encode == 'MacCyrillic':
            str_encode = 'Windows-1256'
        if str_encode != None:
            d = data.decode(str_encode, errors='ignore')
        else:
            try:
                d = data.decode('UTF-8')
            except:
                try:
                    d = data.decode('gbk')
                except:
                    try:
                        d = data.decode('gb2312')
                    except:
                        try:
                            d = data.decode('cp437')
                        except:
                            try:
                                d = data.decode('cp850')
                            except:
                                print_and_log('Error: No suitable charset encoding is available!')
                                return None
        after = d.encode('UTF-8', errors='ignore')
    except Exception as err:
        print_and_log('Error in transform_encode!')
        print_and_log(err)
        return None
    else:
        return after


def get_season_and_episode(name):      # 使用正则表达式获取字幕文件名上的季和集信息
    season = None
    episode = None
    if len(re.findall(r'.*([sS][ _-]\d{1,2}[ _-][eE][ _-]\d{1,2}).*', name)) == 1:
        season = re.findall(r'.*[sS][ _-](\d{1,2})[ _-][eE][ _-]\d{1,2}.*', name)
        episode = re.findall(r'.*[sS][ _-]\d{1,2}[ _-][eE][ _-](\d{1,2}).*', name)
        if season == None or episode == None or len(season) != 1 or len(episode) != 1 or season[0] == '00' or season[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([Ss]eason[ _-]\d{1,2}[ _-][Ee]pisode[ _-]\d{1,2}).*', name)) == 1:
        season = re.findall(r'.*[Ss]eason[ _-](\d{1,2})[ _-][Ee]pisode[ _-]\d{1,2}.*', name)
        episode = re.findall(r'.*[Ss]eason[ _-]\d{1,2}[ _-][Ee]pisode[ _-](\d{1,2}).*', name)
        if season == None or episode == None or len(season) != 1 or len(episode) != 1 or season[0] == '00' or season[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([Ss]eason\d{1,2}[Ee]pisode\d{1,2}).*', name)) == 1:
        season = re.findall(r'.*[Ss]eason(\d{1,2})[Ee]pisode\d{1,2}.*', name)
        episode = re.findall(r'.*[Ss]eason\d{1,2}[Ee]pisode(\d{1,2}).*', name)
        if season == None or episode == None or len(season) != 1 or len(episode) != 1 or season[0] == '00' or season[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([Ss]eason\d{1,2}[\. _-][Ee]pisode\d{1,2}).*', name)) == 1:
        season = re.findall(r'.*[Ss]eason(\d{1,2})[\. _-][Ee]pisode\d{1,2}.*', name)
        episode = re.findall(r'.*[Ss]eason\d{1,2}[\. _-][Ee]pisode(\d{1,2}).*', name)
        if season == None or episode == None or len(season) != 1 or len(episode) != 1 or season[0] == '00' or season[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([sS]\d{1,2}[eE]\d{1,2}).*', name)) == 1:
        season = re.findall(r'.*[sS](\d{1,2})[eE]\d{1,2}.*', name)
        episode = re.findall(r'.*[sS]\d{1,2}[eE](\d{1,2}).*', name)
        if episode == None or len(episode) != 1 or season == None or len(season) != 1 or season[0] == '00' or season[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([sS]\d{1,2}[\. _-][eE]\d{1,2}).*', name)) == 1:
        season = re.findall(r'.*[sS](\d{1,2})[\. _-][eE]\d{1,2}.*', name)
        episode = re.findall(r'.*[sS]\d{1,2}[\. _-][eE](\d{1,2}).*', name)
        if episode == None or len(episode) != 1 or season == None or len(season) != 1 or season[0] == '00' or season[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*(\D\d{1,2}x\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*\D(\d{1,2})x\d{1,2}\D.*', name)
        episode = re.findall(r'.*\D\d{1,2}x(\d{1,2})\D.*', name)
        if season == None or episode == None or len(season) != 1 or len(episode) != 1 or season[0] == '00' or season[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    else:
        return None


def get_episode(name):    # 仅获取字幕文件名中的集的信息
    episode = None
    if len(re.findall('.*(\D[eE]pisode\d{1,2}\D).*', name)) == 1:
        episode = re.findall('.*\D[eE]pisode(\d{1,2})\D.*', name)
        if episode == None or len(episode) != 1:
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    elif len(re.findall('.*(\D[eE]\d{1,2}\D).*', name)) == 1:
        episode = re.findall('.*\D[eE](\d{1,2})\D.*', name)
        if episode == None or len(episode) != 1:
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    elif len(re.findall('.*(\D\d\d\D).*', name)) == 1:
        episode = re.findall('.*\D(\d\d)\D.*', name)
        if episode == None or len(episode) != 1:
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    else:
        return None


def file_name_translate(name):
    translate_name = None
    try:
        translate_name = name.replace('\u2019', '').encode('cp437', errors='ignore').decode('ascii', errors='ignore')
    except Exception as err:
        translate_name = None
        print_and_log('Error: No suitable charset encoding is available for file name!')
        print_and_log(err)
    return translate_name


def delete_special_char(name):
    # 去掉文件名中的括号和特殊字符
    return name.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '') \
        .replace(' .', '.').replace('. ', '.').replace('?', '').replace('&', '').replace("'", '').replace('%20', '-') \
        .replace('`', '').replace('!', '').replace(',', '').replace('-_-', '-').replace('#', '').replace('+', '-') \
        .replace('%', '').replace('@', '').replace('!', '').replace('$', '').replace('^', '').replace('*', '') \
        .replace('~', '').replace('<', '').replace('>', '').replace('|', '').replace('"', '').replace('=', '') \
        .replace(';', '').replace(':', '').replace(' ', '-').replace('._.', '-').replace('.-.', '-') \
        .replace('-.-', '-').replace('--', '-').replace('..', '.').replace('__', '-')


def close_connection(send_exit=False):
    if send_exit:
        client.sendall('exit'.encode('utf-8'))      # 告知服务端的接受者关闭当前连接
    time.sleep(1)
    client.close()
    print_and_log('client close!')
    try:
        transport.close()
        cursor.close()
        conn.close()
    except Exception as err:
        print_and_log('Error: Unable to close all connection!')
        print_and_log(err)
    os.kill(os.getpid(), signal.SIGTERM)           # 结束程序


def release_lock(locker):
    try:
        locker.release()        # 释放锁
    except Exception as err:
#        print_and_log('error in release lock!')
        print_and_log(err)


def receiver():
    while 1:
        try:
            byte_data = client.recv(1024)
            if byte_data.decode('utf-8') == 'exit' or byte_data.decode('utf-8') == '':
                print_and_log('Client receiver close!')
                close_connection(send_exit=True)
                break
            lock.acquire()
            try:
                job_queue.put(byte_data.decode('utf-8'))
            except Exception as err:
                print_and_log('Error: Unable put job to queue!')
                print_and_log(err)
            release_lock(lock)
        except ConnectionResetError:             # 服务端强迫关闭连接
            print_and_log('Server forced to close!')
            close_connection(send_exit=False)
            break
        except Exception as err:
            print_and_log('Client receive string error!')
            print_and_log(err)
            close_connection(send_exit=True)
            break


def send_finish():
    try:
        client.sendall('OK'.encode('utf-8'))     # 告知服务端，客户端已完成任务，正在空闲
    except Exception as err:
        print_and_log('Client send string error!')
        print_and_log(err)
        close_connection(send_exit=True)


def download_subtitles_file(url, language, imdb, tv_name, subtitle_id, season):
    global is_close_transport
    release_lock(lock)
    if len(re.findall('^tt\d{7,8}', imdb)) != 1 and len(imdb) != 7 and len(imdb) != 8:
        print_and_log('Error: Job message imdb not correct, skip!!!  ' + imdb)
        return None
    if 'None' != season and ('S' not in season or len(season) != 3):
        print('Error: Job message season not correct, skip!!!  ' + season)
        return None
    file_name = url.split('/')[-1] + '.zip'
    res = None
    count = 0
    while count < 8:
        res = get_response(url, my_header=download_header())  # 下载字幕文件压缩包
        if res == None or res.status_code != 200:
            if res != None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log(str(count) + '  Unable to download subtitles file!  ' + url + '  ' + imdb)
            session.cookies.clear_session_cookies()
            count += 1
            time.sleep(5)
            get_cookies()
        else:
            count = 0
            break
    if res == None or count >= 8:
        return None
    try:
        with open('/data/series/tmp/'+file_name, 'wb') as f:       # 字幕zip包保存到/data/series/tmp目录下
            f.write(res.content)
    except Exception as err:
        print_and_log('Error: Save subtitles file error!!!  '+imdb)
        print_and_log(err)
        return None
    try:
        zip_file = zipfile.ZipFile('/data/series/tmp/'+file_name, 'r')    # 尝试使用zip打开压缩包
    except:
        try:
            zip_file = rarfile.RarFile('/data/series/tmp/'+file_name, 'r')   # 不成功，则尝试使用rar打开压缩包
        except Exception as err:
            print_and_log('Error: Unable to open compress file!!!')
            print_and_log(err)
            return None
    for srt_file_name in zip_file.namelist():     # 遍历zip包内所有文件的文件名称
        srt_file = file_name_translate(srt_file_name)     # 文件名去除非ASC-II编码的字符
        if srt_file == None:
            continue
        if '/' in srt_file:  # 文件名带有目录的情况
            srt_file = delete_special_char(srt_file[srt_file.rfind('/') + 1:].replace('\\', ''))
        elif '\\' in srt_file:  # 文件名带有目录的情况
            srt_file = delete_special_char(srt_file[srt_file.rfind('\\') + 1:].replace('/', ''))
        else:  # 文件名不带有目录
            srt_file = delete_special_char(srt_file)
        if not srt_file.endswith('.srt') and not srt_file.endswith('.ass'):  # 不是.srt或.ass后缀，则跳过
            print_and_log('Not a subtitle file:  ' + srt_file)
            continue
        season_and_episode = get_season_and_episode(srt_file)    # 从文件名获取季和集信息
        if season_and_episode == None:
            episode = get_episode(srt_file)  # 从文件名获取集信息
            if episode == None:
                print_and_log('File name not contain season and episode:  ' + srt_file)
                continue
            else:
                if season == 'None':
                    print_and_log('Title and file name not contain season:  ' + srt_file)
                    continue
                else:
                    print_and_log('Only episode in file name: ' + srt_file)
                    season_and_episode = season + episode
        if not os.path.exists('/data/series/' + imdb):        # 创建季文件夹
            os.mkdir('/data/series/' + imdb)
        if not os.path.exists('/data/series/'+imdb+'/'+season_and_episode):   # 创建集文件夹
            os.mkdir('/data/series/'+imdb+'/'+season_and_episode)
            if not scp_folder('/data/series/'+imdb+'/'+season_and_episode):   # 如果scp同步文件夹失败则跳过
                print_and_log('Error: SCP synchronize folder failed!!!')
                # continue
        try:
            data = zip_file.read(srt_file_name)  # 根据文件名从zip包读取指定文件
        except Exception as err:
            print_and_log('Error: Unable to read file from compress file! (no replace)')
            print_and_log(err)
            try:
                data = zip_file.read(srt_file_name.replace('/', '\\'))  # 根据文件名从zip包读取指定文件
            except Exception as err:
                print_and_log('Error: Unable to read file from compress file! (replace /)')
                print_and_log(err)
                try:
                    data = zip_file.read(srt_file_name.replace('\\', '/'))  # 根据文件名从zip包读取指定文件
                except Exception as err:
                    print_and_log('Error: Unable to read file from compress file! (replace \\)')
                    print_and_log(err)
                    continue
        if len(data) < 1024*2:     # 数据小于2KB
            print_and_log('Error: Subtitle file data too small, skip!  ' + srt_file)
            continue
        data = transform_encode(data)
        if srt_file.endswith('.srt'):          # srt字幕文件
            data = transform_encode(data)
            if data == None:                   # srt字幕文件不成功转码为utf-8，则放弃
                continue
            srt_file_new = '/data/series/' + imdb + '/' + season_and_episode + '/' + subtitle_id + '-' + srt_file  # 新文件绝对路径
        else:                                  # ass字幕文件
            with open('/data/series/tmp/' + srt_file, 'wb') as f:
                f.write(data)
            ass_file = open('/data/series/tmp/' + srt_file, 'r', encoding='utf-8')
            try:
                srt_string = ass2srt.convert(ass_file, None, True, False)           # 将ass文件转为srt文件
            except Exception as err:
                print_and_log('Error: Unable to convert ass to srt!')
                print_and_log(err)
                ass_file.close()
                continue
            ass_file.close()
            data = srt_string.encode('utf-8')
            srt_file_new = '/data/series/' + imdb + '/' + season_and_episode + '/' + subtitle_id + '-' + srt_file + '.srt'  # 新文件绝对路径
#            print_and_log(srt_file_new + ' is ass after convert file!!!')
        md5_this = None
        try:
            md5_this = hashlib.md5(data).hexdigest()
        except Exception as err:
            print_and_log('Error: 1---Unable to get file MD5!  '+srt_file)
            print_and_log(err)
            continue
        if md5_this == None:
            print_and_log('Error: 1---Unable to get file MD5!  ' + srt_file)
            continue
        result = ()
        try:
            cursor.execute(select_sql, (imdb, language, season_and_episode))      # 从数据库查询所有该电视剧、该语种、该季集的字幕文件路径
            result = cursor.fetchall()
        except Exception as err:
            print_and_log('Error: Unable to get data from DB!!! Unable to compare the subtitle file MD5 value!')
            print_and_log(err)
            continue
        is_exist = False  # 字幕文件是否已存在，默认为否
        for each_result in result:  # 分别比较已存在的文件与现在下载的文件的MD5值
            res = get_md5_response(each_result[0])
            if res == None or res.status_code != 200:
                if res != None:
                    print_and_log('Status code is ' + str(res.status_code))
                print_and_log('error: 2---Unable to get file MD5 response, skip this file!  ' + each_result[0])
                continue
            try:
                md5_result = hashlib.md5(res.content).hexdigest()  # 读取文件，获取其MD5值
            except Exception as err:
                print_and_log('error: 2---Unable to get file MD5, skip this file!  ' + each_result[0])
                print_and_log(err)
                continue
            if md5_result == None:
                print_and_log('error: 2---Unable to get file MD5, skip this file!  ' + each_result[0])
                continue
            if md5_this == md5_result:  # MD5相同，即为相同字幕文件
                is_exist = True
                is_close_transport = True
                transport.close()
                # print_and_log('<< '+tv_name+' >> '+language+' '+season_and_episode+' '+srt_file_new.split('/')[-1]+' is existed on Disk!!!')
                break
        if not is_exist:  # 文件还没存在
            language_short = language_dict.get(language)      # 获取语言缩写
            if language_short == None:
                print_and_log('Error: Unable to get ' + language + ' short name!')
            result = ()
            try:
                cursor.execute(select_all_sql, (imdb, language, season_and_episode,
                                                'http://109.236.82.140:8088' + srt_file_new))  # 查询数据库是否已有该文件名称的电视剧记录
                result = cursor.fetchall()
            except Exception as err:
                print_and_log('Error: Unable to get data from DB!!! Unable to check this subtitle data existed or not on DB!')
                print_and_log(err)
                continue
            if len(result) > 0:  # 有该文件名称的电视剧记录
                random_code = format(int(str(time.time()).replace('.', '') + str(randint(0, 1000))), 'x')
                if srt_file_new.endswith('.ass.srt'):
                    srt_file_new = srt_file_new.replace('.ass.srt', '') + '-' + random_code + '.ass.srt'  # 文件名增加随机码，以避开相同文件名
                else:
                    srt_file_new = srt_file_new.replace('.srt', '') + '-' + random_code + '.srt'  # 文件名增加随机码，以避开相同文件名
            try:
                cursor.execute(insert_sql,
                               (imdb, season_and_episode, tv_name,
                                language, language_short, 'http://109.236.82.140:8088' + srt_file_new))  # 插入数据库
                conn.commit()
            except Exception as err:
                print_and_log('Error: Unable insert data to DB!!!')
                print_and_log(err)
                continue
            else:
                try:
                    with open(srt_file_new, 'wb') as f:  # 插入数据库成功后，再把文件写入磁盘
                        f.write(data)
                except Exception as err:
                    print_and_log('Error: Unable save subtitle file to disk!!!')
                    print_and_log(err)
                    continue
                if not scp_file(srt_file_new, srt_file_new):  # 如果scp同步文件不成功则跳过
                    print_and_log('Error: SCP synchronize file failed!!!')
                    continue
                print_and_log('********<< ' + tv_name + ' >> ' + language + ' ' + season_and_episode + ' ' +
                              srt_file_new.split('/')[-1] + ' is successfully insert to DB!')
    try:
        zip_file.close()     # 关闭zip文件
    except Exception as err:
        print_and_log('Error: Unable to close compress file!!!  '+'/data/series/tmp/'+file_name)
        print_and_log(err)
    try:
        os.system('rm -f /data/series/tmp/*')     # 删除tmp目录下zip包，节约空间
    except Exception as err:
        print_and_log('Error: Unable to delete compress file and subtitle file!!!')
        print_and_log(err)
    return None


def main():
    if not os.path.exists('/data'):
        os.mkdir('/data')
    if not os.path.exists('/data/series'):
        os.mkdir('/data/series')
    if not os.path.exists('/data/series/tmp'):  # 创建存放zip包的临时文件夹
        os.mkdir('/data/series/tmp')
    t1 = threading.Thread(target=receiver, args=())    # 创建子线程用于接收服务端发过来的任务
    t1.start()
    get_cookies()
    is_first_print = True
    while 1:
        time.sleep(2)
        lock.acquire()
        if not job_queue.empty():
            is_first_print = True
            job_str = job_queue.get()
            job_str_list = job_str.split('<|>')
            if len(job_str_list) != 6:
                print_and_log('Error: Job message string not correct!')
            else:
                download_subtitles_file(job_str_list[4], job_str_list[2], job_str_list[0],
                                        job_str_list[1], job_str_list[3], job_str_list[5])     # 执行字幕压缩包下载、提取、写入数据库和保存到本地
                send_finish()     # 告诉服务端已完成任务
        else:
            if is_first_print:
                print_and_log('Waiting job now...............')
                is_first_print = False
        release_lock(lock)


if __name__ == '__main__':
    main()
