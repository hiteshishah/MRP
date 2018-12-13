#!/usr/bin/env python
#
# Name: Hiteshi Shah (hss7374)
# Homework 3
#

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import math
import sys
import rospkg 

twist = Twist()

class GoTo:

	def __init__(self):
		self.current_x = 0
		self.current_y = 0
		self.current_theta = 0
		self.current_ranges = []
	
	def laser_callback(self, msg):
		self.current_ranges = msg.ranges

	def callback(self, msg):
	    	self.current_x = msg.pose.pose.position.x
	    	self.current_y = msg.pose.pose.position.y

	    	q = msg.pose.pose.orientation

	    	self.current_theta = 2 * math.atan2(q.z, q.w)

	def turn_to_goal(self, goal_x, goal_y):
		angle_to_goal = math.atan2(goal_y - self.current_y, goal_x - self.current_x)

		while abs(angle_to_goal - self.current_theta) > 0.1:
			self.turn_left()

	def go_to_goal(self, goal_x, goal_y):
		while abs(goal_x - self.current_x) > 0.02:
			self.go()

	def go(self):
		twist.linear.x = 0.5
		twist.angular.z = 0.0
		self.pub.publish(twist)
	
	def go_back(self):
		twist.linear.x = -0.5
		twist.angular.z = 0.0
		self.pub.publish(twist)

	def stop(self):
		twist.linear.x = 0.0
		twist.angular.z = 0.0
		self.pub.publish(twist)

	def turn_left(self):
		twist.linear.x = 0.0
		twist.angular.z = 0.5
		self.pub.publish(twist)

	def turn_right(self):
		twist.linear.x = 0.0
		twist.angular.z = -0.2
		self.pub.publish(twist)

	def stop(self):
		twist.linear.x = 0.0
		twist.angular.z = 0.0
		self.pub.publish(twist)

	def safegoto(self, arg1):
		rospy.init_node('safegoto', anonymous=True)

		rospack = rospkg.RosPack()

		positions = []

		with open(rospack.get_path('safegoto') + '/' + arg1) as file:
			for line in file:
				position = list(map(float, line.split()))
				positions.append(position)

		rate = rospy.Rate(5)

		self.pub = rospy.Publisher('r1/cmd_vel', Twist, queue_size=10)

		sub = rospy.Subscriber('r1/odom', Odometry, self.callback)

		laser_sub = rospy.Subscriber('r1/kinect_laser/scan', LaserScan, self.laser_callback)

		for position in positions:
			flag = True
			while flag:		
				self.turn_to_goal(position[0], position[1])
				if len(set(self.current_ranges[159:479])) > 1:
					distance_to_goal = math.sqrt(math.pow((position[0] - self.current_x), 2) + math.pow((position[1] - self.current_y), 2))
					if any(elem != float("inf") and elem > distance_to_goal for elem in self.current_ranges[159:479]):
						self.go_to_goal(position[0], position[1])
						self.stop()
						rospy.sleep(5)
						flag = False
					else:
						while any(elem < 1.5 for elem in self.current_ranges):
							self.go_back()
						while all(elem > 1.5 for elem in self.current_ranges):
							self.go()
						while len(set(self.current_ranges[159:479])) != 1:
							self.turn_right()
						while self.current_ranges[639] != float("inf"):
							self.go()
						start_time = rospy.get_rostime()
						while rospy.get_rostime() - start_time <= rospy.Duration(5):
							self.go()
				else:
					self.go_to_goal(position[0], position[1])
					self.stop()
					rospy.sleep(5)
					flag = False
			

if __name__ == '__main__':
    try:
        g = GoTo()
	g.safegoto(sys.argv[1])
    except rospy.ROSInterruptException:
        pass
