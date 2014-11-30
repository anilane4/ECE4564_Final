class TemperatureMonitor:
	def __init__(self):
		triggerTemperature = [75, 75]
		zoneTemperatures = []
		isManual = False
		manualTrigger = 0
		isACRunning = [False, False]

	def setTriggerTemperature(self, zone, temp):
		self.triggerTemperature[zone] = temp
	def getTriggerTemperature(self, zone):
		return self.triggerTemperature[zone]

	def setZoneTemperatures(self, index, temp):
		self.zoneTemperatures[index] = temp
	def getZoneTemperatures(self):
		return self.zoneTemperatures

	def setManual(self, manualBool):
		self.isManual = manualBool
	def getManual(self):
		return self.isManual

	def setManualTrigger(self, triggerBool):
		self.manualTrigger = triggerBool
	def getManualTrigger(self):
		return self.manualTrigger

	def setACRunning(self, zone, acBool):
		self.isACRunning[zone] = acBool
	def getACRunning(self, zone):
		return self.isACRunning[zone]
