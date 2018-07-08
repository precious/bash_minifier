#!/usr/bin/python
# 
# $1 Bash script file to minify
#
#
 
import sys
import re
from os.path import expanduser
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename", help="Passed bash script to minify", metavar="file")

args = parser.parse_args()

fileresult = open("res.sh", "w+")

deep = -1
def readFile(filename, deep):
    deep += 1
    # Open the file
    file = open(filename.rstrip("\r\n"), "r")
    # Check if the file is in read mode
    if file.mode == "r":
        contents = file.readlines()
        for line in contents:
            lineStrip = line.strip()
            if lineStrip.startswith("source ~") or lineStrip.startswith("source /"):
                fileresult.write(line)
                lineStrip = lineStrip.replace("source ", "")
                print("[", deep, "] ", lineStrip)
                readFile(lineStrip.replace("~", expanduser("~")), deep)
            elif not lineStrip.startswith("#"):
                fileresult.write(line)
        file.close()



if __name__ == "__main__":
    readFile(args.filename.replace("~", expanduser("~")), deep)
    fileresult.close()