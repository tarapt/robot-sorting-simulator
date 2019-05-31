import sys;
import math;
import rospy;
import numpy as np;
from nav_msgs.msg import Odometry;
from geometry_msgs.msg import Pose,Twist;
from sensor_msgs.msg import LaserScan;
from tf.transformations import euler_from_quaternion;
from sorting_robot.msg import *;

class Controller:
	def __init__(self,name):
		rospy.init_node(name+'_controller',anonymous=False);
		self.pose = Pose();
		self.goal = State();
		self.velocity = Twist();
		self.laser_scan = [];
		self.theta = 0;
		self.name = name;
		self.state = "idle";
		self.possible_states = ["idle","moving","reached"];
		self.pose_subscriber = rospy.Subscriber('/'+name+'/odom',Odometry,self.odom_callback);
		self.laser_subscriber = rospy.Subscriber('/'+name+'/laser_0',LaserScan, self.laser_callback);
		self.goal_subscriber = rospy.Subscriber('/'+name+'/subgoal',Pose, self.goal_callback);
		self.reached_publisher = rospy.Publisher('/'+name+'/reached_subgoal',Int,queue_size=10);
		self.publisher = rospy.Publisher('/'+name+'/cmd_vel',Twist,queue_size=10);
		self.rate = rospy.Rate(1);

	def odom_callback(self,data):
		self.pose = data.pose.pose;
		self.theta = euler_from_quaternion([self.pose.orientation.x,self.pose.orientation.y,self.pose.orientation.z,self.pose.orientation.w])[2];

	def laser_callback(self,data):
		self.laser_scan = list(data.ranges);

	def goal_callback(self,data):
		self.goal = data;
		self.state = "moving";

	def move(self):
		kv = 1;
		kw = 1;
		i = 0;
		dg = 5;
		while(dg>0.01):
			if not rospy.is_shutdown():
				print('location(x,y),dg,i: ',self.pose.position.x,self.pose.position.y,dg,i)
				dx = self.goal.position.x-self.pose.position.x;
				dy = self.goal.position.y-self.pose.position.y;
				print("goal coordinates: ",self.goal.position.x,self.goal.position.y)
				a2g = np.arctan2(dy,dx);
				e = np.arctan2(math.sin(a2g-self.theta),math.cos(a2g-self.theta));
				dg = kv*math.sqrt(dx*dx+dy*dy);
				if(abs(e)>0.01):
					self.velocity.angular.z = kw*e;
					self.velocity.linear.x = 0.0;
				else:
					self.velocity.linear.x = kv*math.sqrt(dx*dx+dy*dy);
					self.velocity.angular.z = 0.0;
				if(min(self.laser_scan)<=0.5)
					self.velocity.linear.x = 0;
					self.velocity.angular.z = 0;
					self.publisher.publish(self.velocity);
				else:
					self.publisher.publish(self.velocity);
		
		self.rate.sleep();
		self.velocity.linear.x = 0
		self.velocity.angular.z = 0
		self.publisher.publish(self.velocity);
		return;

	def run(self):
		while not rospy.is_shutdown():
			if(self.state=="idle"):
				continue;
			elif(self.state=="moving"):
				self.move();
				self.state = "reached";
			elif(self.state=="reached"):
				self.reached_publisher.publish(1);
				self.state = "idle";
