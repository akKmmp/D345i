import pyrealsense2 as rs
import numpy as np
import cv2
import Unitree_Python_sdk
import socket
import time

#---------------------------配置列表---------------------------#
#判断是否   左  , 右
LR_line = [220,420]
#消除背景    宽   , 高
WH_line = [100,100]
#------------------------------------------------------------------#

#-------------------------运动初始化---------------------------#
unitree_robot = Unitree_Python_sdk.Unitree_Robot()  #调用SDK库
motion_time = 0
#------------------------------------------------------------------#


#----------------------D345i初始化配置----------------------#
#配置颜色流
pipeline = rs.pipeline()
config = rs.config()
#创建窗口，指定颜色类型
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# 开始直播
pipeline.start(config)
#------------------------------------------------------------------#
#视觉
def D345i_init():
    Left = 2
    Right = 2
    #等待一对连贯的帧: 颜色
    frames = pipeline.wait_for_frames()
    #正常读取的视频流
    color_frame = frames.get_color_frame()
    #将图像转换为数字数组
    color_image = np.asanyarray(color_frame.get_data())
    #滤波
    frame1 = cv2.blur(color_image,(5,5))
    #空间转换
    hsv = cv2.cvtColor(frame1,cv2.COLOR_BGR2HSV)
    #颜色阈值分割，hsv的三个分量值-get remove iio-sensor -proxy
    low_blue = np.array([10, 75, 30])                 #低于值变为0
    high_blue = np.array([80, 255, 255])           #高于值变为0
    #low_blue = np.array([20, 20, 75])
    #high_blue = np.array([100, 255, 255]) 
    dst = cv2.inRange(hsv, low_blue, high_blue)     #之间变为255

    #去除噪点
    kerenl = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
    dst1 = cv2.morphologyEx(dst,cv2.MORPH_OPEN,kerenl)  #开运算去除外部噪点
    dst2 = cv2.morphologyEx(dst1,cv2.MORPH_CLOSE,kerenl)    #闭运算

    #查找轮廓, 必须是3个返回值
    dst2,cnts,h = cv2.findContours(dst2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    for(i,c)in enumerate(cnts):
        (x,y,w,h) = cv2.boundingRect(c)
        #去除背景干扰
        isValid = (w >= WH_line[0]) and (h >= WH_line[1])
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
        if(cX <= LR_line[0]):Left = 1
        else: Left = 0 
        if(cX >= LR_line[1]):Right = 1
        else: Right = 0
    return Left,Right

def dog_init():
    time.sleep(0.002)
    motion_time += 1
    if (motion_time < 1000):
        state = unitree_robot.robot_dance(1)
    if (motion_time >= 1000 and motion_time < 2000):
        state = unitree_robot.quit_dance()
    if (motion_time >= 2000 and motion_time < 3000):
        state = unitree_robot.robot_walking(gaitType = 1, forwardSpeed = 0.1, sidewaySpeed = 0.0, rotateSpeed = 0.0, speedLevel = 0, bodyHeight = 0.0)
    if(motion_time >= 3000):
        state = unitree_robot.robot_pose(0.0, 0.0, 0, 0.0)

#主函数
def main():
    while True:
        Left_1,Right_1= D345i_init()
        print("左右偏移",Left_1,Right_1)
        dog_init()

main()