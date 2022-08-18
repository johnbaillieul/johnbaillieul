#!/usr/bin/env python

#import the dependencies
 
import rospy
from geometry_msgs.msg import Twist, Pose, TwistStamped
from apriltag_ros.msg import AprilTagDetectionArray
import transformation_utilities as tu
import numpy as np
import tf2_ros
import tf.transformations 
import tf2_geometry_msgs
from std_msgs.msg import Float64
from gazebo_msgs.srv import GetModelState, GetModelStateRequest
from nav_msgs.msg import Odometry



class Input_Differential:
    def __init__(self):
        self.tfBuffer = tf2_ros.Buffer()
        self.listener = tf2_ros.TransformListener(self.tfBuffer)
        self.sub_img_detec =  rospy.Subscriber("/tag_detections", AprilTagDetectionArray, self.apriltag_callback)
        self.selected_id = None
        self.x_position = None
        self.y_position = None
        self.aptag = None
        self.sub_odom =  rospy.Subscriber("/my_odom", Odometry, self.odom_callback)

    def get_rot_matrix_aptags(self):
        rospy.wait_for_service('/gazebo/get_model_state')
        get_model_srv = rospy.ServiceProxy('/gazebo/get_model_state',GetModelState)
        model = GetModelStateRequest()
        model.model_name = 'apriltag1'
        result = get_model_srv(model)
        self.aptag_transf = tu.msg_to_se3(result.pose)
    
    def apriltag_callback(self,msg):
        if msg.detections:
            # print(msg.detections)
            # '''If there's an AprilTag in the image'''
            min_distance = np.inf
            selected_apriltag = []
            for at in msg.detections:
                dist = np.linalg.norm([at.pose.pose.pose.position.x, at.pose.pose.pose.position.y, at.pose.pose.pose.position.z])
                if dist < min_distance:
                    min_distance = dist
                    self.selected_id = at.id[0]
                    selected_apriltag = at.pose.pose
            
            #change frame from camera to baselink
            source_frame = "front_realsense_gazebo"
            transform = self.tfBuffer.lookup_transform("base_link", source_frame, rospy.Time(0), rospy.Duration(1.0))
            pose_transformed = tf2_geometry_msgs.do_transform_pose(selected_apriltag, transform)
            ''' convert the stamped message '''
          
            self.aptag_transf = tu.msg_to_se3(pose_transformed.pose)
            print('1',self.aptag_transf)
        else:
            self.selected_id = None

    def odom_callback(self,msg):
        if msg:

            self.x_position = msg.pose.pose.position.x
            self.y_position = msg.pose.pose.position.y
            # se3
            jack = tu.msg_to_se3(msg.pose.pose)
            if self.aptag_transf is not None:
                print('odom_pose',jack - self.aptag_transf)
if __name__ == "__main__" :
    rospy.init_node("test")

    #  jackal = Jackal(K_gains)
    jackal = Input_Differential()
    jackal.get_rot_matrix_aptags()
    r = rospy.Rate(10)
    while not rospy.is_shutdown():
	r.sleep() 
 
