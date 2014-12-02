"""
ECE 4564
Temperture pi
will relay a json file to the server
json format is
Zone: 'xonenumber'
Temp: 'tempuerature in F'

"""

__author__ = 'Martin Anilane'

import sys
import getopt
import signal
import json
import time
import socket

# Global variable that controls running the app
publish_Temp = True


def stop_temp_service(signal, frame):
    global publish_Temp # Ensures that a local version of this variable is not made
    publish_Temp = False # Shuts down event loop
    print "\ngood bye "
    return


#this function is going to read teh value from the temp sensor and return that value
# for now i dont have the hard ware so i am going to fake it
def getTemperatureData( numInArray):
    mylist = ["75", "74", "79", "70", "70", "70", "71", "72", "75", "68"]
    print "this temp = " + mylist[numInArray]
    #sleep for one sec
    time.sleep(5)
    return mylist[numInArray]


# main of the project
def main(argv):
    try:
        zoneNumber = 0
        host = ""
        signal_num = signal.SIGINT
        try:
            signal.signal(signal_num, stop_temp_service)
            signal_num = signal.SIGTERM
            signal.signal(signal_num, stop_temp_service)
        except ValueError, ve:
            print "Warning: Greceful shutdown may not be possible: Unsupported Signal: " + signal_num

        # get the opts
        try:
            opts, args = getopt.getopt(argv, "z:h:")
        #error handle for the incorrect values
        except getopt.GetoptError:
            print "temp -z zone number"
            sys.exit(2)
        zopt = False
        # for each operation interate through and place it with the correct value
        for opt, arg in opts:
            if opt == '-z':
                convert = int(arg)
                if isinstance(convert, int):
                    zoneNumber = convert
                    zopt = True
                else:
                    print "Zone number must be a int"
                    sys.exit(2)
            elif opt == '-h':
                host = arg

        # check the boolean for the set option
        if zopt == False:
            print "must put in zone number"
            sys.exit(2)

        mainSocket = None
        print "im here"
        try:
            try:
                mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                mainSocket.connect((str(host), int(2001)))
            except socket.error, (value, message):
                print "closing socket: " + message
                if mainSocket:  
                    mainSocket.close()
                sys.exit()
                
            print "Connected to host"
            #my dictionary for my information to be sent out
            zone_data = {"Zone": zoneNumber, "Temp": "0"}
            myCount = 0
            print "Sending Temperature data"
            while(publish_Temp):
                zone_data["Temp"] = getTemperatureData(myCount)
                myCount += 1
                if myCount == 10:
                    myCount = 0
                json_message = json.dumps(zone_data)
                # Send the message
                mainSocket.send(json_message)
        except Exception, eee:
            print "Error: An unexpected exception occured: " + eee.message

        finally:
            if mainSocket is not None:
                print "closing socket"
                mainSocket.close()
    except Exception, ee:
        # unkown error shouting down
        print ee
        print "Shuting down"
        sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
