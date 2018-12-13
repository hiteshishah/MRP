#!/usr/bin/env python
#
# Name: Hiteshi Shah (hss7374)
# Homework 1
#

import rospy
from p2os_msgs.msg import MotorState
from geometry_msgs.msg import Twist
import sys

twist = Twist()

def stop():
    twist.linear.x = 0.0
    twist.linear.y = 0.0
    twist.linear.z = 0.0
    twist.angular.x = 0.0
    twist.angular.y = 0.0
    twist.angular.z = 0.0
    return twist

def move():
    twist.linear.x = 0.5
    twist.linear.y = 0.0
    twist.linear.z = 0.0
    twist.angular.x = 0.0
    twist.angular.y = 0.0
    twist.angular.z = 0.5
    return twist

def hw1(arg1):
    rospy.init_node('hw1', anonymous=True)
    pub1 = rospy.Publisher('cmd_motor_state', MotorState, queue_size=10)
    pub1.publish(1)

    pub2 = rospy.Publisher('r1/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(10)

    start_time = rospy.get_rostime()

    while not rospy.is_shutdown():
	if rospy.get_rostime() - start_time <= rospy.Duration(int(arg1)):
		twist = move()
	else:
        	twist = stop()
        rospy.loginfo(twist)
        pub2.publish(twist)
        rate.sleep()

if __name__ == '__main__':
    try:
        hw1(sys.argv[1])
    except rospy.ROSInterruptException:
        pass
