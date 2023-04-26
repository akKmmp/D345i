import pyrealsense2 as rs
import numpy as np
import cv2
import socket
from matplotlib import pyplot as plt

#摄像头初始化
pipeline = rs.pipeline()        #配置颜色流
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)#创建窗口，指定颜色类型
pipeline.start(config)          # 开始直播  
#------------------------------------------------------------#
ip_remote = '192.168.123.163'         # IP
port_remote = 5005                              # 端口
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 配置参数
y2 =  220
y0 = 300                                    #切片中间行y位置
y1 = 380

cX = 320
cY = 380

# -----------------------------------------------------------#

def ymax_x(arry,y):            #求固定y坐标的最小x坐标
    max_value = 0
    for i in range(len(arry)):
        if arry[i,0,1] == y:
            max_value = max(max_value , arry[i,0,0])
    return max_value

def ymin_x(arry,y):            #求固定y坐标的最小x坐标
    min_value = 640
    for i in range(len(arry)):
        if arry[i,0,1] == y:
            min_value = min(min_value , arry[i,0,0])
    return min_value

try:
    while True:
        # 等待一对连贯的帧: 深度和颜色
        frames = pipeline.wait_for_frames()
        # 正常读取的视频流
        color_frame = frames.get_color_frame()
        #检测是否有视频
        if not color_frame:
            continue
        #将图像转换为数字数组
        color_image = np.asanyarray(color_frame.get_data())

        frame1 = cv2.blur(color_image,(5,5))  #滤波
        hsv = cv2.cvtColor(frame1,cv2.COLOR_BGR2HSV)    #空间转换

        #颜色阈值分割，hsv的三个分量值-get remove iio-sensor -proxy
        low_blue = np.array([5, 60, 50])
        high_blue = np.array([120, 255, 255]) 
        dst = cv2.inRange(hsv, low_blue, high_blue)     #之间变为255

        #去除噪点
        kerenl = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
        dst1 = cv2.morphologyEx(dst,cv2.MORPH_OPEN,kerenl)  #开运算去除外部噪点
        dst2 = cv2.morphologyEx(dst1,cv2.MORPH_CLOSE,kerenl)    #闭运算

        #查找轮廓
        dst2,cont, ho = cv2.findContours(dst2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE) 
        max_cont = []
        for(i,c)in enumerate(cont):
            if( not cont):
                    continue
            max_cont= max(cont,key=cv2.contourArea) #获取到了面积最大的轮廓点集
            #max_area = cv2.contourArea(max_cont)            #面积求值 
        
        #切片获取点位置
        y0max = ymax_x(max_cont,y0)
        y0min = ymin_x(max_cont,y0)
        y1max = ymax_x(max_cont,y1)
        y1min = ymin_x(max_cont,y1)
        #中值
        y0_z = np.int0((y0max + y0min)/2)
        y1_z = np.int0((y1max + y1min)/2)

        cv2.line(frame1, (y0max,y0),(y0min,y0),  (255, 255, 255), 2)      #绘制线
        cv2.line(frame1, (y1max,y1),(y1min,y1),  (255, 255, 255), 2)      #绘制线
        
        if y0_z > 0 and y1_z > 0:
                cv2.line(frame1, (y0_z,y0),(y1_z,y1),  (255, 0, 255), 2)      #绘制k线
        
        cv2.circle(frame1, (cX, cY), 5, (0, 0, 255), -1)      #绘制点
        #判断
        ret =  np.int0(round((cX - y1_z)/10))           #偏移量
        k = round((y1_z - y0_z)/(y1 - y0))                  #斜率
        print(ret,k)

        data = (ret,k)
        msg = bytes(str(data),'utf-8')
        udp_socket.sendto(msg,(ip_remote, port_remote))  

        cv2.imshow('001',frame1)
        cv2.imshow('002',dst2)

        cv2.waitKey(1)

finally:
    #停止直播
    cv2.waitKey(1) 
    udp_socket.close()