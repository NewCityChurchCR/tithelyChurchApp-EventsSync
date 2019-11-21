#/usr/bin/env python
import os, inspect
currentScriptDirectory=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import eventsDbManager as dbm

eventsDb=dbm.db(os.path.join(currentScriptDirectory, 'nccEventsDb.csv'))
#eventsDb.save()

#os.environ['HTTP_PROXY']='http://proxy.rockwellcollins.com:9090'
#os.environ['HTTPS_PROXY']=os.environ['HTTP_PROXY']
#os.environ['FTP_PROXY']=os.environ['HTTP_PROXY']
ICAL_URL='https://outlook.office365.com/owa/calendar/a29261f7c5454557aa03c7fba115a31d@newcitycr.org/e116874f35034674ba87384239ab05df10800306611703141858/calendar.ics'
LOCAL_FILE_NAME='calendar.ics'

import requests
import dateutil.parser
r = requests.head(ICAL_URL)
url_time = dateutil.parser.parse(r.headers['Date']).astimezone()

import time
with open(LOCAL_FILE_NAME, 'w') as localIcsHandle:
	tempIcsText = requests.get(ICAL_URL).text
	localIcsHandle.write(tempIcsText)
modTime = time.mktime(url_time.timetuple())
os.utime(LOCAL_FILE_NAME, (modTime, modTime))

#print('tempIcsText="'+tempIcsText+'"')

import pprint

#import icalendar
#cal = icalendar.Calendar.from_ical(tempIcsText)

import arrow
import ics
cal = ics.Calendar(tempIcsText)

INDENT_LEVEL=0
def lineprefix(incr=0):
	global INDENT_LEVEL
	INDENT_LEVEL+=incr
	if INDENT_LEVEL < 0:
		INDENT_LEVEL= 0
	return ''.join(['\t']*INDENT_LEVEL)

def printWithPrefix(*args, incr=0, **kargs):
	print(lineprefix(incr=incr), end='')
	print(*args, **kargs)

import ics.grammar.parse

def printContentLine(contLine, incr=0):
	printWithPrefix('ContentLine:', incr=incr)
	printWithPrefix('name:'+str(contLine.name), incr=1)
	printWithPrefix('value:'+str(contLine.value))
	printWithPrefix('params:'+str(contLine.params))
	lineprefix(-1)

def printContainer(cont, incr=0):
	printWithPrefix('Container:', incr=incr)
	tempIncr=1
	for tempObj in cont:
		if type(tempObj) == ics.grammar.parse.ContentLine:
			printContentLine(tempObj, incr=tempIncr)
		elif type(tempObj) == ics.grammar.parse.Container:
			printContainer(tempObj, incr=tempIncr)
		if tempIncr > 0:
			tempIncr=0
	if tempIncr == 0:
		lineprefix(-1)

def printExtra(var, incr=0):
	printWithPrefix('extra:', incr=incr)
	printContainer(var.extra, incr=1)
	lineprefix(-1)

def printDuration(var, incr=0):
	printWithPrefix('duration:' + str(var.duration), incr=incr)
	printWithPrefix('min:' + str(var.duration.min), incr=1)
	printWithPrefix('max:' + str(var.duration.max))
	printWithPrefix('resolution:' + str(var.duration.resolution))
	printWithPrefix('days:' + str(var.duration.days))
	printWithPrefix('seconds:' + str(var.duration.seconds))
	printWithPrefix('microseconds:' + str(var.duration.microseconds))
	printWithPrefix('total_seconds():' + str(var.duration.total_seconds()))
	lineprefix(-1)

def printGeo(var, incr=0):
	printWithPrefix('geo:' + str(var.geo), incr=incr)
	if var.geo is not None:
		printWithPrefix('latitude:' + str(var.geo.latitude), incr=1)
		printWithPrefix('longitude:' + str(var.geo.longitude))
		lineprefix(-1)

def printEvent(var, incr=0):
	var=eachEvent
	varName='eachEvent'
	printWithPrefix(varName+':', incr=incr)
	printWithPrefix('alarms:'+str(var.alarms), incr=1)
	printWithPrefix('attendees:'+str(var.attendees))
	printWithPrefix('categories:'+str(var.categories))
	printWithPrefix('created:'+str(var.created))
	printWithPrefix('description:'+str(var.description))
	printWithPrefix('last_modified:'+str(var.last_modified))
	printWithPrefix('location:'+str(var.location))
	printWithPrefix('name:'+str(var.name))
	printWithPrefix('organizer:'+str(var.organizer))
	printWithPrefix('transparent:'+str(var.transparent))
	printWithPrefix('uid:'+str(var.uid))
	printWithPrefix('url:'+str(var.url))
	printWithPrefix('all_day:'+str(var.all_day))
	printWithPrefix('begin:'+str(var.begin))
	printWithPrefix('classification:'+str(var.classification))
	printDuration(var)
	printWithPrefix('end:'+str(var.end))
	printGeo(var)
	printWithPrefix('status:'+str(var.status))
	printWithPrefix('has_end():'+str(var.has_end()))
	printExtra(var)
	lineprefix(incr=-1)

def printTimeline(var, incr=0):
	varName='eachTimeline'
	printWithPrefix(varName+':', incr=incr)
	printWithPrefix('now():'+str(var.now()), incr=1)
	lineprefix(incr=-1)

def returnContainer(cont):
	retCont={}
	tempOther=[]
	for tempObj in cont:
		if type(tempObj) == ics.grammar.parse.ContentLine:
			retCont[tempObj.name]={'value': tempObj.value, 'params':tempObj.params}
			#printContentLine(tempObj, incr=tempIncr)
		elif type(tempObj) == ics.grammar.parse.Container:
			tempOther+=[returnContainer(cont)]
	if len(tempOther) > 0:
		retCont['other']=tempOther
	return retCont

import copy

events=[]
for eachEvent in cal.timeline.start_after(arrow.utcnow().shift(days=-1)):
	printEvent(eachEvent)
	extrasDict=returnContainer(eachEvent.extra)
	tempKeys=[]
	tempKeys+=extrasDict.keys()
	for eachExtra in tempKeys:
		#print('eachExtra='+eachExtra)
		if eachExtra.startswith('X-MICROSOFT-'):
			del extrasDict[eachExtra]
	eventDict={
		'name': eachEvent.name,
		'description': eachEvent.description,
		'location': eachEvent.location,
		'categories': eachEvent.categories,
		'uid': eachEvent.uid,
		'last_modified': eachEvent.last_modified,
		'begin': eachEvent.begin,
		'end': eachEvent.end,
		'classification': eachEvent.classification,
		'status': eachEvent.status,
		'extras': extrasDict
	}
	eventsDb.addUpdate(eventDict)
printExtra(cal)
printWithPrefix('method:'+str(cal.method))
printWithPrefix('scale:'+str(cal.scale))

printTimeline(cal.timeline)
#for eachTimeline in cal.timeline:
#	printTimeline(eachTimeline)
for eachTodo in cal.todos:
	var=eachTodo
	varName='eachTodo'
	printWithPrefix(varName+':'+str(var))
	printExtra(var, incr=1)
	lineprefix(incr=-1)

#eventsDb.addUpdate(keyStr)
#eventsDb.save()

entryKeysToRemove=[]
for eachEntry in eventsDb:
	needsRemoval=False

	''''''

	if needsRemoval:
		entryKeysToRemove+=[]
	else:
		print('eachEntry='+str(eachEntry))

for eachKey in entryKeysToRemove:
	eventsDb.remove(eachKey)

#eventsDb.save()
