#!/usr/bin/python
# 
# $1 Bash script file to minify
#
#
 
import sys
from os.path import expanduser
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename", help="Passed bash script to minify", metavar="file")

args = parser.parse_args()

def readFile():
    # Open the file
    file = open(args.filename.replace("~", expanduser("~")),"r")
    # Check if the file is in read mode
    if file.mode == "r":
        contents = file.readlines()
        for line in contents:
            print(line)

if __name__ == "__main__":
    readFile()