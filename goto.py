#!/usr/bin/env python
#
# Name: Hiteshi Shah (hss7374)
# Homework 2
#

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import sys
import rospkg 

twist = Twist()
index = 0
positions = None
sub = None

def callback(msg, args):
	global index

    	current_x = msg.pose.pose.position.x
    	current_y = msg.pose.pose.position.y

    	q = msg.pose.pose.orientation

    	current_theta = 2 * math.atan2(q.z, q.w)

    	goal_x = args[0]
    	goal_y = args[1]

	rospy.loginfo("goal x: " + str(goal_x) + " goal y: " + str(goal_y))
	rospy.loginfo("x: " + str(round(current_x, 2)) + " y: " + str(round(current_y, 2)))

    	angle_to_goal = math.atan2(goal_y - current_y, goal_x - current_x)

	if abs(angle_to_goal - current_theta) > 0.1:
	    twist.linear.x = 0.0
	    twist.angular.z = 0.2
	    rospy.loginfo("angle_to_goal: " + str(angle_to_goal) + " current_theta: " + str(current_theta))
	elif abs(goal_x - current_x) > 0.02:
	    twist.linear.x = 0.2
	    twist.angular.z = 0.0
	    rospy.loginfo("moving x: " + str(round(current_x, 2)) + " moving y: " + str(round(current_y, 2)))
	else:
	    twist.linear.x = 0.0
	    twist.angular.z = 0.0
	    rospy.sleep(5)
	    index += 1
	    rospy.loginfo("index: " + str(index))
	    if index < len(positions):
		sub[index - 1].unregister()
	    	sub.append(rospy.Subscriber('r1/odom', Odometry, callback, positions[index]))

def goto(arg1):
    rospy.init_node('goto', anonymous=True)

    rospack = rospkg.RosPack()

    global positions
    positions = []
    with open(rospack.get_path('goto') + '/' + arg1) as file:
	for line in file:
		position = list(map(float, line.split()))
		positions.append(position)

    rate = rospy.Rate(10)

    pub = rospy.Publisher('r1/cmd_vel', Twist, queue_size=10)

    global sub
    sub = []
    sub.append(rospy.Subscriber('r1/odom', Odometry, callback, positions[0]))

    while not rospy.is_shutdown():
        pub.publish(twist)
	rate.sleep()

if __name__ == '__main__':
    try:
        goto(sys.argv[1])
    except rospy.ROSInterruptException:
        pass
