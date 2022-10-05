import pyrealsense2 as rs
import numpy as np
import cv2
import socket

#------------------------配置区域---------------------------#
Middle = 3                      #UDP传输数据初始化
LR_line = [230,410]    #判断是否   左  , 右
LR_line_1 = [150,490]
WH_line = [40,40]  #消除背景    宽   , 高
Far = 372                         #对于远处的处理
#-----------------------初始化区域-------------------------#
ip_remote = '192.168.123.163' # upboard IP
port_remote = 4000 # port
# 创建套接字(用于Internet之间的通讯，数据报套接字(UPD))
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('',4000))
#摄像头初始化
cap = cv2.VideoCapture(0)     #获取视频设备
pipeline = rs.pipeline()        #配置颜色流
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)#创建窗口，指定颜色类型
pipeline.start(config)          # 开始直播
#------------------------------------------------------------#

try:
    while True:
        #------------配置区域----------#
        Left = 3
        Right = 3
        a = 0
        #-----------------------------#
        # 等待一对连贯的帧: 深度和颜色
        frames = pipeline.wait_for_frames()
        # 正常读取的视频流
        color_frame = frames.get_color_frame()  #实感相机
        ret_0,frame0 = cap.read()               #网络相机
        # #检测是否有视频
        # if not color_frame:
        #     continue
        #将图像转换为数字数组
        color_image = np.asanyarray(color_frame.get_data())
        
        #滤波
        frame1 = cv2.blur(color_image,(5,5))
        frame_0 = cv2.blur(frame0,(5,5))  #滤波
        #空间转换
        hsv = cv2.cvtColor(frame1,cv2.COLOR_BGR2HSV)
        hsv_0 = cv2.cvtColor(frame_0,cv2.COLOR_BGR2HSV)

        #颜色阈值分割，hsv的三个分量值-get remove iio-sensor -proxy
        #网络相机
        low_blue_0 = np.array([0, 0, 0])                 #低于值变为0
        high_blue_0 = np.array([20, 255, 255])           #高于值变为0
        dst_0 = cv2.inRange(hsv_0, low_blue_0, high_blue_0)     #之间变为255
        #实感相机
        #low_blue = np.array([10, 75, 30])                 #低于值变为0
        #high_blue = np.array([80, 255, 255])           #高于值变为0
        low_blue = np.array([5, 60, 125])
        high_blue = np.array([120, 255, 255]) 
        dst = cv2.inRange(hsv, low_blue, high_blue)     #之间变为255

        #去除噪点
        kerenl = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
        dst1 = cv2.morphologyEx(dst,cv2.MORPH_OPEN,kerenl)  #开运算去除外部噪点
        dst2 = cv2.morphologyEx(dst1,cv2.MORPH_CLOSE,kerenl)    #闭运算
        dst1_0 = cv2.morphologyEx(dst_0,cv2.MORPH_OPEN,kerenl)  #开运算去除外部噪点
        dst2_0 = cv2.morphologyEx(dst1_0,cv2.MORPH_CLOSE,kerenl)    #闭运算

        #查找轮廓, 必须是3个返回值
        dsta,cnts,h = cv2.findContours(dst2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        #画一条检测线
        cv2.line(frame1,(LR_line[0],0),(LR_line[0],480),(255,0,0),1)
        cv2.line(frame1,(LR_line[1],0),(LR_line[1],480),(255,0,0),1)
        cv2.line(frame1,(LR_line[0],Far),(LR_line[1],Far),(255,0,0),1)
        cv2.line(frame1,(LR_line_1[0],0),(LR_line_1[0],480),(255,0,0),1)
        cv2.line(frame1,(LR_line_1[1],0),(LR_line_1[1],480),(255,0,0),1)

        for(i,c)in enumerate(cnts):
            (x,y,w,h) = cv2.boundingRect(c)
            #消除过小区域
            isValid = (w >= WH_line[0]) and (h >= WH_line[1])
            if( not isValid):
                continue
            # 有效则计算等高线的中心
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # 在图像上绘制形状的轮廓和中心
            cv2.drawContours(frame1, [c], -1, (0, 255, 0), 2)       #轮廓绘制
            cv2.circle(frame1, (cX, cY), 5, (255, 255, 255), -1)      #绘制点
            cv2.putText(frame1, "O", (cX - 20, cY - 20),                  #绘制字符
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            if(cY <= Far):a = -3
            #是否偏移逻辑处理
            if(cX <= LR_line[0] and cX > LR_line_1[0]):Left = 1
            elif(cX <= LR_line_1[0]):Left = 2
            else: Left = 0 
            if(cX >= LR_line[1] and cX < LR_line_1[1]):Right = 1
            elif(cX >= LR_line_1[1]):Right = 2
            else: Right = 0
            #print("左右偏移",Left,Right)
        
        #中值处理
        if(a == -3):Middle = -3
        if(Left == 0 and Right ==0):Middle = 0
        elif(Left == 1):Middle = -1
        elif(Left == 2):Middle = -2
        elif(Right == 1):Middle = 1
        elif(Right == 2):Middle = 2
        else:Middle = 3

        #发送数据(数据类型，(ip，端口))
        udp_socket.sendto(bytes(str(Middle),'utf-8'),(ip_remote, port_remote))

        #显示图像
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('frame', frame1)
        cv2.imshow('dst', dst2)
        cv2.imshow('dst2',dst2_0)       #显示
        key = cv2.waitKey(5)        #等待时间

finally:
    #停止直播
    pipeline.stop()