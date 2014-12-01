#! /usr/bin/python
import thread, pika, json, sys, time

def main(argv):
	# Variable declarations
	zoneTemp = [75, 75]
	zTrigger = [75, 75]
	zACStatus = [0, 0]
	zManual = [0, 0]
	# Initiate message broker
	try:
		msg_broker = pika.BlockingConnection(
			pika.ConnectionParameters(host='localhost',
									  virtual_host='environment_host',
									  credentials=pika.PlainCredentials('leonp92', 'raspberry', True)))

		# Set up channel
		msg_ch = msg_broker.channel()
		msg_ch.exchange_declare(exchange='environment_broker', type='direct')

		# Create a queue for consuming messages
		temp_queue = msg_ch.queue_declare(exclusive=True)
		msg_ch.queue_bind(exchange="environment_broker", queue=temp_queue.method.queue, routing_key='zone_info')

		client_queue = msg_ch.queue_declare(exclusive=True)
		msg_ch.queue_bind(exchange="environment_broker", queue=client_queue.method.queue, routing_key='client_to_server')

		result = msg_ch.queue_declare(exclusive=True)
		queue_name = result.method.queue

		result2 = msg_ch.queue_declare(exclusive=True)
		queue_name2 = result.method.queue

		msg_ch.queue_bind(exchange='environment_broker', queue=queue_name, routing_key='zone_info')
		msg_ch.queue_bind(exchange='environment_broker', queue=queue_name2, routing_key='client_to_server')


		def sendData():
			tempDict = {'Zone 1':{'temp':str(zoneTemp[0]), 'isOn':str(zACStatus[0])}, 'Zone 2':{'temp':str(zoneTemp[1]), 'isOn':str(zACStatus[1])}}

			msg_ch.basic_publish(exchange='environment_broker', routing_key='server_to_client',
				body=json.dumps(tempDict, default=lambda o:o.__dict__, indent=4))
			print "Sending messages to exchange environment_broker and routing key server_to_client"

		def toggleAC(zone, status):
			msg_ch.basic_publish(exchange='environment_broker', routing_key='control_hub',
				body=json.dumps({"Zone":str(zone), "AC":str(status)}, default=lambda o:o.__dict__, indent=4))
			print "Sending messages to exchange environment_broker and routing key control_hub"


		def zoneCallback(zoneIndex, zoneTemp):
			# If it's not manual control AND Temp > current
			if zManual[zoneIndex] == 0 and zoneTemp != None:
				if zTrigger[zoneIndex] >= zoneTemp:
					if zACStatus[zoneIndex] == 1:
						# Turn off.
						zACStatus[zoneIndex] = 0
						toggleAC(zoneIndex+1, 0)
						print "Turning off AC in zone: " + str(zoneIndex+1)

				else:
					if zACStatus[zoneIndex] == 0:
						# Turn on
						zACStatus[zoneIndex] = 1
						toggleAC(zoneIndex+1, 1)
						print "Turning on AC in zone: " + str(zoneIndex+1)

		def callback(ch, method, properties, body):
			print " [X] %r:%r" % (method.routing_key, body,)

			if method.routing_key == 'zone_info':
				jsonTemp = body.replace(" ", "").strip('{')
				jsonTemp = jsonTemp.strip('}')
				jsonTemp = jsonTemp.split(',')
				json1 = jsonTemp[0].split(':')
				json2 = jsonTemp[1].split(':')

				if json1[0].replace("\"","") == 'Temp':
					temp = int(json1[1].replace("\"",""))
					zone = int(json2[1].replace("\"","")) - 1
				else:

					temp = int(json2[1].replace("\"",""))
					zone = int(json1[1].replace("\"","")) - 1
				zoneTemp[zone - 1] = int(temp)	
				zoneCallback(zone, temp)
				sendData()	
			else:
				jsonTemp = body.replace('{',"").replace('}',"").replace(" ","").replace('\"',"").replace("\n", "").replace(":", ",").split(',')
				print jsonTemp
				zone = None
				trigger = None
				manual = None
				acOn = None
				i = 0

				for entry in jsonTemp:
					if entry == 'id':
						zone = int(jsonTemp[i+1])
					elif entry == 'trigger':
						trigger = int(jsonTemp[i+1])
					elif entry == 'manual':
						manual = int(jsonTemp[i+1])
					elif entry == 'acOn':
						acOn = int(jsonTemp[i+1])
					i += 1

				zTrigger[zone-1] = trigger
				zManual[zone-1] = manual

				if manual == 0:
					if trigger >= zoneTemp[zone-1]:
						if zACStatus[zone-1] == 1:
							# Turn off.
							zACStatus[zone-1] = 0
							toggleAC(zone, 0)
							print "Turning off AC in zone: " + str(zone)

					else:
						if zACStatus[zone-1] == 0:
							# Turn on
							zACStatus[zone-1] = 1
							toggleAC(zone, 1)
							print "Turning on AC in zone: " + str(zone)
				else:
					if acOn ==  0 and zACStatus[zone-1] == 1:
						# Turn off
						zACStatus[zone-1] = 0
						toggleAC(zone, 0)
						print "Turning off AC in zone: " + str(zone)
					elif acOn == 1 and zACStatus[zone-1] == 0:
						# Turn on
						zACStatus[zone-1] = 1
						toggleAC(zone, 1)
						print "Turning on AC in zone: " + str(zone)


		print "Environment Server is up and running!"
		msg_ch.basic_consume(callback, queue=queue_name, no_ack=True)
		msg_ch.basic_consume(callback, queue=queue_name2, no_ack=True)
		msg_ch.start_consuming()

	except (KeyboardInterrupt, SystemExit):
		msg_broker.close()
		print "\nClosing message broker connection...\nTerminating Environment Server! "

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	except (KeyboardInterrupt, SystemExit):
		print "Error setting up message broker. Exiting Environment Server!"

	
