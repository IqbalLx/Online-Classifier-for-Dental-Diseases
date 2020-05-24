#!/usr/bin/python3
import io
import threading, os, signal
import picamera
import logging
import socketserver
from evdev import InputDevice
from select import select
from threading import Condition
from http import server
import subprocess
from subprocess import check_call, call
import sys
import glob

ipath = "/home/pi/Documents/live.py"    #CHANGE THIS PATH TO THE LOCATION OF live.py

def thread_second():
    call(["python3", ipath])

def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        print(fields)
        pid = fields[0]
        print(pid)
        os.kill(int(pid), signal.SIGKILL)

# store mouse event listener
eventNum = 0;
print("Finding mouse...")

# loop through all events and find mouse: Logitech M325
for i in range(20):
    devFind = str(InputDevice('/dev/input/event' + str(i)))
    devData = devFind.split(',')
    if devData[1] == ' name "Logitech M325"':    #CHANGE THE DEVICE NAME TO THE ONE YOU ARE USING
        eventNum = devData[0][-1]
        print("Device found. Event Number: " + eventNum)
        break

# store mouse event listener
dev = InputDevice('/dev/input/event' + eventNum)

# run script continuosly
while True:

    # whatever this is for the mouse
    r,w,x= select([dev],[],[])

    # check all event listeners for all devices (i.e. mouse, etc.)
    for event in dev.read():

        # check if left mouse button is pressed
        if event.code == 272:     #CHANGE THE EVENT CODE TO YOUR DEVICE BUTTON CODE

            # only activate code when button is pressed (not released)
            if event.value == 1:

                # end livestream
                check_kill_process('live.py')
                print("Stream ended.")

                # get last image number in usb drive
                pictures = glob.glob('/media/pi/4GB DRIVE/*.jpg')     #CHANGE PATH TO YOUR USB THUMBDRIVE

                # default picture number to zero
                picNum = 0

                # determine the picture number
                if not pictures == []:
                    numPics = len(pictures)
                    lastPic = pictures[numPics-1]
                    lastPicData = lastPic.split('/')
                    sudoLen = len(lastPicData)
                    jpgFile = lastPicData[sudoLen-1]
                    jpgData = jpgFile.split('.')
                    picNum = jpgData[0]
                    picNum = int(picNum) + 1
                else:
                    picNum = 1

                # take picture with camera
                with picamera.PiCamera() as camera:

                    #change resolution to get better latency
                    camera.resolution = (640,480)
                    camera.capture("/media/pi/4GB DRIVE/" + str(picNum) + ".jpg")     #CHANGE PATH TO YOUR USB THUMBDRIVE

                # alert picture taken
                print("Picture taken. Stored in thumbdrive: " + str(picNum) + ".jpg")

                # run live stream again
                processThread = threading.Thread(target=thread_second)
                processThread.start()
                print("Stream running. Refresh page.")

        # when middle mouse button is pressed, shutdown raspberry pi
        elif event.code == 274:      #CHANGE THIS TO YOUR DESIRED BUTTON

            if event.value == 1:
                call("sudo nohup shutdown -h now", shell=True)
                print("Shutting down...")

                break

# print in the command line instead of file's cons
if __name__ == '__main__':
    main()
