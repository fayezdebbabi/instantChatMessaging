from threading import Thread, Event
import time


class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
    	global a
        while not self.stopped.wait(3.5):
        	a=a+1
        	print "a "+str(a)
        	print " please don't forget"
        	# Timout => now you should retransmit
global a
a=0
stopFlag = Event()
thread = MyThread(stopFlag)
thread.start()

message = raw_input("Please enter your message: ")
print a
# Once we get the input we were waiting for, we stop asking the user, so we stop the thread
stopFlag.set()
print ("Merci !")

a=10

message = raw_input("Plaaaaaaaaaaaaaaaaaaa: ")
print a
# Once we get the input we were waiting for, we stop asking the user, so we stop the thread
stopFlag.set()
print ("Merci !")