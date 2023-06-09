#!/usr/bin/python3

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Int32, Int32MultiArray, Float32MultiArray, Float32
from sensor_msgs.msg import NavSatFix

import math

rospy.init_node("scan_node")

open("/home/group1/Desktop/project/AUTO4508/catkin_ws/src/master/src/distances.txt", 'w').close()

cmd_publisher = rospy.Publisher('/scan_cmd_vel', Twist, queue_size=1)
photo_publisher = rospy.Publisher('/take_bucket_photo', Bool, queue_size=1)
scan_complete_publisher = rospy.Publisher('/scan_complete', Bool, queue_size=1)
gui_bucket_publisher = rospy.Publisher('/gui/bucket', Float32MultiArray, queue_size=1)
gui_bucket_cone_distance = rospy.Publisher('/gui/bucket_cone_distance', Float32, queue_size=1)

pose = Twist()

initial_heading = None

pose.angular.z = 0.5

taken_photo = False
target_reached = False

find_distance = None
current_target_gps = None

is_cone_detected = False

def find_bucket(data):
    global pose
    global taken_photo
    global target_reached
    global find_distance
    global is_cone_detected

    dists = data.data
    # print(dists[len(dists)//2-2:len(dists)//2+2])
    if not taken_photo and target_reached:
        for d in dists[len(dists)//2-2:len(dists)//2+2]:
            # if 2 < d < 10 or d > 1 and not is_cone_detected:
            if 8 > d > 1 and not is_cone_detected:
                print(d)
                find_distance = d
                msg = Bool()
                msg.data = True
                taken_photo = True
                photo_publisher.publish(msg)
                print("take photo while scanning")
                break

def target_reached_cb(data):
    global target_reached
    if data.data:
        target_reached = data.data

current_heading = None

bucket_pos = None

self_oriented = False

def heading_callback(data):
    global pose
    global taken_photo
    global initial_heading
    global target_reached
    global current_heading
    global bucket_pos
    global self_oriented

    current_heading = data.data

    if (not initial_heading) and target_reached:
        initial_heading = data.data
    
    if not initial_heading:
        return

    if taken_photo and bucket_pos:
        # print(initial_heading)
        if not (initial_heading - 10 < data.data < initial_heading + 10):
            pose.angular.z = 0.5
        else:
            pose = Twist()
            self_oriented = True




def gps_callback(data):
    global current_heading
    global find_distance
    global taken_photo
    global bucket_pos

    if taken_photo and find_distance:
        print(find_distance)
        dist = find_distance / 100000
        phi = current_heading / 180 * math.pi

        xdist = dist 
        ydist = 0

        x2 = math.cos(phi) * xdist - math.sin(phi) * ydist + data.longitude
        y2 = math.sin(phi) * xdist + math.cos(phi) * ydist + data.latitude

        msg = Float32MultiArray()

        msg.data = [y2, x2]

        bucket_pos = msg.data

        gui_bucket_publisher.publish(msg)

        rospy.logerr(msg.data)

def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    lat1_rad = lat1
    lon1_rad = lon1
    lat2_rad = lat2
    lon2_rad = lon2

    # Calculate the differences in latitude and longitude
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Calculate the straight-line distance using the Euclidean formula
    distance = math.sqrt(delta_lat**2 + delta_lon**2)

    return distance

def current_target_gps_cb(data):
    global current_target_gps
    global bucket_pos
    global pose
    global taken_photo
    global initial_heading
    global target_reached
    global current_heading
    global self_oriented


    if not current_target_gps:
        current_target_gps = data.data
    
    elif taken_photo and bucket_pos and self_oriented:
        dist = calculate_distance(current_target_gps[0], current_target_gps[1], bucket_pos[0], bucket_pos[1]) * 100000
        msg = Float32()
        msg.data = dist
        # rospy.logerr(f"distttttt: {dist}")
        with open("/home/group1/Desktop/project/AUTO4508/catkin_ws/src/master/src/distances.txt", 'a') as f:
            f.write(f"{dist}\n")
        gui_bucket_cone_distance.publish(dist)

        initial_heading = None
        taken_photo = False
        target_reached = False
        msg = Bool()
        msg.data = True
        bucket_pos = None
        self_oriented = False
        scan_complete_publisher.publish(msg)

        # publish distance

        current_target_gps = data.data

def cone_detected(data):
    global is_cone_detected
    is_cone_detected = data.data

if __name__ == '__main__':
    rate = rospy.Rate(500)
    rospy.Subscriber('/target_reached', Bool, target_reached_cb)
    rospy.Subscriber('/lidar_front', Float32MultiArray,  find_bucket)
    rospy.Subscriber('/imu_heading', Int32, heading_callback)
    rospy.Subscriber('/fix', NavSatFix, gps_callback)
    rospy.Subscriber('/gui/current_target', Float32MultiArray, current_target_gps_cb)
    rospy.Subscriber('/cone_detected', Bool, cone_detected)


    while not rospy.is_shutdown():
        # print(pose)
        cmd_publisher.publish(pose)

        rate.sleep()




    
