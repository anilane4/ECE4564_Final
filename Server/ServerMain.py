#! /usr/bin/python
import TemperatureMonitor, thread, pika, json

# Expects a json object like {Zone: '1', Temp: 'X'}
def zoneListener(ch, queue, tempMon, controlSocket):

	def recordData(ch, method, properties, body):
		jsonDict = json.load(body)
		zoneIndex = int(jsonDict['Zone']) - 1
		zoneTemp = int(jsonDict['Temp'])

		tempMon.setZoneTemperatures(zoneIndex, zoneTemp)

		# If it's not manual control AND Temp > current
		if tempMon.getManual() == False:
			if tempMon.getTriggerTemperature(zoneIndex) >= zoneTemp:
				if tempMon.getACRunning(zoneIndex) == True:
					# Turn off.
					jsonObj = json.dumps({"Zone":str(zoneIndex+1), "AC":"0"})
					controlSocket.send(jsonObj)
					tempMon.setACRunning(zoneIndex, False)
					print "Turning off AC in zone: " + str(zoneIndex+1)

			else:
				if tempMon.getACRunning(zoneIndex) == False:
					# Turn on
					jsonObj = json.dumps({"Zone":str(zoneIndex+1), "AC":"1"})
					controlSocket.send(jsonObj)
					tempMon.setACRunning(zoneIndex, True)
					print "Turning on AC in zone: " + str(zoneIndex+1)

	try:
		channel.basic_consume(recordData, queue=queue.method.queue, no_ack=True)
		channel.start_consuming()
	except (KeyboardInterrupt, SystemExit):
		ch.close()

def clientSender(ch, tempMon):
	def timedFunction():
		zoneTemp = tempMon.getZoneTemperatures()
		tempDict = {}
		zoneIndex = 1

		for temp in zoneTemp:
			tempDict['Zone ' + str(zoneIndex)] =  {"temp":str(temp), "isOn": str(tempMon.getACRunning(zoneIndex-1))}
			zoneIndex += 1

		ch.basic_publish(exchange='environment_broker', routing_key='server_to_client',
			body=json.dumps(tempDict, default=lambda o:o.__dict__, indent=4))
		print "Sending messages to exchange environment_broker and routing key server_to_client"

	# Infinite loop until terminating
	try:
		while True: 
			time.sleep(60)
			timedFunction()
	except:
		# Just needs to return, zone listener should close the channel
		return

def clientListener(ch, queue, tempMon, controlSocket):
	def callback():
		jsonDict = json.load(body)

		# Expecting
		# Zone : {id:1, manual:0, acOn: 0, trigger:64 }
		for key in jsonDict:
			zoneInfo = jsonDict[key]
			zoneIndex = int(zoneInfo["id"])-1
			isManual = int(zoneInfo["manual"])
			isACOn = int(zoneInfo["acOn"])
			triggerTemp = int(zoneInfo["trigger"])
			zoneTemp = tempMon.getZoneTemperatures()

			if (isManual and isACOn) or (isManual == 0 and zoneTemp[zoneIndex] > triggerTemp) :
				jsonObj = json.dumps({"Zone":str(zoneIndex+1), "AC":"1"})
				controlSocket.send(jsonObj)
				tempMon.setACRunning(zoneIndex, True)
				print "Turning on AC in zone: " + str(zoneIndex+1)
			else:
				jsonObj = json.dumps({"Zone":str(zoneIndex+1), "AC":"0"})
				controlSocket.send(jsonObj)
				tempMon.setACRunning(zoneIndex, False)
				print "Turning off AC in zone: " + str(zoneIndex+1)
	try:
		channel.basic_consume(callback, queue=my_queue.method.queue, no_ack=True)
		channel.start_consuming()
	except:
		return

def main(argv):
	# Variable declarations
	tempMon = TemperatureMonitor.TemperatureMonitor()
	controlSocket = None

	# Initiate control hub socket
	try:
		# Set up server information
		controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		controlSocket.connect((str(host), 2000))
		print "Connected to control hub"
	except socket.error, (value, message):
		if controlSocket:	
			controlSocket.close()
			print "Could not connect to control hub: " + message
			sys.exit(1)

	# Initiate message broker
	try:
		msg_broker = pika.BlockingConnection(
			pika.ConnectionParameters(host='localhost',
									  virtual_host='environment_host',
									  credentials=pika.PlainCredentials(leonp92, raspberry), True)))
		# Set up channel
		msg_ch = msg_broker.channel()
		msg_ch.exchange_declare(exchange='environment_broker', type='direct')
		
		# Create a queue for consuming messages
		temp_queue = msg_ch.queue_declare(exclusive=True)
		msg_ch.queue_bind(exchange="environment_broker", queue=temp_queue.method.queue, routing_key='zone_info')
		
		# Queue for receiving client commands
		client_queue = msg_ch.queue_declare(exclusive=True)
		msg_ch.queue_bind(exchange="environment_broker", queue=client_queue.method.queue, routing_key='client_to_server')

		# Spawn off thread to handle receiving information from Zones
		thread.start_new_thread(zoneListener, (msg_ch, temp_queue, tempMon, controlSocket))

		# Spawns off thread to handle clients
		thread.start_new_thread(clientSender, (msg_ch, tempMon))
		thread.start_new_thread(clientListener, (msg_ch, client_queue, tempMon, controlSocket))
	except:
		msg_broker.close()
		print "\nClosing message broker connection...\nTerminating Environment Server! "

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	except:
		print "Shutting down environment server."

