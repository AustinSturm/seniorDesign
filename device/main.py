import apiHandler
import deviceHandler
import settings
import config
import socketServer

import sys, subprocess
import time, threading, socket

import RPi.GPIO as GPIO





def init():
    # Try to login with any creds in settings.py
    handler = None
    try:
        handler = apiHandler.HandlerBase(config.getUsername(), config.getPassword(), config.getDeviceId())
        global api
        api = handler
    except Exception as e:
        print(e)
        threading.Timer(60, init).start()

## MAIN api init

api = None
# sets api until it is available
init()

class Event():

    def __repr__(self):
        return self.command[0] + "  " + ' '.join(self.command[1])

    def __init__(self, command):
        self.command = self.cmdParse(command)
        self.method = self.command[0]
        self.args = self.command[1]

    # string command -> list (method, (arg1, arg2))
    def cmdParse(self, command):
        cmd = command.strip().split("|")
        return (cmd[0], cmd[1:])

    def run(self):
        try:
            function = getattr(EventHandler, self.method)
            print(function)
            data = function(*self.args)
            return data
        except AttributeError as e:
            print("Wrong method  ")
            print(e)
            return -2
        except:
            print(sys.exc_info()[1])
            return -1


## EventHandler for local and remote Ques
## execQ for local utilization aka SoftAP connects
## rexecQ for remote API queue
class EventHandler():
    # parses string of event to list of events. Data String -> list List event
    @staticmethod
    def eventParser(data):
        data = data.decode().split("||")
        eventList = []
        for command in data:
            eventList.append(Event(command))
        return eventList

    # takes list of events to handle
    @staticmethod
    def execQ(eventList):
        for event in eventList:
            if event.run() != -1:
                print("Failed")
            else:
                print(event)

    @staticmethod
    def init(data):
        EventHandler.execQ(EventHandler.eventParser(data))

    @staticmethod
    def rexecQ():
        # call some standard actions
        global api
        EventHandler.getLocation()
        if api:
            queue = api.getQueue_get()
            # run through queue and execute, delete event if successful
            if queue:
                for entry in queue:
                    event = Event(entry['command'])
                    # if completed successfully delete event
                    if event.run() != -1:
                        api.delEvent_delete(event['uid'])
                    else:
                        print(event.command)
        threading.Timer(30, EventHandler.rexecQ).start()

    # TODO: Add functiosn it can perform here
    # configure account settings
    def setAccount(username, password):
        pass

    # configure routes in settings
    def setRoutes(apiurl=None, rtmprelay=None):
        pass

    # settings to modify SoftAP
    def modifyAP():
        pass

    # todo: add error catching
    def addNetwork(iface, ssid, type, password=None):
        network.add_network(iface, ssid, type, password)

    # todo: add error catching
    def connectNetwork(iface, netNum):
        network.add_network(iface, netNum)

    # todo:
    def updateNetwork():
        pass

    # todo: add error catching
    def removeNetwork(iface, netNum):
        network.remove_network(iface, netNum)

    # list all available media
    def listMedia():
        pass

    # download media from device
    def getMedia():
        pass

    # toggles a camera stream | params : ("frontCamera" or "rearCamera") ("enable" or "disable"), returns pid if success
    def enableStream(camera, toggle='', remote="1"):
        cam = globals()[camera]
        if toggle.lower() == 'disable' and cam.get_status()[int(remote)]:
            return cam.killStream()
        if toggle.lower() == 'enable' and not cam.get_status()[int(remote)]:
            return cam.streamDevice()
        else:
            return -1

    # returns list of (long, lat) and send data to api
    @staticmethod
    def getLocation():
        try:
            global api
            data = deviceHandler.SensorHandler.retStatistic()
            if not (data is None):
                api.createLoc_post(data[0], data[1], 0)
            return data
        except:
            return None

    # !!!!!! for debug only, REMOVE IN PRODUCTIONS !!!!!!!
    def backdoor(*args):
        try:
            proc = subprocess.run(args[0], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return proc.stdout
        except:
            print(proc.stderr)
            return -1

frontCamera = deviceHandler.StreamHandler('/dev/video0', api)
rearCamera = deviceHandler.StreamHandler('/dev/video1', api, direction=False)

network = deviceHandler.NetworkHandler()

# trigger pin setup
ARD_TRIGGER_PIN = 11
GPIO.setmode(GPIO.BCM)
GPIO.setup(ARD_TRIGGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
ard_timestamp = time.time()

# Triggers both cameras, push an alert to the api server
def ardTrigger(channel):
    global ard_timestamp
    ard_timestamp = time.time()
    print("Event Triggered ardTrigger")
    #send aleert to api
    #TODO: change alertType and alertDetails based on function
    alertType = "Arduino Trigger"
    alertDetails = "Extenuous event occured and triggered. Check vehicle."
    if api:
        api.createAlert_post(alertType, alertDetails)
    # enable cams
    frontCamera.enableCamera()
    rearCamera.enableCamera()

# listen for interrupt on ard trigger pin
GPIO.add_event_detect(ARD_TRIGGER_PIN, GPIO.RISING, callback=ardTrigger, bouncetime=60000)

# runs through event queu every 30 secs
EventHandler.rexecQ()
# start local socket server, which handles socket cmdParse
server = socketServer.BaseServer(EventHandler)
threading.Thread(target=server.socketServer).start()
