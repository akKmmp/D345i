import socket
from imp import C_EXTENSION
import walk
import numpy as np
import cv2

#-----------------------配置区域-------------------------#
walk_1 = walk.Unitree_Robot()  #调用SDK库
Middle = 2                                             #中值变量
upd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #UPD接收
upd.bind(('', 4000))                           # 为服务器绑定一个固定的地址，ip和端口
#------------------------------------------------------------#

#UPD接收
def cv_m():
    data,addr = upd.recvfrom(1024)
    #print(data.decode('utf-8') ) #打印接收的内容
    return data         #返回值为bytes 对象，b'*'

#主函数
def main():
    while True:
        Middle = cv_m()
        print("偏移",Middle)
        #运动判断
        if(Middle == b'0'): 
            state = walk_1.forward_walk(0.2)
        elif(Middle == -1):state = walk_1.stop_walk()

main()