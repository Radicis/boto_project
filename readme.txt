Adam Lloyd
R00117318
DWEB2

Cloud Computing with Python 
Assignment 2
30/10/2014
Amazon AWS Management Application - Readme.txt

Options
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Program accepts arguments when executing main.py to specify information to be displayed when Monitor Running Instances is selected
Options: 
	-i  (ID)
	-tp (type)
	-r (region)
	-tm (launch time)
----------------------------------------------------------------------------------------------------------------------------------------------------------------

Main menu
----------------------------------------------------------------------------------------------------------------------------------------------------------------
1. Launch an EC2 instance
	The user can choose between a windows and linux AMI to spin up
	(When I was writing this I think Amazon may have changed the AMI of the free tier Windows machine which is hard coded in the application so got an error until I updated it so if it generates an error check this image code is correct at time of testing.)

2. Monitor running instances
	A list of instances is displayed. The information displayed depends on the arguments passed to the method.

3. List S3 buckets
	A list of all S3 buckets on the AWS account are displayed

4. Enable Cloudwatch and set metric alarm
	User is prompted for an email address
	For each running instance, a Cloudwatch alarm is set to trigger when the average CPU utilisation is below 40%

5. Get cloudtrails information (See note below)
	Checks to see if there is an cloudtrail set up on the AWS account
	Displays options for start and stop logging and to view recent activity
	Recent activity parses the json based cloudtrails logs and displays a list of the recent events on the EC2 instances.  
	Check for unauthorised access prompts for an account ID then parses all of the json logs in the bucket and checks if any events are found that don't match the account IDs set up in the source code. If so then the user is alered and given the option to add he ID to the trusted list or be SNS emailed with the details of the event to follow up on it.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------

!!! I MPORTANT NOTE  !!!
Validating a bucket name and related availability checks to set up a cloudtrails bucket would have been a bit much to take on. The name of the bucket you create must be entered into the getCtRecent method below once created.

I think the functionality is interesting enough without this though as it combines S3, Sns and Cloudtrails (along with some fun with json and gzip) to provide something that could be very useful although basic in it's current state.
!!!