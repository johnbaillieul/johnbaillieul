#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import numpy as np

class Nodo():
    def __init__(self):
        # Params
        self.image = None
        self.br = CvBridge()
        # Node cycle rate (in Hz).
        self.loop_rate = rospy.Rate(1)
        # Publishers
        self.pub = rospy.Publisher('extereme_left_img', Image,queue_size=10)
        # Subscribers
        rospy.Subscriber("/realsense/depth/image_rect_raw",Image,self.callback)

    def callback(self, msg):
        rospy.loginfo('Image received...')
        self.image = self.br.imgmsg_to_cv2(msg)

    def start(self):
        rospy.loginfo("Timing images")
        #rospy.spin()
        while not rospy.is_shutdown():
            rospy.loginfo('publishing image')
            #br = CvBridge()
            if self.image is not None:
                self.pub.publish(self.br.cv2_to_imgmsg(self.image[0:120, 0:130],encoding='32FC1'))
            self.loop_rate.sleep()

if __name__ == '__main__':
    rospy.init_node("imagetimer111", anonymous=True)
    my_node = Nodo()
    my_node.start()