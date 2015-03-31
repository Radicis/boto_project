#script 1
	#list running EC2 instances
		#contains menu options -i -h etc
	#list all s3 buckets
	#enable cloudwatch monitoring on all ec2 instances
		#set alarm if cpu utilization less than 40%
			#when alarm is raised use AWS SNS to email 
				#user setup email account as a menu option
				
import boto
import boto.ec2
import time

key_id = "AKIAIK5DOQ5FI55STIVA"
secret_key = "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"

region = boto.ec2.get_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)

conn = boto.connect_ec2(aws_access_key_id=key_id,aws_secret_access_key=secret_key,region=region)				
				
def monitorRunning():
	#counter variable
	i = 0
	print "\nRunning AWS EC2 instances:\n"	
	
	#Iterate through the list of reservation objects returned by get_all_reservations()
	#Iterate through each instance in reservation.instances and determine if they are running
	#If their state is set to u'running' then print out the instance details

	for reservation in conn.get_all_reservations():
		for instance in reservation.instances:
			if instance.state == u'running':				
				print i, ":", instance.id, "-", instance.instance_type, "(",  instance.region, ")  : (Running since:", instance.launch_time, ")"
				i +=1


	
		

monitorRunning()				
				
#Script 2
	
		#create new AMI
			#prompt user for windows or linux
			#ask user how many they wish to deploy
		
		