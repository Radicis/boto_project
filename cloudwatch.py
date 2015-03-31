import boto
import boto.ec2
import boto.ec2.cloudwatch
import datetime
from boto.regioninfo import RegionInfo

key_id = "AKIAIK5DOQ5FI55STIVA"
secret_key = "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"

#The variable region is get when get_region returns a boto RegionInfo object when passed a region string and key parameters
region = boto.ec2.get_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)

#The variable conn is set to a connection object by passing the key and secret key to the boto.connect_ec2 method
conn = boto.connect_ec2(aws_access_key_id=key_id,aws_secret_access_key=secret_key,region=region)

res = conn.get_all_instances()
inst = res[0].instances[0]

inst.monitor()

cw = boto.ec2.cloudwatch.connect_to_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)
metrics = cw.list_metrics()

my_metrics = []

for metric in metrics:
	if 'InstanceId' in metric.dimensions:
		if inst.id in metric.dimensions['InstanceId']:
			my_metrics.append(metric)

print my_metrics

def enableCW():
	cw = boto.ec2.cloudwatch.connect_to_region("eu-west-1", aws_access_key_id=key_id, aws_secret_access_key=secret_key)
	i=0
	metrics = cw.list_metrics()
	for reservation in conn.get_all_reservations():
		for instance in reservation.instances:
			if instance.state == u'running':
				#cw.put_metric_data('str_namespace', 'str_metricname', 'str_or_int_value', 'str_unit_or_str_None', {'InstanceID': instance.id})
				
				#Enable monitoring for specified instance id
				conn.monitor_instance(instance.id)
				#print out the CPUutilisation stats for given instance
				print "\n\n", i, ": ", instance.id, ": CPU Utilization Statistics: "
				instanceMetrics = cw.get_metric_statistics(300,
				datetime.datetime.utcnow() - datetime.timedelta(seconds=600),
				datetime.datetime.utcnow(),
				'CPUUtilization',
				'AWS/EC2',
				'Average',
				dimensions={'InstanceId':[instance.id]}
				) 
				print instanceMetrics
					
			i+=1