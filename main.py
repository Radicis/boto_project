'''
Adam Lloyd
R00117318
DWEB2

Cloud Computing with Python 
Assignment 2
30/10/2014
Amazon AWS Management Application

'''

#import scripts
import list_instances
import launch_instance

title = "\n\n*****************************************************\n\n\t- Amazon AWS Management Application -\n\n   By Adam Lloyd | R00117318 | adam.lloyd@mycit.ie\n\n*****************************************************"
menu = "\n\nMain Menu\n\n 1. Launch an instance\n 2. Monitor running instances\n 3. Display buckets\n 4. Set CloudWatch Alarm\n 5. Manage CloudTrail\n 0. Exit\n\n> "

print title

while True:
	#Display Menu to user
	input = raw_input(menu)	
	if input == '1':
		launch_instance.launch_instance()
	elif input == '2':
		list_instances.monitorRunning()
	elif input == '3':
		list_instances.listBuckets()
	elif input == '4':
		list_instances.setAlarm()
	elif input == '5':
		list_instances.getCloudTrail()
	elif input == '0':
		exit(1)
	else:
		print "\nInvalid option! Please try again."


