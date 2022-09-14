from imp import C_EXTENSION
import scripts.walk as walk
import numpy as np
import cv2

#---------------------------配置列表---------------------------#
#判断是否   左  , 右
LR_line = [240,400]
#消除背景    宽   , 高
WH_line = [150,150]
#------------------------------------------------------------------#

#-----------------------运动视觉初始化-----------------------#
walk_1 = walk.Unitree_Robot()  #调用SDK库
cap = cv2.VideoCapture(0)     #获取视频设备
motion_time = 0                         #时间初始化
#------------------------------------------------------------------#



def cv_m():
    Left = 2
    Right = 2
    ret,frame = cap.read()
    frame1 = cv2.blur(frame,(5,5))  #滤波
    hsv = cv2.cvtColor(frame1,cv2.COLOR_BGR2HSV)    #空间转换

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

    #查找轮廓
    dst2,cnts,h = cv2.findContours(dst2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

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

def main():
    while True:
        Left_1,Right_1= cv_m()
        print("左右偏移",Left_1,Right_1)
        if(Left_1 == 0 and Right_1 == 0): 
            state = walk_1.forward_walk()
        else:state = walk_1.robot_pose(0.0, 0.0, 0, 0.0)

main()

