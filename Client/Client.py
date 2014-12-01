import sys, Tkinter, pika, ClientGUI_Sockets, threading, json, socket, os

def main(argv):
	root = Tkinter.Tk()
	root.geometry("500x500")

	host = argv[0]

	def serverListener(ch, guiObj):
		try:
			while True:
				body = ch.recv(1024)

				if not body:
					print "Server Environment Socket closed!"
					os._exit(1)
				else:
					jsonDict = json.loads(body)
					i = 0
					print " [X] %r" % (jsonDict,)
					for key in jsonDict:
						value = jsonDict[key]
						guiObj.setZoneTemp(i, int(value["temp"]), int(value["isOn"])) 
						i += 1
		except KeyboardInterrupt:
			print "Terminating connection with Environment Server!"
			ch.close()
			root.destroy()
			root.quit()
			os._exit(1)

	try:
		mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mainSocket.connect((str(host), int(2000)))

		try:
			appGUI = ClientGUI_Sockets.ClientGUI(root, mainSocket)
			socketThread = threading.Thread(target=serverListener, args=(mainSocket, appGUI,))
			socketThread.start()
		except:
			mainSocket.close()

		def closeOut():
			print "Exiting Environment Client!"
			if mainSocket:
				mainSocket.close()
			os._exit(1)
		root.protocol("WM_DELETE_WINDOW", closeOut)
		root.mainloop()
	except:
		root.destroy()
		root.quit()
		if mainSocket:	
			mainSocket.close()
		print "ERROR: Failed to connect to Environment Server!"
		os._exit(1)

if __name__=='__main__':
	try:
		main(sys.argv[1:])
	except:
		print "Exiting Environment Client"
		os._exit(1)

