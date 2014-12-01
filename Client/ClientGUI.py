import Tkinter, tkMessageBox, json, socket

class ClientGUI(Tkinter.Frame):
	def __init__(self, parent, sock):
		Tkinter.Frame.__init__(self, parent, background="white")
		self.parent = parent
		self.socket = sock
		self.zoneTemp = [None, None]

		self.parent.title("Environment Control Client")

		zone1_frame = Tkinter.LabelFrame(self.parent, text="Zone 1", font=("Helvetica", 16, "bold"))
		zone1_frame.pack(fill="both", expand="yes")
		zone2_frame = Tkinter.LabelFrame(self.parent, text="Zone 2", font=("Helvetica", 16, "bold"))
		zone2_frame.pack(fill="both", expand="yes")

		self.zone1Temp = Tkinter.Label(zone1_frame, text="N/A", font=("Helvetica", 80), fg="red")
		self.zone2Temp = Tkinter.Label(zone2_frame, text="N/A", font=("Helvetica", 80), fg="red")
		self.zone1Temp.pack()
		self.zone2Temp.pack()

		def manualZ1Callback():
			if str(self.z1_isManual.get()) == '1':
				self.textInput1.pack_forget()
				self.sButton1.pack_forget()
				self.acOnCheck1.pack()
				self.sButton1.pack()
			else:
				self.sButton1.pack_forget()
				self.acOnCheck1.pack_forget()
				self.textInput1.pack()
				self.sButton1.pack()

		def manualZ2Callback():
			if str(self.z2_isManual.get()) == '1':
				self.textInput2.pack_forget()
				self.sButton2.pack_forget()
				self.acOnCheck2.pack()
				self.sButton2.pack()
			else:
				self.sButton2.pack_forget()
				self.acOnCheck2.pack_forget()
				self.textInput2.pack()
				self.sButton2.pack()

		self.z1_isManual = Tkinter.IntVar()
		Tkinter.Checkbutton(zone1_frame, text="Manual Control", variable=self.z1_isManual, command=manualZ1Callback).pack()
		self.z2_isManual = Tkinter.IntVar()
		Tkinter.Checkbutton(zone2_frame, text="Manual Control", variable=self.z2_isManual, command=manualZ2Callback).pack()
	
		def submitZone1Callback():
			triggerTemp = self.textInput1.get()

			if triggerTemp.isdigit():
				self.socket.send(json.dumps({"id":"1", "manual":str(self.z1_isManual.get()), "acOn":str(self.acOn1.get()),"trigger":str(triggerTemp)}, default=lambda o:o.__dict__, indent=4))
				print "Submiting Zone 1 Data to the Server!"
			else:
				tkMessageBox.showerror("Error!", "ERROR: Trigger temperature value must be a number!")
		def submitZone2Callback():
			triggerTemp = self.textInput2.get()

			if triggerTemp.isdigit():
				self.socket.send(json.dumps({"id":"2", "manual":str(self.z2_isManual.get()), "acOn":str(self.acOn2.get()),"trigger":str(triggerTemp)}, default=lambda o:o.__dict__, indent=4))
				print "Submiting Zone 2 Data to the Server!"
			else:
				tkMessageBox.showerror("Error!", "ERROR: Trigger temperature value must be a number!")

		self.textInput1 = Tkinter.Entry(zone1_frame, width=10, justify="center", bd=5)
		self.textInput1.insert(0, "75") # Default value
		self.textInput1.pack()
		self.sButton1 = Tkinter.Button(zone1_frame, text="Submit", command=submitZone1Callback)
		self.sButton1.pack()

		self.textInput2 = Tkinter.Entry(zone2_frame, width=10, justify="center", bd=5)
		self.textInput2.insert(0, "75")
		self.textInput2.pack()
		self.sButton2 = Tkinter.Button(zone2_frame, text="Submit", command=submitZone2Callback)
		self.sButton2.pack()

		self.acOn1 = Tkinter.IntVar()
		self.acOn2 = Tkinter.IntVar()
		self.acOnCheck1 = Tkinter.Checkbutton(zone1_frame, text="AC On", variable=self.acOn1)
		self.acOnCheck2 = Tkinter.Checkbutton(zone2_frame, text="AC On", variable=self.acOn2)

	def setZoneTemp(self, zoneIndex, temp, status):
		self.zoneTemp[zoneIndex] = temp

		if zoneIndex == 0:
			self.zone1Temp.config(text = str(temp) + u'\xb0' + 'F')

			if int(status) == 1:
				self.zone1Temp.config(fg="green")
			else:
				self.zone1Temp.config(fg="red")
		else:
			self.zone2Temp.config(text = str(temp) + u'\xb0' + 'F')
			if int(status) == 1:
				self.zone2Temp.config(fg="green")
			else:
				self.zone2Temp.config(fg="red")

