import socket
import threading
import time
from datetime import datetime

addr_name = {}
all_client = []
name_client = {}
# 颜色定义
RED = "\033[31m"
END = "\033[0m"

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host = socket.gethostname()

port = 9999
server.bind((host,port))
server.listen(5)
lock = threading.Lock()

print("////////Room///////")

def handle_sock(sock,addr):
    while True:
        try:
            from_name = addr_name[str(addr)]
            data = sock.recv(1024)
            if not data:
                raise ConnectionResetError
            
            raw_msg = data.decode("utf-8")
            ts = int(time.time())
            time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            log_text = (f"[{time_str}]-{RED}{from_name}{END}:{raw_msg}")
            print(log_text)

            #查看在线用户
            if raw_msg == "/list":
                online_list_id = list(name_client.keys())
                reply = f"[{time_str}] SYSTEM ONLINE LIST:{online_list_id}"
                send_one(sock,addr,reply)
                continue

            if raw_msg == "/exit":
                raise ConnectionResetError



            if raw_msg.startswith('@'):
                index = raw_msg.find(' ')# @h后加空格
                if index == -1:
                    send_one(sock,addr,"error:@name + space")
                    continue

                to_name = raw_msg[1:index] #截取@后用户名
                to_msg = raw_msg[index:]#内容   

                #判断对方是否在线
                if to_name not in name_client:
                    send_one(sock,addr,f"user [{to_name}] not online\n")
                    continue

                to_sock = name_client[to_name]
                send_one(to_sock,addr,from_name+":"+to_msg)
            else:
                send_all(all_client,addr,f"{from_name}:{raw_msg}")
        except ConnectionResetError:
            #掉线清理资源
            exit_name = addr_name[str(addr)]
            if exit_name in name_client:
                del name_client[exit_name]
            if sock in all_client:
                all_client.remove(sock)

            #广播退出消息
            quit_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统：{exit_name} quit room"
            send_all(all_client,addr,quit_msg)
            sock.close()
            break
        except KeyError:
            send_one(sock,addr,"error\n")

        except Exception as e:
            print("thread error: ",e)
            sock.close()
            break

def send_all(socks,addr,msg):
    for sock in socks:
        sock.send(msg.encode("utf-8"))

def send_one(sock,addr,msg):
    sock.send(msg.encode("utf-8"))

while True:
    sock,addr = server.accept()
    name = sock.recv(1024).decode("utf-8")
    addr_name[str(addr)] = name
    name_client[name] = sock
    all_client.append(sock)
    hello = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SYSTEM:wellcome {RED}{name}{END} coming room"
    send_all(all_client,addr,hello)
    client_thread = threading.Thread(target = handle_sock,args=(sock,addr))
    client_thread.start()