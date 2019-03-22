import subprocess, shlex
import logging
import config
import apiHandler
import time

import struct, smbus

import socket, threading

class StreamHandler():

    # Dev is '/dev/video0', direction is string "front"
    def __init__(self, dev, apiHandler, direction=True):
        self.dev = dev
        # front is True and rear is False
        self.direction = direction
        self.api = apiHandler
        self.streamProc = [-1, -1]

    def get_status(self):
        status = []
        for i in range(0,2):
            # if stream proc not set
            if self.streamProc[i] == -1:
                status.append(False)
            # is none if running
            elif (self.streamProc[i].poll() is None):
                status.append(True)
            else:
                status.append(False)
        return status

    # return list [localCmd, remotecmd]
    def get_StreamCommand(self):
        rcmd = "avconv -f video4linux2 -i " + self.dev + " -r 60 -f flv rtmp://" + config.getRtmpRelay()
        relative = self.get_relativeStream()
        rcmd = rcmd + '/' + relative
        if self.direction:
            port = "8090"
        else:
            port = "8091"
        mjpegPath = "/opt/mjpg-streamer/"
        lcmd = mjpegPath + "mjpg_streamer -i \""+mjpegPath+"input_uvc.so -d " + self.dev + "\" -o \""+mjpegPath+"output_http.so -p " + port + " -w "+mjpegPath+"www\""
        return [lcmd, rcmd]

    def get_relativeStream(self):
        # returns "app/uuuuid"
        if self.api:
            if self.direction:
                return self.api.streamRoute_post()['url'].split("/", 3)[3] + '-10'
            else:
                return self.api.streamRoute_post()['url'].split("/", 3)[3] + '-01'

    # used to enable stream TODO: make this stream local and remote
    def streamDevice(self, tries=0):
        cmds = self.get_StreamCommand()
        cmds = [shlex.split(cmd) for cmd in cmds]
        for num in range(0,2):
            # if poll is none that means it is running, so don't try to open a new one.
            if not self.get_status()[num]:
                self.streamProc[num] = subprocess.Popen(cmds[num])
                time.sleep(4)
                self.validateStream(tries, num)
                if self.api:
                    if self.direction and num:
                        self.api.streamEnables_post({'frontEnable':self.get_status()[num]})
                    elif num:
                        self.api.streamEnables_post({'rearEnable':self.get_status()[num]})

        return -1

    def killStream(self):
        for i in range(0,2):
            try:
                self.streamProc[i].kill()
            except:
                pass
            if self.api:
                if self.direction:
                    self.api.streamEnables_post({'frontEnable':self.get_status()[i]})
                else:
                    self.api.streamEnables_post({'rearEnable':self.get_status()[i]})

        return self.get_status()[0]

    # checks if stream is enabled, if not then start it.
    def validateStream(self, tries,num, i=0):
        tries += 1
        if tries > 4:
            return self.get_status()
        # if it was found not running
        if not self.get_status()[num]:
            print("Failed to stream: Retrying count " + tries)
            self.streamDevice(tries)
        return self.get_status()[num]

    #todo: have it update the api, used by interupt.
    def enableCamera(self):
        self.streamDevice()


# class utilized to manage networking
# add, remove, connect, list networks
class NetworkHandler():

    def __init__(self):
        pass

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(filename)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='evil.log',
                        filemode='w')

    def runProc(self, rcmd):
        """
        Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
        Returns output if successful, or None and logs error if not.
        """

        cmd = shlex.split(rcmd)
        executable = cmd[0]
        executable_options=cmd[1:]

        try:
            proc  = subprocess.run(([executable] + executable_options), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            response_stdout, response_stderr = proc.stdout, proc.stderr
        except OSError as e:
            logging.debug("OsError")
        except ValueError as e:
            logging.debug( "Value error occured. Check your parameters." )
        else:
            print(response_stdout)
            return response_stdout

    # add network and connect to it
    def add_network(self, _iface, _ssid, _type, _pass=None):
        netNum = self.runProc("wpa_cli -i %s add_network" % _iface).decode().strip()
        self.runProc('wpa_cli -i %s set_network %s ssid \'"%s"\'' % (_iface, netNum, _ssid))
        if _type == "OPEN":
            self.runProc("wpa_cli -i %s set_network %s auth_alg OPEN" % (_iface, netNum) )
            self.runProc("wpa_cli -i %s set_network %s key_mgmt NONE" % (_iface, netNum) )
        elif _type == "WPA" or _type == "WPA2":
            self.runProc('wpa_cli -i %s set_network %s psk \'"%s"\'' % (_iface, netNum, _pass))
        elif _type == "WEP":
            self.runProc('wpa_cli -i %s set_network %s wep_key \'"%s"\'' % (_iface, netNum, _pass))

        self.runProc("wpa_cli -i %s select_network %s" % (_iface, netNum))

    # connect to a network based on netNum
    def connect_network(self, _iface, _netNum):
        self.runProc("wpa_cli -i %s select_network %s" % (_iface, _netNum))

    # disconnect from network
    def disconnect_network(self, _iface, _netNum):
        self.runProc("wpa_cli -i %s disconnect %s" % (_iface, _netNum))

    # remove a network based on the network Num
    def remove_network(self, _iface, _netNum):
        self.runProc("wpa_cli -i %s remove_network %s" % (_iface, _netNum))

    # list networks available to wpa_cli
    def list_networks(self, _iface):
        return self.runProc("wpa_cli -i %s list_networks" % _iface).decode().split('\n')[1:]

    # run softAP
    def createAP(self):
        pass

    # modify softAP settings
    def modifyAP(self):
        pass


class SensorHandler():
    # for RPI version 1, use “bus = smbus.SMBus(0)”
    bus = smbus.SMBus(1)
    # This is the address we setup in the Arduino Program
    address = 0x04

    @staticmethod
    def get_data():
        try:
            return SensorHandler.bus.read_i2c_block_data(SensorHandler.address, 0);
        except:
            pass

    @staticmethod
    def get_float(data, index):
        bytes = data[4*index:(index+1)*4]
        return struct.unpack('f', "".join(map(chr, bytes)).encode())[0]

    @staticmethod
    # retireve statistic and send to server
    def retStatistic():
        try:
            data = SensorHandler.get_data()
            buf = SensorHandler.get_float(data, 5)
            latitude = SensorHandler.get_float(data, 0)/100
            if int(buf) == 78:
                lat = 'N'
            else:
               lat = 'S'
               latitude = latitude*-1
            lon = SensorHandler.get_float(data, 6)
            longitude = SensorHandler.get_float(data,1)/100
            if int(lon) == 87:
               lon = 'W'
               longitude = longitude*-1
            else:
               lon = 'E'
            return [longitude, latitude]
        except:
            return None
