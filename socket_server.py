# -*- coding: utf-8 -*-
from socket import *
import threading
import time
import os
import signal

address = '0.0.0.0'
port = 9999
buff_size = 1024
server = socket(AF_INET, SOCK_STREAM)
server.bind((address, port))
server.listen(5)     # 最大连接数
conn_dict = {}


def tcplink(sock, addr):
    while 1:
        try:
            byte_data = sock.recv(buff_size)
            if byte_data.decode('utf-8') == 'exit':
                conn_dict[addr].close()        # 关闭与该地址的客户端的连接
                conn_dict.pop(addr)            # 移除记录
                print(addr, 'exit!')
                break
            elif byte_data.decode('utf-8') == '':
                conn_dict[addr].close()         # 关闭与该地址的客户端的连接
                conn_dict.pop(addr)             # 移除记录
                print(addr, 'offline!')
                break
            print(byte_data.decode('utf-8'))
        except ConnectionResetError:          # 客户端强迫关闭连接
            conn_dict.pop(addr)               # 移除记录
            print(addr, 'forced to close!')
            break
        except Exception as err:
            print('Server receive string error!')
            print(err)
            conn_dict[addr].sendall('exit'.encode('utf-8'))
            conn_dict[addr].close()             # 关闭与该地址的客户端的连接
            conn_dict.pop(addr)                 # 移除记录
            print(addr, 'close!')
            break

def recs():
    while 1:
        client_sock, client_address = server.accept()
        if str(client_address) not in conn_dict:
            conn_dict.update({str(client_address): client_sock})
        print('Connect from:', str(client_address))
        t = threading.Thread(target=tcplink, args=(client_sock, str(client_address)))  # 每连接一个客户端就创建一个线程用于接收
        t.start()

def close_all_connection(send_exit=False):
    if send_exit:
        for each_address in conn_dict.keys():
            conn_dict[each_address].sendall('exit'.encode('utf-8'))    # 发送给所有客户端关闭连接
    while 1:
        time.sleep(1)
        if len(conn_dict) == 0:  # 等待所有与客户端的连接关闭
            break  # 结束线程
        else:
            print(str(len(conn_dict)), 'connection not close!')
    print('Server sender close!')
    time.sleep(1)
    server.close()
    print('server close!')
    os.kill(os.getpid(), signal.SIGTERM)  # 结束程序

def send():
    while 1:
        try:
            input_str = input()
            for each_address in conn_dict.keys():
                conn_dict[each_address].sendall(input_str.encode('utf-8'))
            if input_str == 'exit':
                close_all_connection(send_exit=False)
                break
        except EOFError:
            print('EOF error exit!')
            close_all_connection(send_exit=True)
            break
        except Exception as err:
            print('Server send string error!')
            print(err)
            close_all_connection(send_exit=True)
            break


if __name__ == '__main__':
    t1 = threading.Thread(target=recs, args=())
    t2 = threading.Thread(target=send, args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    server.close()
    print('Server Close!')
    print('EXIT')
