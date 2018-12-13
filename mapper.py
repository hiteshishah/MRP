#!/usr/bin/python
'''
Name: Hiteshi Shah (hss7374)
Homework 4
'''

import Tkinter as tk
from PIL import Image
import ImageTk
import rospy
import sys
import math
from sensor_msgs.msg import LaserScan
from p2os_msgs.msg import SonarArray
from nav_msgs.msg import Odometry


# a reasonable size? depends on the scale of the map and the
# size of the environment, of course:
MAPSIZE = 200

class Mapper(tk.Frame):    

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.master.title("I'm the map!")
        self.master.minsize(width=MAPSIZE,height=MAPSIZE)

        # makes a grey-scale image filled with 50% grey pixels
        self.themap = Image.new("L",(MAPSIZE,MAPSIZE),128)
        self.mapimage = ImageTk.PhotoImage(self.themap)

        # this gives us directly memory access to the image pixels:
        self.mappix = self.themap.load()
        # keeping the odds separately saves one step per cell update:
        self.oddsvals = [[1.0 for _ in range(MAPSIZE)] for _ in range(MAPSIZE)]

        self.canvas = tk.Canvas(self,width=MAPSIZE, height=MAPSIZE)

        self.map_on_canvas = self.canvas.create_image(MAPSIZE/2, MAPSIZE/2, image = self.mapimage)
        self.canvas.pack()
        self.pack()

	self.current_x = 0
    	self.current_y = 0

	self.current_theta = 0

    def callback(self, msg):
    	self.current_x = msg.pose.pose.position.x
    	self.current_y = msg.pose.pose.position.y

	q = msg.pose.pose.orientation

	self.current_theta = 2 * math.atan2(q.z, q.w)

    def update_image(self):
        self.mapimage = ImageTk.PhotoImage(self.themap)       
        self.canvas.create_image(MAPSIZE/2, MAPSIZE/2, image = self.mapimage)

    def odds_to_pixel_values(self,odds):
	val = odds / (1 + odds)
	if 0 <= val < 0.2:
	    return 255
	elif 0.2 <= val < 0.4:
	    return 192
	elif 0.4 <= val < 0.6:
	    return 128
	elif 0.6 <= val < 0.8:
	    return 64
	elif 0.8 <= val < 1:
	    return 0
	elif val >= 1:
	    return 0

    def laser_update(self,lmsg):

	ranges = lmsg.ranges

	angle_increment = lmsg.angle_increment

        sx = self.current_x
        sy = self.current_y

        for lrange in range(0, len(ranges), 40):
	    distance = ranges[lrange]
	    if distance > 3:
		for d in range(0, 20):
		    x1 = sx + float(d)/10 * math.cos(self.current_theta - ((320 - lrange) * angle_increment))
		    y1 = sy + float(d)/10 * math.sin(self.current_theta - ((320 - lrange) * angle_increment))
		    sx1 = int(x1*10)
        	    sy1 = int(y1*10)
		    if sy1 == 0:
			ploty = sy1 + 100
		    elif sy1 > 0:
			ploty = 100 - sy1
		    elif sy1 < 0:
			ploty = 100 + abs(sy1)
		    self.oddsvals[sx1][sy1] *= 0.9
		    self.mappix[sx1+100,ploty] = self.odds_to_pixel_values(self.oddsvals[sx1][sy1])
	    else:
		for d in range(0, int(distance)*10):
		    x1 = sx + float(d)/10 * math.cos(self.current_theta - ((320 - lrange) * angle_increment))
		    y1 = sy + float(d)/10 * math.sin(self.current_theta - ((320 - lrange) * angle_increment))
		    sx1 = int(x1*10)
        	    sy1 = int(y1*10)
		    if sy1 == 0:
			ploty = sy1 + 100
		    elif sy1 > 0:
			ploty = 100 - sy1
		    elif sy1 < 0:
			ploty = 100 + abs(sy1)
		    self.oddsvals[sx1][sy1] *= 0.9
		    self.mappix[sx1+100,ploty] = self.odds_to_pixel_values(self.oddsvals[sx1][sy1])

		for d in range(int(distance)*10, int(distance)*10 + 5):
		    x1 = sx + float(d)/10 * math.cos(self.current_theta - ((320 - lrange) * angle_increment))
		    y1 = sy + float(d)/10 * math.sin(self.current_theta - ((320 - lrange) * angle_increment))
		    sx1 = int(x1*10)
        	    sy1 = int(y1*10)
		    if sy1 == 0:
			ploty = sy1 + 100
		    elif sy1 > 0:
			ploty = 100 - sy1
		    elif sy1 < 0:
			ploty = 100 + abs(sy1)
		    self.oddsvals[sx1][sy1] *= 1.1
		    self.mappix[sx1+100,ploty] = self.odds_to_pixel_values(self.oddsvals[sx1][sy1])
	self.after(0,self.update_image)
        
    def sonar_update(self,lmsg):
	ranges = lmsg.ranges

	angles = [-90, -50, -30, -10, 10, 30, 50, 90]

	sx = self.current_x
        sy = self.current_y

	for lrange in range(len(ranges)):
	    distance = ranges[lrange]
	    start_angle = angles[lrange] - 10
	    stop_angle = angles[lrange] + 10
	    for angle in range(start_angle, stop_angle):
	        if distance > 3:
		    for d in range(0, 20):
		        x1 = sx + float(d)/10 * math.cos(self.current_theta - (angle * math.pi/180))
		        y1 = sy + float(d)/10 * math.sin(self.current_theta - (angle * math.pi/180))
		        sx1 = int(x1*10)
        	        sy1 = int(y1*10)
		        if sy1 == 0:
			    ploty = sy1 + 100
		        elif sy1 > 0:
			    ploty = 100 - sy1
		        elif sy1 < 0:
			    ploty = 100 + abs(sy1)
		        self.oddsvals[sx1][sy1] *= 0.9
		        self.mappix[sx1+100,ploty] = self.odds_to_pixel_values(self.oddsvals[sx1][sy1])
		else:
		    for d in range(0, int(distance)*10):
		        x1 = sx + float(d)/10 * math.cos(self.current_theta - (angle * math.pi/180))
		        y1 = sy + float(d)/10 * math.sin(self.current_theta - (angle * math.pi/180))
		        sx1 = int(x1*10)
        	        sy1 = int(y1*10)
		        if sy1 == 0:
			    ploty = sy1 + 100
		        elif sy1 > 0:
			    ploty = 100 - sy1
		        elif sy1 < 0:
			    ploty = 100 + abs(sy1)
		        self.oddsvals[sx1][sy1] *= 0.9
		        self.mappix[sx1+100,ploty] = self.odds_to_pixel_values(self.oddsvals[sx1][sy1])

		    for d in range(int(distance)*10, int(distance + 0.5)*10):
		        x1 = sx + float(d)/10 * math.cos(self.current_theta - (angle * math.pi/180))
		        y1 = sy + float(d)/10 * math.sin(self.current_theta - (angle * math.pi/180))
		        sx1 = int(x1*10)
        	        sy1 = int(y1*10)
		        if sy1 == 0:
			    ploty = sy1 + 100
		        elif sy1 > 0:
			    ploty = 100 - sy1
		        elif sy1 < 0:
			    ploty = 100 + abs(sy1)
		        self.oddsvals[sx1][sy1] *= 1.1
		        self.mappix[sx1+100,ploty] = self.odds_to_pixel_values(self.oddsvals[sx1][sy1])
	self.after(0,self.update_image)


def main(arg1):
    rospy.init_node("mapper")
    root = tk.Tk()
    m = Mapper(master=root,height=MAPSIZE,width=MAPSIZE)
    if arg1 == "laser":
    	rospy.Subscriber("/r1/kinect_laser/scan",LaserScan,m.laser_update)
    elif arg1 == "sonar":
    	rospy.Subscriber("/r1/sonar",SonarArray,m.sonar_update)
    elif arg1 == "both":
    	rospy.Subscriber("/r1/kinect_laser/scan",LaserScan,m.laser_update)    	
	rospy.Subscriber("/r1/sonar",SonarArray,m.sonar_update)
    rospy.Subscriber('r1/odom', Odometry, m.callback)

    root.mainloop()

if __name__ == "__main__":
    main(sys.argv[1])
