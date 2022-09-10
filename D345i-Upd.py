import pyrealsense2 as rs
import numpy as np
import cv2
import socket

#配置颜色流
pipeline = rs.pipeline()
config = rs.config()

#左右范围，320为中心，
Left_line = 220
Right_line = 420

#创建窗口，指定颜色类型
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

ip_remote = '192.168.123.161' # upboard IP
port_remote = 32000 # port

# 创建套接字(用于Internet之间的通讯，数据报套接字(UPD))
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 


# 开始直播
pipeline.start(config)

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
        
        #滤波
        frame1 = cv2.blur(color_image,(5,5))
        #空间转换
        hsv = cv2.cvtColor(frame1,cv2.COLOR_BGR2HSV)
        #颜色阈值分割，hsv的三个分量值-get remove iio-sensor -proxy
        #low_blue = np.array([10, 75, 30])                 #低于值变为0
        #high_blue = np.array([80, 255, 255])           #高于值变为0
        low_blue = np.array([20, 20, 75])
        high_blue = np.array([100, 255, 255]) 
        dst = cv2.inRange(hsv, low_blue, high_blue)     #之间变为255

        #去除噪点
        kerenl = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
        dst1 = cv2.morphologyEx(dst,cv2.MORPH_OPEN,kerenl)  #开运算去除外部噪点
        dst2 = cv2.morphologyEx(dst1,cv2.MORPH_CLOSE,kerenl)    #闭运算

        #查找轮廓, 必须是3个返回值
        dst2,cnts,h = cv2.findContours(dst2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        #画一条检测线
        cv2.line(frame1,(Left_line,0),(Left_line,480),(255,0,0),1)
        cv2.line(frame1,(Right_line,0),(Right_line,480),(255,0,0),1)

        for(i,c)in enumerate(cnts):
            (x,y,w,h) = cv2.boundingRect(c)
            #判断是否正确
            isValid = (w >= 100) and (h >= 100)
            
            if( not isValid):
                continue
                #有效
	            # 计算等高线的中心
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
	        # 在图像上绘制形状的轮廓和中心
            cv2.drawContours(frame1, [c], -1, (0, 255, 0), 2)       #轮廓绘制
            cv2.circle(frame1, (cX, cY), 5, (255, 255, 255), -1)      #绘制点
            cv2.putText(frame1, "O", (cX - 20, cY - 20),                  #绘制字符
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            #是否偏移逻辑处理
            if(cX <= Left_line):Left = 1
            else: Left = 0 
            if(cX >= Right_line):Right = 1
            else: Right = 0
            print("左右偏移",Left,Right)

        #发送数据(数据类型，(ip，端口))
        udp_socket.sendto(bytes(str(Left), 'utf-8'), (ip_remote, port_remote))

        #显示图像
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('frame', frame1)
        cv2.imshow('dst', dst2)
        key = cv2.waitKey(5)        #等待时间

finally:
    #停止直播
    pipeline.stop()