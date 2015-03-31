import boto
import boto.ec2
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto.ec2.cloudwatch
import boto.cloudtrail
from boto.ec2.cloudwatch import MetricAlarm
import boto.sns
import datetime
import boto.utils
import argparse
import sys
import json
import gzip
import StringIO

key_id = "AKIAIK5DOQ5FI55STIVA"
secret_key = "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"

#The variable region is set when get_region returns a boto RegionInfo object when passed a region string and key parameters
region = boto.ec2.get_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)

#The variable conn is set to an Amazon EC2 connection object by passing the key, secret key and region object to the boto.connect_ec2 method
conn = boto.connect_ec2(aws_access_key_id=key_id,aws_secret_access_key=secret_key,region=region)

#Set up Argparse object
parser = argparse.ArgumentParser()
#Populate the parser with optional arguments using the add_argument method
parser.add_argument("-i", "-id", dest="listId", help="List the instance IDs", action="store_true")
parser.add_argument("-tp", "-type", dest="listType", help="List the instance types", action="store_true")
parser.add_argument("-r", "-region", dest="listRegion", help="List the instance regions", action="store_true")
parser.add_argument("-tm", "-time", dest="listTime", help="List the instance launch times", action="store_true")
#Invoke the parse_args method to convert the arguments into an object with the specified attributes
args = parser.parse_args()				
				
def monitorRunning():
	
	#Counter variable only used for display purposes
	i = 0
	print "\nRunning AWS EC2 instances:\n"	
	
	#Iterate through the list of reservation objects returned by get_all_reservations()
	#This method returns a list of all EC2 instance objects
	for reservation in conn.get_all_reservations():
		#Iterate through each instance in reservation.instances and determine if they are running
		for instance in reservation.instances:
			#If their state is set to 'running' then print out the instance details
			if instance.state == u'running':	
				#If no arguments are passed then display all information				
				if not len(sys.argv)>1:
					print i, ":", instance.id, "-", instance.instance_type, "(",  instance.region, ")  : (Running since:", instance.launch_time, ")"
				else:	
					#print out the details based on passed argument flags
					print "\n",i,
					if args.listId:
						print ":", instance.id,
					if args.listType:
						print ":", instance.instance_type,
					if args.listRegion:
						print ": (", instance.region, ")",
					if args.listTime:
						print ": (Running since:", instance.launch_time, ")"				
				i +=1

#Method to list all S3 buckets	
def listBuckets():
	#An S3 connection object is constructed by passing in the key and secret key variables
	s3_conn = S3Connection(key_id,secret_key)
	#Buckets is set to point to the list of bucket objects returned from .get_all_buckets
	buckets = s3_conn.get_all_buckets()
	#iterate through the list of buckets and print out the details
	print "\n\nCurrent AWS S3 Buckets:\n"
	for bucket in buckets:				
		#Print out the bucket name and creation date attributes
		print "\n\tName: ", bucket.name, "Created: ", bucket.creation_date

