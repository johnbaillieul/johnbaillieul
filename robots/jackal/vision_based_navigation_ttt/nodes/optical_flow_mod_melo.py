#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from vision_based_navigation_ttt.msg import OpticalFlow
from cv_bridge import CvBridgeError, CvBridge
import cv2
import sys
import numpy as np

# separate keypoints in the extreme regions

################################################################################
# Extreme left and extreme right
x_init_el = 0
y_init_el = 0
x_end_el = 0
y_end_el = 0

x_init_er = 0
y_init_er = 0
x_end_er = 0
y_end_er = 0

# Left and right
x_init_l = 0
y_init_l = 0
x_end_l = 0
y_end_l = 0

x_init_r = 0
y_init_r = 0
x_end_r = 0
y_end_r = 0

# Centre
x_init_c = 0
y_init_c = 0
x_end_c = 0
y_end_c = 0

def set_limit(img_width, img_height):

    # Extreme left and extreme right
    global x_init_el
    global y_init_el
    global x_end_el
    global y_end_el
    x_init_el = 0
    y_init_el = 0
    x_end_el = int(3 * img_width / 12)
    y_end_el = int(11 * img_height / 12)

    global x_init_er
    global y_init_er
    global x_end_er
    global y_end_er
    x_init_er = int(9 * img_width / 12)
    y_init_er = 0
    x_end_er = int(img_width)
    y_end_er = int(11 * img_height / 12)

    # Left and right
    global x_init_l
    global y_init_l
    global x_end_l
    global y_end_l
    x_init_l = int(3 * img_width / 12)
    y_init_l = int(1 * img_height / 12)
    x_end_l = int(5 * img_width / 12)
    y_end_l = int(9.5 * img_height / 12)

    global x_init_r
    global y_init_r
    global x_end_r
    global y_end_r
    x_init_r = int(7 * img_width / 12)
    y_init_r = int(1 * img_height / 12)
    x_end_r = int(9 * img_width / 12)
    y_end_r = int(9.5 * img_height / 12)

    # Centre
    global x_init_c
    global y_init_c
    global x_end_c
    global y_end_c
    x_init_c = int(5.5 * img_width / 12)
    y_init_c = int(2.5 * img_height / 12)
    x_end_c = int(6.5 * img_width / 12)
    y_end_c = int(7.5 * img_height / 12)


################################################################################

