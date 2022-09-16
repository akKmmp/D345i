#!/usr/bin/python
import sys
import time
from tkinter import N
sys.path.append('/home/ak/文档/unitree_legged_sdk-3.3.2/build') # Edit the path to "build" folder on your computer
import robot_interface_high_level as robot_interface #导入robot_interface_high_level模块时指定了别名robot_interface
motion_time=0
class Unitree_Robot():#定义一个类叫宇数机器人

    unitree_robot = robot_interface.RobotInterface()#unitree_robot机器人接口
    robot_state = robot_interface.HighState()#高层状态
    
     
    def __init__(self):     #
        self.mode = 0 #
        self.gaitType = 0   #步态
        self.speedLevel = 0
        self.footRaiseHeight = 0.0
        self.forwardSpeed = 0.0  #向前后
        self.sidewaySpeed = 0.0  #向左右移动
        self.rotateSpeed = 0.0   #向左右旋转
        self.bodyHeight = 0.0   #调整站立高度指令（-1，+1；0.3，0.45 ）
        self.yaw = 0.0          #偏航（-1，+1；+-28）
        self.pitch = 0.0        #俯仰（+-20）
        self.roll = 0.0         #横滚（+-20）
        self.quit_dance_time = 0 

    def cmd_init(self):
        self.mode = 0
        self.gaitType = 0
        self.speedLevel = 0
        self.footRaiseHeight = 0.0
        self.forwardSpeed = 0.0
        self.sidewaySpeed = 0.0
        self.rotateSpeed = 0.0
        self.bodyHeight = 0.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.quit_dance_time = 0
    
    def send_UDP(self):
        self.unitree_robot.UDPSend()    #执行udpsend功能

    def recv_UDP(self):
        self.unitree_robot.UDPRecv()    #执行udprecv功能
        
    def robot_control(self):
        self.unitree_robot.robotControl(self.mode, self.gaitType, self.speedLevel,    
                                    self.footRaiseHeight, self.bodyHeight, 
                                    self.roll, self.pitch, self.yaw,
                                    self.forwardSpeed, self.sidewaySpeed, self.rotateSpeed) #机器人控制
    
    


    def robot_walking(self, gaitType = 1, forwardSpeed = 0.0, sidewaySpeed = 0.0, 
                      rotateSpeed = 0.0, speedLevel = 0, bodyHeight = 0.0, footRaiseHeight = 0.0):#机器人行走
        self.cmd_init()
        self.gaitType = gaitType #=1
        self.speedLevel = speedLevel #=0.0
        self.footRaiseHeight = footRaiseHeight  #=0.0
        self.forwardSpeed = forwardSpeed    #=0.0
        self.sidewaySpeed = sidewaySpeed    #=0.0
        self.rotateSpeed = rotateSpeed      #=0.0
        self.bodyHeight = bodyHeight        #=0.0
        self.mode = 2 #进入模式2
        robot_state = self.unitree_robot.getState()#getshate将walking数值记录下来
        self.recv_UDP()
        self.robot_control()  #运行robot_control
        self.send_UDP()
        return robot_state  #将robot_state值返回终端
    def stop_walk(self):#停止走路
        self.cmd_init()
        self.gaitType = 0
        self.mode =2
        robot_state = self.unitree_robot.getState()#getshate将walking数值记录下来
        self.recv_UDP()
        self.robot_control()  #运行robot_control
        self.send_UDP()
        return robot_state  #将robot_state值返回终端     
    def leftyaw_walk(self,forwardSpeed ):#左斜
        self.cmd_init()
        self.gaitType = 1
        self.forwardSpeed = forwardSpeed
        self.sidewaySpeed = 0.2
        self.mode =2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
        return robot_state  
    def rightyaw_walk(self, forwardSpeed):#右斜
        self.cmd_init()
        self.gaitType = 1
        self.forwardSpeed = forwardSpeed
        self.sidewaySpeed = -0.2
        self.mode =2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
        return robot_state        
    def leftRotate_walk(self,forwardSpeed,rotateSpeed,sidewaySpeed):#左转（走）
        self.cmd_init()
        self.gaitType = 1
        self.rotateSpeed =rotateSpeed
        self.sidewaySpeed = sidewaySpeed
        self.forwardSpeed = forwardSpeed
        self.mode =2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
        self.rotateSpeed = -0.6
    def rightRotate_walk(self,forwardSpeed,rotateSpeed,sidewaySpeed):#右转（走）
        self.cmd_init()
        self.gaitType = 1
        self.rotateSpeed = rotateSpeed
        self.sidewaySpeed = sidewaySpeed
        self.forwardSpeed = forwardSpeed
        self.mode =2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
    def Robot_leftRotate(self):#左转
        self.cmd_init()
        self.gaitType =1
        self.rotateSpeed =1
        self.mode = 2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
    def Robot_rightRotate(self):#右转
        self.cmd_init()
        self.gaitType =1
        self.rotateSpeed =-1
        self.mode = 2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
    def forward_walk(self,forwardSpee,rotateSpeed):#直行
        self.gaitType = 1
        self.forwardSpeed =forwardSpee
        self.rotateSpeed = rotateSpeed
        self.mode = 2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
    def a1_yaw(self):
        self.mode=2
        robot_state = self.unitree_robot.getState()
        self.recv_UDP()
        self.robot_control()
        self.send_UDP()
    def robot_pose(self, roll, pitch, yaw, bodyHeight):#机器人动作
        self.cmd_init()
        self.bodyHeight = bodyHeight    #高度
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.mode = 1
        robot_state = self.unitree_robot.getState()####
        self.recv_UDP()     #####
        self.robot_control()#####
        self.send_UDP()####
        return robot_state #####