#! /usr/bin/python
import thread, sys, socket, json

def main(argv):
	# Variable declarations
	zoneTemp = [75, 75]
	zTrigger = [75, 75]
	zACStatus = [0, 0]
	zManual = [0, 0]
	clients = []

	if len(argv) > 0:
		host = argv[0]
	else:
		print "ERROR: No control host found. Exiting\n"
		sys.exit(1)

	# Initiate message broker
	try:
		try:
			# Set up server information
			server2ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server2ClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			server2ClientSocket.bind(('', 2000))
			server2ClientSocket.listen(5)
			print "Client Socket is open on port 2000!"

			server2ZonesSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server2ZonesSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			server2ZonesSocket.bind(('', 2001))
			server2ZonesSocket.listen(5)
			print "Zone Socket is open on port 2001!"

		except socket.error, (value, message):
			if server2ClientSocket:	
				server2ClientSocket.close()
			if server2ZonesSocket:	
				server2ZonesSocket.close()
			print "Could not open server socket: " + message
			sys.exit(1)

		# Try to set up connetion to control hub
		try:
			controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			controlSocket.connect((str(host), int(2003)))
		except socket.error, (value, message):
			if controlSocket:	
				controlSocket.close()
			if server2ClientSocket:	
				server2ClientSocket.close()
			if server2ZonesSocket:	
				server2ZonesSocket.close()
			print "Could not connect to control hub socket: " + message
			sys.exit(1)

		def sendData(clients):
			dataDict = {'Zone 1':{'temp':str(zoneTemp[0]), 'isOn': str(zACStatus[0])}, 'Zone 2':{'temp':str(zoneTemp[1]), 'isOn':str(zACStatus[1])}}
			for client in clients:
				client.send(json.dumps(dataDict))
			print "Sending messages to exchange environment_broker and routing key server_to_client"

		def toggleAC(zone, status):
			dataDict = {'Zone':str(zone), 'AC':str(status)}
			controlSocket.send(json.dumps(dataDict))
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

		def clientCallback(client, address):
			data = client.recv(1024)

			jsonTemp = json.loads(data)
			zone = None
			trigger = None
			manual = None
			acOn = None
			i = 0
			
			zone = int(jsonTemp['id'])
			trigger = int(jsonTemp['trigger'])
			manual = int(jsonTemp['manual'])
			acOn = int(jsonTemp['acOn'])

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

		def zoneCallback(client, address):
			data = client.recv(1024)

			jsonTemp = json.loads(data)
			temp = int(jsonTemp['Temp'])
			zone = int(jsonTemp['Zone']) - 1
			
			zoneTemp[zone - 1] = int(temp)	
			zoneCallback(zone, temp)
			sendData()	

		def clientThreads(sock):
			try:
				while True:
					connection, address = sock.accept()
					clients.append(connection)
					thread.start_new_thread(clientCallback, (connection, address,))
					print 'A client connected!'
			except KeyboardInterrupt:
				print "Server is closing."
				sock.close()

		def zoneThreads(sock):
			try:
				while True:
					connection, address = sock.accept()
					thread.start_new_thread(zoneCallback, (connection, address,))
					print 'A client connected!'
			except KeyboardInterrupt:
				print "Server is closing."
				sock.close()

		thread.start_new_thread(clientThreads, (server2ClientSocket,))
		thread.start_new_thread(zoneThreads, (server2ZonesSocket, ))
		print "Environment Server is up and running!"

	except (KeyboardInterrupt, SystemExit):
		if server2ClientSocket:	
			server2ClientSocket.close()
		if server2ZonesSocket:	
			server2ZonesSocket.close()
		print "\nClosing message broker connection...\nTerminating Environment Server! "


if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	except (KeyboardInterrupt, SystemExit):
		print "Error setting up message broker. Exiting Environment Server!"

	
