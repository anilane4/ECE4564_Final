"""
ECE 4564
Temperture pi
will relay a json file to the server
json format is
Zone: 'xonenumber'
Temp: 'tempuerature in F'

"""

__author__ = 'Martin Anilane'

import pika
import pika.exceptions
import sys
import getopt
import signal
import json

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
    mylist = [65.3, 68.5, 69.4, 70.3, 70.3, 70.3, 71.2, 72.3, 75.6, 68.2]
    return mylist[numInArray]


# main of the project
def main(argv):
    try:
        zoneNumber = 0
        broker = None
        v_host = '/'
        login = "guest"
        password = "guest"
        routkey = None
        # Setup signal handlers to shutdown this app when SIGINT or SIGTERM is
        # sent to this app
        # For more info about signals, see: https://scholar.vt.edu/portal/site/0a8757e9-4944-4e33-9007-40096ecada02/page/e9189bdb-af39-4cb4-af04-6d263949f5e2?toolstate-701b9d26-5d9a-4273-9019-dbb635311309=%2FdiscussionForum%2Fmessage%2FdfViewMessageDirect%3FforumId%3D94930%26topicId%3D3507269%26messageId%3D2009512
        signal_num = signal.SIGINT
        try:
            signal.signal(signal_num, stop_temp_service)
            signal_num = signal.SIGTERM
            signal.signal(signal_num, stop_temp_service)
        except ValueError, ve:
            print "Warning: Greceful shutdown may not be possible: Unsupported Signal: " + signal_num

        # get the opts
        try:
            opts, args = getopt.getopt(argv, "z:")
        #error handle for the incorrect values
        except getopt.GetoptError:
            print "temp -z zone number"
            sys.exit(2)
        zopt = False
        # for each operation interate through and place it with the correct value
        for opt, arg in opts:
            if opt == '-z':
                if isinstance(arg, int):
                    zoneNumber = arg
                    zopt = True
                else:
                    print "Zone number must be a int"
                    sys.exit(2)

        # check the boolean for the set option
        if zopt == False:
            print "must put in zone number"
            sys.exit(2)

        msg_broker = None
        ch = None
        try:
            # connect to the message broker

            msg_broker = pika.BlockingConnection(
                pika.ConnectionParameters(host=broker,
                                          virtual_host=v_host,
                                          credentials=pika.PlainCredentials(login,
                                                                            password,
                                                                            True))
            )

            print "Connected to message broker"

            # setup the exchange
            ch = msg_broker.channel()
            # try:
            ch.exchange_declare(exchange="environment_broker",
                                type="direct")
            #my dictionary for my information to be sent out
            zone_data = {"Zone": zoneNumber, "Temp": 0.0}
            myCount = 0
            print "Sending Temperature data"
            while(publish_Temp):
                zone_data["Temp"] = getTemperatureData(myCount)
                myCount += 1
                if myCount == 10:
                    myCount = 0
                      # creates a JSON representation of the networking and CPU information
                json_message = json.dumps(zone_data)
                # Send the message
                ch.basic_publish(exchange="environment_broker",
                            routing_key="zone_info",
                            body=json_message)

        except pika.exceptions.AMQPError, ae:
            print "Error: An AMQP Error occured: " + ae.message

        except pika.exceptions.ChannelError, ce:
            print "Error: A channel error occured: " + ce.message

        except Exception, eee:
            print "Error: An unexpected exception occured: " + eee.message

        finally:
            if ch is not None:
                ch.close()
            if msg_broker is not None:
                msg_broker.close()
    except Exception, ee:
        # unkown error shouting down
        print ee
        print "Shuting down"
        sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])