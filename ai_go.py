import socket
from imp import C_EXTENSION
from typing_extensions import Self
import walk
import time

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
    motion_time = 0
    while True:
        time.sleep(0.002)
        motion_time += 1
        Middle = cv_m()
        if (motion_time >= 165 and motion_time < 180):
            state = walk_1.stop_walk()
        elif (motion_time >= 180 and motion_time < 190):
            state = walk_1.robot_pose(-1.5,0.0,0.0,0.0)
        elif (motion_time >= 460 and motion_time < 485):
            state = walk_1.forward_walk(1,0)      #直行
        elif (motion_time >= 485):
            state = walk_1.stop_walk()      #直行

        #运动判断
        elif(Middle == b'0'): 
            state = walk_1.forward_walk(1,0.2)      #直行
        #向左修正，(直行速度，旋转，侧向)
        elif(Middle == b'-1'):
            state = walk_1.leftRotate_walk(0.8,0.5,0.1)
        elif(Middle == b'-2'):
            state = walk_1.leftRotate_walk(0.8,0.8,0.1)
        #向右修正，(直行速度，旋转，侧向)
        elif(Middle == b'1'):
            state = walk_1.rightRotate_walk(0.8,-0.5,-0.1)
        elif(Middle == b'2'):
            state = walk_1. rightRotate_walk(0.8,-0.8,-0.1)
        
        elif(Middle == b'-3'):
            state = walk_1. stop_walk()
        elif(Middle == b'3'):
            state = walk_1. Robot_rightRotate()
        print("偏移",motion_time)
main()