def draw_optical_flow_field(gray_image, points_old, points_new, flow, dt):
    color_img = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    color_red = [0, 255, 0]  # bgr colorspace
    linewidth = 3

    #print("Old points " + str(len(points_old)))
    #print("New points " + str(len(points_new)))

    for i in range(len(points_new)):
        x_init = points_old[i, 0]
        y_init = points_old[i, 1]

        x_end = points_new[i, 0]
        y_end = points_new[i, 1]


        cv2.line(color_img, (x_init, y_init), (x_end, y_end), color_red, linewidth)

    cv2.namedWindow('Optical Flow', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Optical Flow', 600, 600)
    cv2.imshow('Optical Flow', color_img)
    cv2.waitKey(10)


################################################################################


class OFCalculator:

    def __init__(self, param):

        ########## IMPORTANT PARAMETERS: ##########
    	self.image_sub_name = "/realsense/color/image_raw"
    	self.num_ext_features = 150 
    	self.num_cen_features = 100 
        self.num__features = 150
    	self.min_feat_threshold = 1.0
    	###########################################
        # Initialize Image acquisition
        self.bridge = CvBridge()
        # Verbose
        self.show = int(param)
        # Previous Image
        self.prev_image = None
        # Previous key points
        self.prev_kps = np.array([], dtype='f')
        # Previous time instant
        self.prev_time = 0
        # Masks
        self.roi_el = np.array([])
        self.roi_er = np.array([])
        self.roi_l = np.array([])
        self.roi_r = np.array([])
        self.roi_c = np.array([])
        # Params for ShiTomasi corner detection
        # self.feature_params = dict(maxCorners=600,
        #                           qualityLevel=0.15,
        #                           minDistance=0,
        #                           blockSize=10)
        # Lucas Kanade Optic Flow parameters
        self.lk_params = dict(winSize=(15, 15),
                              maxLevel=3,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        # ORB Detector/Descriptor initialization
        self.orb_extreme = cv2.ORB_create(self.num_ext_features)
        self.orb_ = cv2.ORB_create(self.num__features)
        self.orb_center = cv2.ORB_create(self.num_cen_features)

        # To enable the tracking
        self.tracking = False

        self.min_num_features = (2*self.num_ext_features + self.num_cen_features)/2

        # Raw Image Subscriber Jackal PointGrey
        self.image_sub = rospy.Subscriber(self.image_sub_name, Image, self.callback)

        # Optical flow message Publisher
        self.optic_flow_pub = rospy.Publisher("optical_flow", OpticalFlow, queue_size=10)

    def callback(self, data):

        rospy.loginfo(rospy.get_caller_id())
        try:
            curr_image = self.bridge.imgmsg_to_cv2(data, "mono8")
        except CvBridgeError as e:
            print(e)
            return

        # Get time stamp
        secs = data.header.stamp.secs
        nsecs = data.header.stamp.nsecs
        curr_time = float(secs) + float(nsecs) * 1e-9
        frequency = 1.0 / (curr_time - self.prev_time)
        print("Frequency: " + str(frequency))

        if self.prev_image is None:
            self.prev_image = curr_image
            self.prev_time = curr_time

            set_limit(data.width, data.height)
            # creating ROI modified
            self.roi_el = curr_image[y_init_el:y_end_el, x_init_el:(x_end_el + data.width / 10)]
            self.roi_er = curr_image[y_init_er:y_end_er, (x_init_er - data.width / 10):x_end_er]
            self.roi_l = curr_image[y_init_l:y_end_l, (x_init_l - data.width / 10):x_end_l]
            self.roi_r = curr_image[y_init_r:y_end_r, x_init_r:(x_end_r + data.width /10)]
            self.roi_c = curr_image[y_init_c:y_end_c, x_init_c:x_end_c]


            keypoints_el = np.array([])
            keypoints_el = np.append(keypoints_el, self.orb_extreme.detect(self.roi_el))
            # if (x_init_el != 0) or (y_init_el != 0):
            for i in range(np.size(keypoints_el)):
                tmp = list(keypoints_el[i].pt)
                tmp[0] += x_init_el
                tmp[1] += y_init_el
                keypoints_el[i].pt = tuple(tmp)

            keypoints_er = np.array([])
            keypoints_er = np.append(keypoints_er, self.orb_extreme.detect(self.roi_er))
            # if (x_init_r != 0) or (y_init_er != 0):
            for i in range(np.size(keypoints_er)):
                tmp = list(keypoints_er[i].pt)
                tmp[0] += x_init_er
                tmp[1] += y_init_er
                keypoints_er[i].pt = tuple(tmp)
            
            keypoints_l = np.array([])
            keypoints_l = np.append(keypoints_l, self.orb_.detect(self.roi_l))
            # if (x_init_l != 0) or (y_init_l != 0):
            for i in range(np.size(keypoints_l)):
                tmp = list(keypoints_l[i].pt)
                tmp[0] += x_init_l
                tmp[1] += y_init_l
                keypoints_l[i].pt = tuple(tmp)

            keypoints_r = np.array([])
            keypoints_r = np.append(keypoints_r, self.orb_.detect(self.roi_r))
            # if (x_init_r != 0) or (y_init_r != 0):
            for i in range(np.size(keypoints_r)):
                tmp = list(keypoints_r[i].pt)
                tmp[0] += x_init_r
                tmp[1] += y_init_r
                keypoints_r[i].pt = tuple(tmp)

            keypoints_c = np.array([])
            keypoints_c = np.append(keypoints_c, self.orb_center.detect(self.roi_c))
            # if (x_end_c != 0) or (y_init_c != 0):
            for i in range(np.size(keypoints_c)):
                tmp = list(keypoints_c[i].pt)
                tmp[0] += x_init_c
                tmp[1] += y_init_c
                keypoints_c[i].pt = tuple(tmp)

            keypoints = np.array([])
            keypoints = np.append(keypoints, keypoints_el)
            keypoints = np.append(keypoints, keypoints_er)
            keypoints = np.append(keypoints, keypoints_l)
            keypoints = np.append(keypoints, keypoints_r)
            keypoints = np.append(keypoints, keypoints_c)

            if np.size(keypoints) > 0:
                p0 = cv2.KeyPoint_convert(keypoints)
                self.prev_kps = np.float32(p0.reshape(-1, 1, 2))
                self.tracking = True
            else:
                self.prev_kps = np.array([], dtype='f')
                print("Features detected: 0")
            return

        if self.tracking is False:
            print("new keyframe!")
            # creating ROI modified
            self.roi_el = curr_image[y_init_el:y_end_el, x_init_el:(x_end_el + data.width / 10)]
            self.roi_er = curr_image[y_init_er:y_end_er, (x_init_er - data.width / 10):x_end_er]
            self.roi_l = curr_image[y_init_l:y_end_l, (x_init_l - data.width / 10):x_end_l]
            self.roi_r = curr_image[y_init_r:y_end_r, x_init_r:(x_end_r + data.width /10)]
            self.roi_c = curr_image[y_init_c:y_end_c, x_init_c:x_end_c]

            keypoints_el = np.array([])
            keypoints_el = np.append(keypoints_el, self.orb_extreme.detect(self.roi_el))
            # if (x_init_el != 0) or (y_init_el != 0):
            for i in range(np.size(keypoints_el)):
                tmp = list(keypoints_el[i].pt)
                tmp[0] += x_init_el
                tmp[1] += y_init_el
                keypoints_el[i].pt = tuple(tmp)

            keypoints_er = np.array([])
            keypoints_er = np.append(keypoints_er, self.orb_extreme.detect(self.roi_er))
            # if (x_init_r != 0) or (y_init_er != 0):
            for i in range(np.size(keypoints_er)):
                tmp = list(keypoints_er[i].pt)
                tmp[0] += x_init_er
                tmp[1] += y_init_er
                keypoints_er[i].pt = tuple(tmp)
            
            keypoints_l = np.array([])
            keypoints_l = np.append(keypoints_l, self.orb_.detect(self.roi_l))
            # if (x_init_l != 0) or (y_init_l != 0):
            for i in range(np.size(keypoints_l)):
                tmp = list(keypoints_l[i].pt)
                tmp[0] += x_init_l
                tmp[1] += y_init_l
                keypoints_l[i].pt = tuple(tmp)

            keypoints_r = np.array([])
            keypoints_r = np.append(keypoints_r, self.orb_.detect(self.roi_r))
            # if (x_init_r != 0) or (y_init_r != 0):
            for i in range(np.size(keypoints_r)):
                tmp = list(keypoints_r[i].pt)
                tmp[0] += x_init_r
                tmp[1] += y_init_r
                keypoints_r[i].pt = tuple(tmp)

            keypoints_c = np.array([])
            keypoints_c = np.append(keypoints_c, self.orb_center.detect(self.roi_c))
            # if (x_end_c != 0) or (y_init_c != 0):
            for i in range(np.size(keypoints_c)):
                tmp = list(keypoints_c[i].pt)
                tmp[0] += x_init_c
                tmp[1] += y_init_c
                keypoints_c[i].pt = tuple(tmp)

            keypoints = np.array([])
            keypoints = np.append(keypoints, keypoints_el)
            keypoints = np.append(keypoints, keypoints_er)
            keypoints = np.append(keypoints, keypoints_l)
            keypoints = np.append(keypoints, keypoints_r)
            keypoints = np.append(keypoints, keypoints_c)

            if np.size(keypoints) > 0:
                p0 = cv2.KeyPoint_convert(keypoints)
                self.prev_kps = np.float32(p0.reshape(-1, 1, 2))
                self.tracking = True
            else:
                self.prev_kps = np.array([], dtype='f')
                print("Features detected: 0")
            return

                
        tracked_features, status, error = cv2.calcOpticalFlowPyrLK(self.prev_image, curr_image,
                                                                   self.prev_kps, None,
                                                                   **self.lk_params)

        # Select good points
        good_kps_new = tracked_features[status == 1]
        good_kps_old = self.prev_kps[status == 1]
        #print("len matches "+ str(len(good_kps_new)))

        if np.size(good_kps_new) < self.min_feat_threshold*np.size(self.prev_kps):
            self.tracking = False
            self.prev_kps = np.array([], dtype='f')
        elif np.size(good_kps_new) <= self.min_num_features:
            self.tracking = False
            self.prev_kps = np.array([], dtype='f')
        else:
            self.prev_kps = np.float32(good_kps_new.reshape(-1, 1, 2))
            
        # Get time between images
        dt = curr_time - self.prev_time

        # Calculate flow field
        flow = good_kps_new - good_kps_old
        # print("Flow: " + str(flow))
        # Draw the flow field
        if self.show == 1:
            draw_optical_flow_field(curr_image, good_kps_old, good_kps_new, flow, dt)
            # Publish Optical Flow data to rostopic
        msg = OpticalFlow()
        msg.header.stamp.secs = secs
        msg.header.stamp.nsecs = nsecs
    
        msg.height = data.height
        msg.width = data.width
    
        msg.dt = dt  # in msec
        msg.x = good_kps_old[:, 0]
        msg.y = good_kps_old[:, 1]
        msg.vx = flow[:, 0] / dt
        msg.vy = flow[:, 1] / dt
        self.optic_flow_pub.publish(msg)

        self.prev_image = curr_image
        self.prev_time = curr_time


# needs to be erased if using main()
def optical_flow(param):
    rospy.init_node("optical_flow", anonymous=False)
    OFCalculator(param)
    rospy.spin()


if __name__ == '__main__':
    # if len(sys.argv) > 2:
    #     parameter = str(0)
    #     print("Parameter = 1, verbose mode")
    # else:
    #     parameter = sys.argv[1]
    optical_flow('1')
