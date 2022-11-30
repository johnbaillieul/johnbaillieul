#!/usr/bin/env python3

#import the dependencies
import rospy
from geometry_msgs.msg import Twist, Pose, TwistStamped
from apriltag_ros.msg import AprilTagDetectionArray
import transformation_utilities as tu
import numpy as np
import tf2_ros 
import tf2_geometry_msgs
import os
from std_msgs.msg import Float64, Header
import pandas as pd
from gazebo_msgs.srv import GetModelState, GetModelStateRequest
import copy
import math

class Feedback_2D_Input:
    def __init__(self,K_gains): 
        self.pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        # self.linear_vel =  rospy.Subscriber("/linear_vel", Float64, self.linear_vel_callback)
        self.sub_img_detec =  rospy.Subscriber("/tag_detections", AprilTagDetectionArray, self.apriltag_callback)
        self.vel = Twist()
        self.tfBuffer = tf2_ros.Buffer()
        self.listener = tf2_ros.TransformListener(self.tfBuffer)
        self.apriltags_list = list()
        self.K_gains = np.array(K_gains)
        # self.K_added = np.array(K_added)
        self.k_index = 0
        # self.u_input = None]
        self.selected_apriltag = None
        self.selected_aptag_id = None
        self.old_vel = None
        # self.used_apriltags = [0,1,2,3,4,5,6,7,8,9,10,11] # add the apriltag ids that you used
        self.apriltag_dist = None
        self.position_landmark_inworld_matrix = {1:np.array([[0,0,1,-8.3137],[1,0,0,-5.89405],[0,1,0,0.5],[0,0,0,1]]),
                                                 2:np.array([[0,0,1,-8.25174],[1,0,0,-1.70236],[0,1,0,0.5],[0,0,0,1]]),
                                                 3:np.array([[0,1,0,-8.20742],[1,0,0,1.44827],[0,1,0,0.5],[0,0,0,1]]),
                                                 4:np.array([[1,0,0,-5.59215],[0,0,-1,3.13622],[0,1,0,0.5],[0,0,0,1]]),
                                                 5:np.array([[1,0,0,-2.523],[0,0,-1,3.28701],[0,1,0,0.5],[0,0,0,1]]),
                                                 6:np.array([[0,0,-1,1.29401],[-1,0,0,1.90886],[0,1,0,0.5],[0,0,0,1]]),
                                                 7:np.array([[0,0,-1,1.28591],[-1,0,0,-2.18859],[0,1,0,0.5],[0,0,0,1]]),
                                                 8:np.array([[0,0,-1,1.24712],[-1,0,0,-6.21105],[0,1,0,0.5],[0,0,0,1]]),
                                                 9:np.array([[-1,0,0,-2.48163],[0,0,1,-8.77517],[0,1,0,0.5],[0,0,0,1]]), 
                                                 10:np.array([[-1,0,0,-5.67756],[0,0,1,-8.7319],[0,1,0,0.5],[0,0,0,1]]),
                                                 11:np.array([[0,0,-1,-4.03817],[-1,0,0,-5.24104],[0,1,0,0.5],[0,0,0,1]]),
                                                 12:np.array([[0,0,-1,-4.16755],[-1,0,0,-2.12336],[0,1,0,0.5],[0,0,0,1]]),    
                                                 13:np.array([[0,0,1,-2.11855],[1,0,0,-2.11572],[0,1,0,0.5],[0,0,0,1]]),
                                                 14:np.array([[0,0,1,-2.06867],[1,0,0,-4.1917],[0,1,0,0.5],[0,0,0,1]]),
                                                }
 
    def apriltag_callback(self,msg):
        if msg.detections:
            # '''If there's an AprilTag in the image it selectes the one closest to the apriltag '''
            min_distance = np.inf
            for at in msg.detections:
                dist = np.linalg.norm([at.pose.pose.pose.position.x, at.pose.pose.pose.position.y, at.pose.pose.pose.position.z])
                if dist < min_distance:
                    min_distance = dist
                    selected_aptag_id = at.id[0]

            #change frame from camera to baselink
            source_frame = "front_realsense_gazebo"
            transform = self.tfBuffer.lookup_transform("base_link", source_frame, rospy.Time(0), rospy.Duration(1.0))
            # print('transform',tu.msg_to_se3(transform))
           
            self.selected_apriltag = np.dot(tu.msg_to_se3(transform),tu.msg_to_se3(at.pose.pose.pose))

            # print('id',selected_aptag_id)
            # print('pose',tu.msg_to_se3(at.pose.pose.pose))
            # print('apriltag',self.selected_apriltag)
            self.selected_aptag_id = selected_aptag_id 
            print('ap_id',self.selected_aptag_id)
        else:
            rospy.logwarn("Can't find an AprilTag in the image!")
            self.selected_apriltag = None
            self.selected_aptag_id = None

    ## compute u using only one apriltag then check how you can include multipe apriltags
    def compute_u(self): # n = num of aptags seen K=[2n,?] y = [2n,1]
        ### eq u = sum_j [K_j(l_i - x)] + sum_j [K_j(l_j - li)]
        if self.selected_apriltag is not None:
            selected_id = self.selected_aptag_id
            print("u_id",selected_id)
            selected_aptag = self.selected_apriltag
            # print("u_ap",selected_aptag)

            K_gains = self.K_gains[self.k_index*2:self.k_index*2+2,:]
            ## print("from_get_state", from_get_state)
            ori_ldmark = np.dot(self.position_landmark_inworld_matrix[selected_id][:3,:3], (selected_aptag[:3,:3]).T)
            ## Rotate the relative distance:
            aptag_dist_vector = np.dot(ori_ldmark, selected_aptag[:3,3])[:2].reshape((2,1)); 
            self.apriltag_dist = aptag_dist_vector
            u_1 = None
            for i in range(int(np.size(K_gains,1)/2)):
                if u_1 is None:
                    u_1 = K_gains[:,i*2:i*2+2].dot(aptag_dist_vector)
                else:
                    u_1  = np.hstack((u_1,K_gains[:,i*2:i*2+2].dot(aptag_dist_vector)))
            u_1 = u_1.sum(axis = 1)

            ### 2nd term in u
            ## distance between apriltags and selected tag                
            lj_li = None 
            for value in self.position_landmark_inworld_matrix.values():
                x = value[0,3] - self.position_landmark_inworld_matrix[selected_id][0,3]
                y = value[1,3] - self.position_landmark_inworld_matrix[selected_id][1,3]
                
                if lj_li is None:
                    lj_li = np.vstack((x,y))
                else:
                    lj_li = np.vstack((lj_li,x,y))
        
            u_2 = np.dot(K_gains,lj_li).sum(axis=1)
            u = u_1 + u_2
            print("u",u)
            # u = np.concatenate((u.flatten(),[0]))
            # print('u',u)
    # ##### marcs code
    #         if selected_aptag is not None:
    #             # K_gains = self.K_gains[self.k_index*2:self.k_index*2+2,:]
    #             _idx = 0
    #             u = 0
    #             for landmark_id in self.position_landmark_inworld_matrix.keys():
    #                 k = K_gains[:,_idx*2:_idx*2+2]
                
    #                 if landmark_id == self.selected_aptag_id:
    #                     for _z in range(int(np.size(K_gains,1)/2)):
    #                         # print('_z',_z)
    #                         # print('K_gains[:,_z*2:_z*2+2]',K_gains[:,_z*2:_z*2+2])
    #                         u += K_gains[:,_z*2:_z*2+2].dot(self.apriltag_dist)
    #                 else:
    #                     # We compute another term of the bias:
    #                     u += np.dot(k,self.position_landmark_inworld_matrix[landmark_id][:2,3] - self.position_landmark_inworld_matrix[self.selected_aptag_id][:2,3]).reshape((2,-1))
    #                     # print('lj-li',self.position_landmark_inworld_matrix[landmark_id][:2,3] - self.position_landmark_inworld_matrix[self.selected_apriltag][:2,3])
    #                 _idx += 1
    #                 # Finally, go back to global coordinates:
    #                 # u = self.transform_matrix[:2,:2].dot(u.flatten())
    #             u = np.concatenate((u.flatten(),[0]))
    #             print('marc',u)
            return u

    def to_tf(self,pos,ori):
        return np.block([[np.array(ori),pos.reshape((-1,1))],[0,0,0,1]])

