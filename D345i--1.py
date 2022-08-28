import pyrealsense2 as rs
import numpy as np
import cv2

#配置颜色流
pipeline = rs.pipeline()
config = rs.config()
# config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

#创建窗口，指定颜色类型
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 开始直播
pipeline.start(config)

#求中心点
def center(x,y,w,h):
    x1 = int(w/2)
    y1 = int(h/2)
    cx = x + x1
    cy = y + y1
    return cx,cy

try:
    while True:

        # 等待一对连贯的帧: 深度和颜色
        frames = pipeline.wait_for_frames()

        # 正常读取的视频流
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        #将图像转换为数字数组
        color_image = np.asanyarray(color_frame.get_data())
        
        frame1 = cv2.blur(color_image,(5,5))  #滤波

        hsv = cv2.cvtColor(frame1,cv2.COLOR_BGR2HSV)    #空间转换

        #颜色阈值分割，hsv的三个分量值-get remove iio-sensor -proxy
        low_blue = np.array([10, 75, 30])                 #低于值变为0
        high_blue = np.array([80, 255, 255])           #高于值变为0
        dst = cv2.inRange(hsv, low_blue, high_blue)     #之间变为255

        #去除噪点
        kerenl = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
        dst1 = cv2.morphologyEx(dst,cv2.MORPH_OPEN,kerenl)  #开运算去除外部噪点
        dst2 = cv2.morphologyEx(dst1,cv2.MORPH_CLOSE,kerenl)    #闭运算

        #查找轮廓, 必须是3个返回值
        dst2,cnts,h = cv2.findContours(dst2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        for(i,c)in enumerate(cnts):
            (x,y,w,h) = cv2.boundingRect(c)
            #判断是否正确
            isValid = (w >= 150) and (h >= 150)
            if( not isValid):
                continue
            #有效
            cv2.rectangle(frame1,(x,y),(x+w,y+h),(0,0,255),2)   #外框绘制
            cx,cy = center(x,y,w,h)                             #中心点
            cv2.line(frame1,(cx,y),(cx,cy),(0,255,0),2)         #中心线
        
         #显示图像
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('frame', frame1)
        cv2.imshow('dst', dst2)
        key = cv2.waitKey(5)        #等待时间


finally:

    #停止直播
    pipeline.stop()