#Method to set up clod watch monitoring and sns metric alarms			
def setAlarm():	
	#An SNS connection object is created by passing the region, key and secret key to the connection_to_region() method
	sns = boto.sns.connect_to_region('eu-west-1',aws_access_key_id=key_id, aws_secret_access_key=secret_key )
	#An cloudwatch connection object is created by passing the region, key and secret key to the connection_to_region() method
	cw = boto.ec2.cloudwatch.connect_to_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)
	
	print "\nEnabling Cloudwatch monitoring on running instances..\n"
	
	#Invoke the get_all_topics method to return a dictionary containing all topic arns on the account
	topics = sns.get_all_topics()
	
	#Get the first [0] topic arm from the dictionary
	topic = topics[u'ListTopicsResponse']['ListTopicsResult']['Topics'][0]['TopicArn']
	
	emailAddr = raw_input("Please enter an email address to receive alarm notifications: ")
	
	#emailAddr = "alloyddesign@gmail.com" 
	
	print "\nSNS email address set to %s\n" % emailAddr	
	#Iterate through the list of reservation objects returned by get_all_reservations()
	#This method returns a list of all EC2 instance objects
	for reservation in conn.get_all_reservations():
		#iterate through all instances in reservation
		for instance in reservation.instances:	
			#Set boolean to alert use if no running instances found
			any_running = False
			
			#for any instances that have their state set to running			
			if instance.state == u'running':
				#Call the monitor_instance method on the EC2 connection object with the specified instance id to enable monitoring
				conn.monitor_instance(instance.id)
				
				alarm_name = 'CPU Utilization < 40 for instance: %s' %instance.id 
				#Set the dimensions for the alarm using the current instance id
				alarm_dimensions = {"InstanceId": instance.id}		
				#Set up the alarm by passing in relevant arguments to the Metric alarm method
				#Notable arguments would be threshold being the % to check against and dimensions being the instances to activate the alarm on
				alarm = MetricAlarm(name = alarm_name, comparison='<', threshold=40, period=300, evaluation_periods=2,namespace='AWS/EC2', metric='CPUUtilization', statistic='Average', alarm_actions=[topic], dimensions = alarm_dimensions)
				#Create the alarm
				cw.create_alarm(alarm)
				print "Alarm set for instance: %s" % instance.id
				#Subscribe to the alarm using the specified email address and the email protocol
				sns.subscribe(topic, "email", emailAddr)
				any_running = True;
			if not any_running:
				print "\nNo running instances found. No alarm set."
				
def getCloudTrail():
	#A cloudtrails connection object is created by passing the region, key and secret key to the connection_to_region() method
	ctconn = boto.cloudtrail.connect_to_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)
	
	#An S3 connection object is constructed by passing in the key and secret key variables
	s3_conn = S3Connection(key_id,secret_key)
	#Buckets is set to point to the list of bucket objects returned from .get_all_buckets
	buckets = s3_conn.get_all_buckets()
	
	#describe_trails returns a dictionary of information relating to the cloudtrail on the connected account
	trail =  ctconn.describe_trails()
	#If no cloudtrail is active on this account in this region alert user
	if trail == "":
		#Validating a bucket name and related availability checks to set up a cloudtrails bucket would have been a bit much to get done so advise user to set it up manually. 
		#The name of the bucket you create must be entered into the getCtRecent method below once created.		
		print "No cloudtrail found for this region on this account.\nPlease set one up from the AWS dashboard."		
	else:
		input = 1
		while True:
			input = raw_input("\n\nCloudtrail found\n\nWhat would you like to do?\n\n 1. Start\n 2. Stop\n 3. View recent activity\n 4. Check for unauthorised access\n 0. Back\n\n > ").lower()
			if input in ("1", "start"):
				#Start cloudtrails logging on the account
				ctconn.start_logging('Default')
			elif input in ("2", "stop"):
				#Stop cloudtrails logging on the account
				ctconn.stop_logging('Default')
			elif input in ("3", "view"):
				#Pass the buckets list to the method checkRecent
				getCtRecent(buckets)
			elif input in ("4", "u", "unauthorised"):
				#Pass the buckets list to the method checkLogs
				checkLogs(buckets)
			elif input in ("exit", "e", "b", "back", "0"):
				return
			else:
				print "\nInvalid option!"

#Method to display recent cloudtrails logs and check for unauthorised access				
def getCtRecent(buckets):	
	
	#Set the name of your cloudTrails bucket
	ct_name = "cloudtrailadam"
	
	for bucket in buckets:			
		#Iterate through buckets and find the cloudtrail bucket
		if bucket.name == ct_name:
			#Iterate though all keys in the bucket such that "key" points to the last one
			#which is the last created log file
			for key in bucket:
				pass
			#Construct an empty StringIO buffer object
			f = StringIO.StringIO()
			#Using the boto s3 method get_file, retrieve the file from the S3 key and place the data in the StringIO buffer
			key.get_file(f)
			#Set the position of the read/write pointer to the beginning of the file
			f.seek(0, 0)
			#Construct a new GzipFile object and pass it the file object contained in the StringIO buffer f
			gzfile = gzip.GzipFile(fileobj=f)
			#get the data from the file using pythons .read method
			data = gzfile.read()
			
			print "\nRecent Activity:\n-------------------------------------------------------------------"
			#Pass the data to the .loads method in the json library which returns an object 
			j = json.loads(data)
			#Set the parent key from the JSON to look for keys within the main key
			parent = j["Records"]
			#Iterate through the parent key 
			for item in parent:
				#print out relevant key values
				print item["sourceIPAddress"], item["userIdentity"]["type"], item["userIdentity"]["accountId"], item["eventName"], item["eventTime"]
					
			print "--------------------------------------------------------------------\n"
				