# keep track of the unnormalized velocity when checking if it dropped less than a certain threshold
    def compute_input_parse(self):
        aptag_transf = self.selected_apriltag
        selected_id = self.selected_aptag_id

        if selected_id is None:
            if self.old_vel is not None:
                self.pub_vel.publish(self.old_vel) 
                print("Didn't update velocities1...")
                return 
            else:
                print("Didn't update velocities2...")
                return
        threshold = 0.001
        u_input = self.compute_u()
        self.old_u = copy.deepcopy(u_input)
        # print('ulen',len(u_input))

        ori = self.robot_pose(aptag_transf,selected_id)
        # ori[1] = - ori[1]
        alpha = 0.8 # linear coef
        beta = 0.5 # angular coef
        
        # print('u',u_input)
        

        linear_velocity = alpha * np.dot(u_input, ori[:2])
        # print("linevel",linear_velocity)
        print("dot",np.dot(u_input, ori[:2]))
        if abs(linear_velocity) < threshold:
            if self.self.k_index != 3:
                self.k_index += 1
                # print("K_index")
            else:
                # rospy.loginfo("Finished experiment!") 
                return 

        
        if linear_velocity < 0: 
            linear_velocity = 0.5
            angular_velocity = beta*np.cross(ori,u_input/np.linalg.norm(u_input))[2]
            # print("ori", ori)
            # print("u_input",u_input)
            # print("cross",np.cross(ori,u_input/np.linalg.norm(u_input)))
        else:
            angular_velocity = beta*np.cross(ori,u_input/np.linalg.norm(u_input))[2]
            # print("ori", ori)
            # print("u_input",u_input)
            # print("cross",np.cross(ori,u_input/np.linalg.norm(u_input)))
        print('u',u_input)
        print( 'ori',ori[:2])
        self.vel.linear.x = linear_velocity/np.linalg.norm(u_input)
        print('Linear_Vel',linear_velocity/np.linalg.norm(u_input))
        self.vel.angular.z = angular_velocity 
        # print('linear_vel',  linear_velocity/np.linalg.norm(u_input), "angl vel",angular_velocity)
        self.old_vel = self.vel
        self.pub_vel.publish(self.vel) 
        
