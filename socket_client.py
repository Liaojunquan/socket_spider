# -*- coding: utf-8 -*-
from socket import *
import threading
import time
import os
import signal

buff_size = 1024
client = socket(AF_INET, SOCK_STREAM)
client.connect(('127.0.0.1', 9999))

def close_connection(send_exit=False):
    if send_exit:
        client.sendall('exit'.encode('utf-8'))      # 告知服务端的接受者关闭当前连接
    time.sleep(1)
    client.close()
    print('client close!')
    os.kill(os.getpid(), signal.SIGTERM)           # 结束程序

def receiver():
    while 1:
        try:
            byte_data = client.recv(buff_size)
            if byte_data.decode('utf-8') == 'exit' or byte_data.decode('utf-8') == '':
                print('Client receiver close!')
                close_connection(send_exit=True)
                break
            print(byte_data.decode('utf-8'))
        except ConnectionResetError:             # 服务端强迫关闭连接
            print('Server forced to close!')
            close_connection(send_exit=False)
            break
        except Exception as err:
            print('Client receive string error!')
            print(err)
            close_connection(send_exit=True)
            break


def sender():
    while 1:
        try:
            input_str = input()
            client.sendall(input_str.encode('utf-8'))
            if input_str == 'exit':
                print('Client sender close!')
                close_connection(send_exit=False)
                break
        except EOFError:
            print('EOF error exit!')
            close_connection(send_exit=True)
            break
        except Exception as err:
            print('Client send string error!')
            print(type(err))
            print(err)
            close_connection(send_exit=True)
            break


if __name__ == '__main__':
    t1 = threading.Thread(target=receiver, args=())
    t2 = threading.Thread(target=sender, args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    client.close()
    print('Client Close!')
