# -*- coding: utf-8 -*-
from socket import *
import threading

address = '0.0.0.0'
port = 9999
buffsize = 1024
server = socket(AF_INET, SOCK_STREAM)
server.bind((address, port))
server.listen(5)     # 最大连接数
conn_list = []
conn_dict = {}

def tcplink(sock, addr):
    while 1:
        try:
            byte_data = sock.recv(buffsize)
            if byte_data.decode('utf-8') == 'exit' or byte_data.decode('utf-8') == '':
                print('receiver close!')
                break
            print(byte_data.decode('utf-8'))
        except Exception as err:
            print('receive string error!')
            print(err)
            break

def recs():
    while 1:
        client_sock, client_address = server.accept()
        if client_address not in conn_list:
            conn_list.append(client_address)
            conn_dict[client_address] = client_sock
        print('connect from:', client_address)
        t = threading.Thread(target=tcplink, args=(client_sock, client_address))  # 在这里创建线程，就可以每次都将socket进行保持
        t.start()


def send():
    while 1:
        try:
            input_str = input()
            if input_str == 'exit':
                print('sender close!')
                break
            for each_address in conn_list:
                conn_dict[each_address].sendall(input_str.encode('utf-8'))
        except Exception as err:
            print('send string error!')
            print(err)
            break


if __name__ == '__main__':
    t1 = threading.Thread(target=recs, args=())
    t2 = threading.Thread(target=send, args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    server.close()
    print('server close!')
