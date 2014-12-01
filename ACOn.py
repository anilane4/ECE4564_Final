import RPi.GPIO as GPIO
import sys, pika, json, socket, thread

def clientThread(currClient, addr):
    while True:
        recvCommand = currClient.recv(1024)
        dict = json.loads(recvCommand)
	zoneFace = dict['Zone']
	acFace = dict['AC']
        if(int(zoneFace) == 1):
            GPIO.output(11,int(acFace))
            print "Zone 1"
        else:
            GPIO.output(12,int(acFace))
            print "Zone 2"
    
             
def main(argv):

##    def callback(ch, method, properties, body):
##        print "%r"%(body)
##	dict = json.loads(body)
##	zoneFace = dict['Zone']
##	acFace = dict['AC']
##        if(int(zoneFace) == 1):
##            GPIO.output(11,int(acFace))
##            print "Zone 1"
##        else:
##            GPIO.output(12,int(acFace))
##            print "Zone 2"
					        
    ## Use Board GPIO pin numbering
    GPIO.setmode(GPIO.BOARD)

    ## Set GPIO pins 11 and 12 as outputs
    ## 11 is ac on signal
    ## 12 is ac off signal
    GPIO.setup(11,GPIO.OUT)
    GPIO.setup(12,GPIO.OUT)

    port = 2003
    s = None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('',port))
        s.listen(1)
        print "Ready for commands."
    except socket.error, (value, message):
        if s:
            s.close()
            print "Not ready for commands."
            sys.exit(1)

    try:
        while True:
            currClient, addr = s.accept()
            thread.start_new_thread(clientThread, (currClient,addr))
            print "Receiving commands."
    except KeyboardInterrupt:
        print "Not ready for commands."
        s.close()
        sys.exit()
    
##    try:
##        msg_broker = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.22',virtual_host='environment_host',credentials=pika.PlainCredentials('leonp92','raspberry', True)))
##    except:
##        print "Couldn't connect to broker"
##        sys.exit(1)

##    print "Connected to broker"

##    channel = msg_broker.channel()
##    channel.exchange_declare(exchange='environment_broker', type='direct')
##    
##    ch = msg_broker.channel()
##    my_queue = ch.queue_declare(exclusive=True)
##
##    ch.queue_bind(exchange='environment_broker', queue=my_queue.method.queue, routing_key='control_hub')
##
##    try:
##        channel.basic_consume(callback, queue=my_queue.method.queue, no_ack=True)
##	channel.start_consuming()
##    except (KeyboardInterrupt, SystemExit):
##	msg_broker.close()
##	print "\nClosing message broker connection...\nTerminating PiStatsView!\n"


##    while(1):
##        isACOn = input('Command: ')
##        if(isACOn):
##            GPIO.output(11,True)
##            GPIO.output(12,False)
##        else:
##            GPIO.output(11,False)
##            GPIO.output(12,True)

if __name__ == "__main__":
    main(sys.argv[1:])



