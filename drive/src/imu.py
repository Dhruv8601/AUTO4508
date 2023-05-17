#!/usr/bin/python3
import rospy
from Phidget22.Phidget import *
from Phidget22.Devices.Spatial import *
import time

rospy.init_node("imu_node")

def onAlgorithmData(self, quaternion, timestamp):
	print("Timestamp: " + str(timestamp))

	eulerAngles = self.getEulerAngles()
	print("EulerAngles: ")
	print("\tpitch: " + str(eulerAngles.pitch))
	print("\troll: " + str(eulerAngles.roll))
	print("\theading: " + str(eulerAngles.heading))

	quaternion = self.getQuaternion()
	print("Quaternion: ")
	print("\tx: " + str(quaternion.x))
	print("\ty: " + str(quaternion.y))
	print("\tz: " + str(quaternion.z))
	print("\tw: " + str(quaternion.w))
	print("----------")

def run():
	spatial0 = Spatial()

	spatial0.setOnAlgorithmDataHandler(onAlgorithmData)

	spatial0.openWaitForAttachment(5000)

	spatial0.setHeatingEnabled(True)

	try:
		input("Press Enter to Stop\n")
	except (Exception, KeyboardInterrupt):
		pass

	spatial0.close()


if __name__ == "__main__":
	rate = rospy.Rate(50)

	while not rospy.is_shutdown():
		run()
		
		rate.sleep()
