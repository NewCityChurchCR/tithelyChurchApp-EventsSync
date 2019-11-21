#/usr/bin/env python
import os, csv

KEY_FIELDNAME='uid'
REQUIRED_FIELDNAMES=['name', 'description', 'location', 'uid', 'categories']

class db():
	def __init__(self, dbPath):
		self.dbPath=os.path.abspath(dbPath)
		self.data={}
		self.fieldnames=REQUIRED_FIELDNAMES

		if os.path.isfile(self.dbPath):
			dbFile=open(self.dbPath, 'r')
			csvHandle=csv.DictReader(dbFile)
			self.fieldnames=csvHandle.fieldnames
			missingFieldNames=[x for x in REQUIRED_FIELDNAMES if x not in csvHandle.fieldnames]
			if len(missingFieldNames) > 0:
				print('Missing fieldnames: '+', '.join(missingFieldNames))
			for eachRow in csvHandle:
				self.addUpdate(eachRow)
			dbFile.close()

	def __iter__(self):
		return iter(self.data.values())

	def addUpdate(self, instance):
		if isinstance(instance, dict):
			missingFieldNames=[x for x in self.fieldnames if x not in instance.keys()]
			for missingField in missingFieldNames:
				instance[missingField]=None

			if instance[KEY_FIELDNAME] is not None and instance[KEY_FIELDNAME] != '':
				if instance[KEY_FIELDNAME] not in self.data.keys():
					self.data[instance[KEY_FIELDNAME]]=instance
				else:
					for eachKey in instance.keys():
						if instance[eachKey] is not None and instance[eachKey] != '':
							self.data[instance[KEY_FIELDNAME]][eachKey] = instance[eachKey]
		elif isinstance(instance, str):
			tempDict={}
			for missingField in self.fieldnames:
				tempDict[missingField]=None
			tempDict[KEY_FIELDNAME]=instance
			if instance not in self.data.keys():
				self.data[instance]=tempDict
		else:
			raise Exception('Only supports dict or '+KEY_FIELDNAME+' string (provided '+str(type(instance))+')!')

	def remove(self, key):
		if self.data.get(key) is not None:
			del self.data[key]

	def save(self):
		print('Saving '+self.dbPath)
		dbFile=open(self.dbPath, 'w', newline='')
		csvHandle = csv.DictWriter(dbFile, fieldnames=self.fieldnames)
		csvHandle.writeheader()
		for dataKey in self.data.keys():
			csvHandle.writerow(self.data[dataKey])
		dbFile.close()
