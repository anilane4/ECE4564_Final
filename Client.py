import sys, Tkinter, pika, ClientGUI, thread

def serverListener(guiObj):
	jsonDict = json.load(body)
	i = 0

	for key, value in jsonDict:
		guiObj.setZoneTemp(i, int(value["temp"]), bool(value["isOn"])) 

def main(argv):
	root = Tkinter.Tk()
	root.geometry("500x500")

	host = argv[0]

	try:
		msg_broker = pika.BlockingConnection(
				pika.ConnectionParameters(host=host,
										  virtual_host='environment_host',
										  credentials=pika.PlainCredentials(leonp92, raspberry), True)))
		# Set up channel
		msg_ch = msg_broker.channel()
		msg_ch.exchange_declare(exchange='environment_broker', type='direct')
		
		# Create a queue for consuming messages
		temp_queue = msg_ch.queue_declare(exclusive=True)
		msg_ch.queue_bind(exchange="environment_broker", queue=temp_queue.method.queue, routing_key='zone_info')
	
		appGUI = ClientGUI.ClientGUI(root, msg_ch)
		thread.start_new_thread(serverListener, appGUI)

		root.mainloop()
	except:
		msg_broker.close()
		print "\nClosing message broker connection...\nTerminating Environment Client! "

if __name__=='__main__':
	main(sys.argv[1:])

