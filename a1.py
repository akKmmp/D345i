import socket
from imp import C_EXTENSION
from telnetlib import WILL
from typing_extensions import Self
import walk
import time

#-----------------------配置区域-------------------------#
walk_1 = walk.Unitree_Robot()  #调用SDK库
Middle = [0,0]                                             #中值变量
re = [0,0]
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #UPD接收
udp.bind(('', 4000))                           # 为服务器绑定一个固定的地址，ip和端口
a = 125
go = 0.5                                                      #直行速度
#------------------------------------------------------------#

#UPD接收
def cv_m():
    data,addr = udp.recvfrom(1024)
    #print(data.decode('utf-8') ) #打印接收的内容
    data = int(data)
    if data >= 10:
        re[0] = data
    elif data >= 0 and data < 10:
        re[1] = data
    else:
        re[0] = 0
        re[1] = 0
    return re         #返回值

#主函数
def main():
    motion_time = 0
    while True:
        Middle = cv_m()
        print(Middle[0])
        #print(Middle[1])
        if (Middle[0] == 11):
            state = walk_1.stop_walk()



        #运动判断
        elif(Middle[1] == 0): 
            state = walk_1.forward_walk(go,0.1)      #直行
        #向左修正，(直行速度，旋转，侧向)
        elif(Middle[1] == -1):
            state = walk_1.leftRotate_walk(go , 0.2 ,0.1)
        elif(Middle[1] == -2):
            state = walk_1.leftRotate_walk(go , 0.4 ,0.1)
        #向右修正，(直行速度，旋转，侧向)
        elif(Middle[1] == 1):
            state = walk_1.rightRotate_walk(go, -0.2 ,-0.1)
        elif(Middle[1] == 2):
            state = walk_1. rightRotate_walk(go, -0.4 ,-0.1)
        
        elif(Middle[1] == -3):
            state = walk_1. forward_walk((0.4),-0.05)
        elif(Middle[1] == 3):
            state = walk_1. Robot_rightRotate()
main()
