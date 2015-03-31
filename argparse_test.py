import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-i", "-id", help="List the instance IDs", action="store_true")
parser.add_argument("-tp", "-type", help="List the instance types", action="store_true")
parser.add_argument("-r", "-region", help="List the instance regions", action="store_true")
parser.add_argument("-tm", "-time", help="List the instance launch times", action="store_true")
parser.parse_args()
