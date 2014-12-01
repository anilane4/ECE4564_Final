import sys, Tkinter, pika, ClientGUI, thread, json

def serverListener(ch, temp_queue, guiObj):
	print 'TESTING TESTING'
	def callback(ch, method, properties, body):
		jsonDict = json.load(body)
		i = 0
		print " [X] %r:%r" % (method.routing_key, body,)
		for key, value in jsonDict:
			guiObj.setZoneTemp(i, int(value["temp"]), bool(value["isOn"])) 

	ch.basic_consume(callback, queue=temp_queue.method.queue, no_ack=True)
	#ch.start_consuming()

def main(argv):
	root = Tkinter.Tk()
	root.geometry("500x500")

	host = argv[0]

	msg_broker = pika.BlockingConnection(
		pika.ConnectionParameters(host=host,
								  virtual_host='environment_host',
								  credentials=pika.PlainCredentials("leonp92", "raspberry", True)))
	# Set up channel
	msg_ch = msg_broker.channel()
	msg_ch.exchange_declare(exchange='environment_broker', type='direct')

	# Create a queue for consuming messages
	temp_queue = msg_ch.queue_declare(exclusive=True)
	msg_ch.queue_bind(exchange="environment_broker", queue=temp_queue.method.queue, routing_key='server_to_client')

	appGUI = ClientGUI.ClientGUI(root, msg_ch)
	thread.start_new_thread(serverListener, (msg_ch, temp_queue, appGUI))

	root.mainloop()

if __name__=='__main__':
	main(sys.argv[1:])

