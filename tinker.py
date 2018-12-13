#!/usr/bin/python

import rospy
from Tkinter import *
from geometry_msgs.msg import Twist
root = Tk()
twist = Twist()
pub = rospy.Publisher('r1/cmd_vel', Twist, queue_size=10)
prompt = '      Press any w, a, or d      '
label1 = Label(root, text=prompt, width=len(prompt), bg='yellow')
label1.pack()
def key(event):
    if event.char == 'a':
        twist.linear.x = 0.0
	twist.angular.z = 0.5
	pub.publish(twist)
	rospy.loginfo(event.char)
    if event.char == 'd':
        twist.linear.x = 0.0
	twist.angular.z = -0.5
	pub.publish(twist)
	rospy.loginfo(event.char)
    if event.char == 'w':
        twist.linear.x = 0.5
	twist.angular.z = 0.0
	pub.publish(twist)
	rospy.loginfo(event.char)
root.bind_all('<Key>', key)
rospy.init_node("tinker")
root.mainloop()
