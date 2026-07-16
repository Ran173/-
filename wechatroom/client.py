#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：client.py
 
import socket               # 导入 socket 模块
import threading

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host = socket.gethostname()
port = 9999
s.connect((host,port))

name = input("pls input name")

s.send(name.encode("utf-8"))

def receive_handl(sock,addr):
    while True:
        data = sock.recv(1024)
        print(data.decode("utf-8"))

receive_thread = threading.Thread(target=receive_handl,args=(s,"1"))
receive_thread.start()

while True:
    re_data = input()
    s.send(re_data.encode("utf-8"))