#Parses all keys in the cloudtrails bucket and checks all events against a given account ID to check for unauthorised access			
def checkLogs(buckets):
	
	#Set ignored id list, add your own account ID here
	ignoredId = []
	
	#Static email address for testing
	#emailAddr = "alloyddesign@gmail.com" 

	#Set the name of our cloudTrails bucket
	ct_name = "cloudtrailadam"
	
	for bucket in buckets:			
		#Iterate through buckets and find the cloudtrail bucket
		if bucket.name == ct_name:
			#Iterate though all keys in the bucket such that key points to the last one
			#which is the last created log file
			for key in bucket:
				#Check if key is a file and not a folder by checking the end of the path
				if not key.name.endswith('/'):
					#Construct an empty StringIO object
					f = StringIO.StringIO()
					#Using the boto s3 method get_file, retrieve the file from the S3 key and place the data in the StringIO buffer
					key.get_file(f)
					#Set the position of the read/write pointer to the beginning of the file
					f.seek(0, 0)
					#Construct a new GzipFile object and pass it the file object contained in f
					gzfile = gzip.GzipFile(fileobj=f)
					#get the data from the file using pythons .read method
					data = gzfile.read()
					#Pass the data to the .loads method in the json library which returns an object 
					j = json.loads(data)
					#Set the parent key from the JSON to look for keys within the main key
					parent = j["Records"]	
					#Iterate though the json parent key again
					for item in parent:
						#If the accountId of any event does not match user specified one.
						if item['userIdentity']['accountId'] not in ignoredId: 
							print "\nAccess from unknown account: ", item['userIdentity']['accountId'],  " found!\n"
							#print the details of the event
							print "Event Details: ", item["sourceIPAddress"], item["userIdentity"]["type"], item["userIdentity"]["accountId"], item["eventName"], item["eventTime"]
							
							while(True):
								input = raw_input("\nDo you wish to ignore events from this account ID? (Y/N) ").lower()							
								if input in ('yes', 'y', 'ye'):
									#Add the event account ID to the list of ignored IDs
									ignoredId.append(item['userIdentity']['accountId'])
									break
								elif input in ('no', 'n', '0'):								
									input = raw_input("Do you wish to be notified of the first event of this ID via email? (Y/N) > ").lower()
									if input in ('yes', 'y', 'ye'):					
										#Set up email address
										emailAddr = raw_input("Please enter an email address to receive alarm notifications: ")
										#Create SNS connection
										sns = boto.sns.connect_to_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)
										#Pull all of the topic ARNs on the account and store them in topics
										topics = sns.get_all_topics()
										#Get the first topic ARN and store it in topic
										topic = topics[u'ListTopicsResponse']['ListTopicsResult']['Topics'][0]['TopicArn']
										#Set up email message body to contain event information
										msg = "Event details -  Source IP: " + str(item["sourceIPAddress"]) + " :  Account ID: " + str(item["userIdentity"]["accountId"]) + " :  Event type: " + str(item["eventName"]) + " :  Event time: " +  str(item["eventTime"])
										#Set up email message subject
										subject = "Unauthorised account access"
										#Public this message to SNS
										sns.publish(topic, msg, subject)
										#Subscribe to the alarm using the specified email address and the email protocol
										sns.subscribe(topic, "email", emailAddr)
										#Add ID to ignored list to continue checking for other unauthorised accounts
										ignoredId.append(item['userIdentity']['accountId'])
										break
									elif input in ('no', 'n', '0'):
										break
									else:
										print "Invalid command"
								else:
									print "Invalid command"
					
	print "\n\nCheck complete\n"
					
		
		