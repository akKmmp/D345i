import socket


upd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
upd.bind(('', 4000))  # 为服务器绑定一个固定的地址，ip和端口
    
while True:
      data,addr = upd.recvfrom(1024)
      print(addr[0])
      print(data.decode('utf-8') ) #打印接收的内容

 
 