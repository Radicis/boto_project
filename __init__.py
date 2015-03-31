#!/usr/bin/python

import boto
import boto.ec2
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto.ec2.cloudwatch
import datetime
import boto.utils
import argparse
import sys 