## Get the orientation from different apriltags this only gets from the closest one
    def robot_pose(self,aptag_transf,selected_id):                           
        ori = np.dot(self.position_landmark_inworld_matrix[selected_id][:3,:3],(aptag_transf[:3,:3]).T)
        print('self.position_landmark_inworld_matrix',self.position_landmark_inworld_matrix[selected_id][:3,:3])
        print('aptag_transf',aptag_transf[:3,:3])
        
        ori= ori[:3,0].flatten()
        ori[2] = 0
        print("orien",ori)
        ori/= np.linalg.norm(ori)
        return ori
    
def read_matrix(csv_dir):
    with open(csv_dir,'r') as f:
        return np.genfromtxt(f,delimiter=',')

home_dir = os.environ["HOME"]

if __name__ == "__main__":
    rospy.init_node("u_control")
    
    shared_path = os.environ["HOME"]+"/catkin_ws/src/output_feedback_controller/csv/"
    
    K_gains_path= shared_path + "K_gains_square.csv"
    K_gains = read_matrix(K_gains_path)

    # K_added_path= shared_path + "K_added.csv"
    # K_added = read_matrix(K_added_path)

    jackal = Feedback_2D_Input(K_gains)
   
    r = rospy.Rate(10)
    while not rospy.is_shutdown(): 
        jackal.compute_input_parse()
        # jackal.robot_pose(jackal.selected_apriltag, \
        # jackal.selected_aptag_id)
        # jackal.compute_u()
        # jackal.apriltag_callback()
        r.sleep()   




 

