# Fonts needed because of utf-8. Document: https://pyfpdf.github.io/fpdf2/Unicode.html. Direct link: https://github.com/reingart/pyfpdf/releases/download/binary/fpdf_unicode_font_pack.zip
# Make a folder with the ones used in the file.
# Known bugs: If there is a sidestage and more than X Delegates, the Delegates are set to compete in the event despite not registering for it.
# If there is more than 4 groups of a combined event, something weird might happen

import collections
import os
from pickle import TRUE
from time import time,sleep
from flask import Flask,request
import subprocess
import json
from datetime import datetime
from copy import deepcopy
from collections import defaultdict
import random
import math
import numpy as np
from pandas import Timestamp
import webbrowser
import requests
from typing import Dict, Generic, Iterator, List, Optional, TypeVar # For the priority queue
from fpdf import FPDF # For pdfs. pip3 install fpdf2
import pytz # for timezones
import socket

Key = TypeVar("Key")

class MaxPQ(Generic[Key]):
	"""
	Pretty much taken from here: https://github.itu.dk/algorithms/AlgorithmsInPython/blob/master/itu/algs4/sorting/max_pq.py
	"""
	def __init__(self, _max: int = 200):
		self._pq: List[Optional[Key]] = [None] * (_max + 1)
		self._n = 0

	def insert(self, x: Key) -> None:
		if self._n == len(self._pq) - 1:
			self._resize(2 * len(self._pq))
		self._n += 1
		self._pq[self._n] = x
		self._swim(self._n)

	def max(self) -> Key:
		if self.is_empty():
			return 0

		assert self._pq[1] is not None
		return self._pq[1]

	def del_max(self) -> Key:
		_max = self._pq[1]
		assert _max is not None
		self._exch(1, self._n)
		self._n -= 1
		self._sink(1)
		self._pq[self._n + 1] = None
		if self._n > 0 and self._n == (len(self._pq) - 1) // 4:
			self._resize(len(self._pq) // 2)
		return _max

	def is_empty(self) -> bool:
		return self._n == 0

	def size(self) -> int:
		return self._n

	def __len__(self) -> int:
		return self.size()

	def _sink(self, k) -> None:
		while 2 * k <= self._n:
			j = 2 * k
			if j < self._n and self._less(j, j + 1):
				j += 1
			if not self._less(k, j):
				break
			self._exch(k, j)
			k = j

	def _swim(self, k: int) -> None:
		while k > 1 and self._less(k // 2, k):
			self._exch(k, k // 2)
			k = k // 2

	def _resize(self, capacity: int):
		temp: List[Optional[Key]] = [None] * capacity
		for i in range(1, self._n + 1):
			temp[i] = self._pq[i]
		self._pq = temp

	def _less(self, i: int, j: int):
		return self._pq[i][1] < self._pq[j][1]

	def _exch(self, i: int, j: int):
		self._pq[i], self._pq[j] = self._pq[j], self._pq[i]

	def __iter__(self) -> Iterator[Key]:
		"""Iterates over all the items in this priority queue in heap order."""
		copy: MaxPQ[Key] = MaxPQ(self.size())
		for i in range(1, self._n + 1):
			key = self._pq[i]
			assert key is not None
			copy.insert(key)
		for i in range(1, copy._n + 1):
			yield copy.del_max()

def basicPr():
	return 100000000 # So sorting work when someone hasn't competed

class Competitor():
	def __init__(self,name,id,citizenship,gender,wcaId):
		self.name = name
		self.id = id
		self.events = set()
		self.citizenship = citizenship
		self.gender = gender
		self.wcaId = wcaId
		self.prs = defaultdict(basicPr)
		self.availableDuring = set() # a set of events where they will be in the venue
		self.orga = 1 # for calculation. Actual orga get 3, for the time being 
		self.groups = {} # Event -> groupnum
		self.assignments = defaultdict(list)
		self.dob = ''
		self.age = 0
		self.stationNumbers = {}
		self.totalAssignments = 1 # so addition works

	def __str__(self):
		return self.name + " + info"

class Schedule():
	def __init__(self):
		self.name = ''
		self.longName= ''
		self.timezone = ''
		self.amountStations = 0
		self.events = [] # list of lists. Inner lists have three values: Event name, s time, and e time of r1.
		self.eventWOTimes = []
		self.timelimits = {}
		self.eventTimes = {} # event -> touple of start and end time
		self.eventCompetitors = defaultdict(list)
		self.daySplit = [0] # the index where a day changes. Len = days-1
		self.groups = {} # event -> groupnum -> group
		self.subSeqAmountCompetitors = {} # event+roundnumber -> amount of competitors
		self.subSeqGroupCount = {} # event+roundnumber -> number of groups
		self.stationOveriew = {}
		self.judgeStationOveriew = {}
		self.groupJudges = {} # event -> groupnum -> group. Made later
		self.groupRunners = {} # Will be event -> groupnum -> group. Made later
		self.groupScramblers = {} # Will be event -> groupnum -> group. Made later
		self.inVenue = defaultdict(set) # event -> set of people in venue
		self.unpred = set() # I didn't use this, but was planning on using it to account for some people not being present for all individual attempts for certain events. 
		self.overlappingEvents = defaultdict(list) # Event -> list of events happening during the timespan of it.
		self.groupTimes = {} # event -> groupnum -> tuple(timeS,timeE)
		self.subSeqGroupTimes = {} # event+roundnum -> groupnum -> tuple(timeS,timeE)
		self.organizers = None # List of organizers and delegates
		self.delegates = None # List of delegates
		self.advancements = {} # event -> round -> tuple (type,level)
		self.entire = []
		self.mbldCounter = 0
		self.sideStageEvents = set()
		self.maxAmountGroups = 0
		self.childActivityMapping = {} # Event -> group -> ID

	def order(self): # ordering events in schedule
		self.events.sort(key=lambda x:x[1]) 
	
	def order_entire(self):
		self.entire.sort(key=lambda x:x[1])

	def orderCompetitors(self,personInfo,combinedEvents): # For scrambling
		for event in self.eventCompetitors:
			if event == combinedEvents:
				for person in personInfo:
					comSplit = event.split('-')
					personInfo[person].prs[combinedEvents] = personInfo[person].prs[comSplit[0]] + personInfo[person].prs[comSplit[1]]
			self.eventCompetitors[event].sort(key=lambda x:personInfo[x].prs[event]*personInfo[x].orga)

	def getIndividualGroupTimes(self):
		for event in self.groups:
			self.groupTimes[event] = {}
			amountOfGroups = len(self.groups[event])
			diff = self.eventTimes[event][1] - self.eventTimes[event][0]
			perGroup = diff/amountOfGroups
			for groupNum in self.groups[event]:
				self.groupTimes[event][groupNum] = ((self.eventTimes[event][0]+ (perGroup*(groupNum-1))).round(freq='S'),(self.eventTimes[event][0]+ (perGroup*(groupNum))).round(freq='S'))
				# self.groupTimes[event][groupNum] = ("tid 1", "tid 2")

	def getSubSeqGroupTimes(self):
		for event in self.subSeqGroupCount:
			self.subSeqGroupTimes[event] = {}
			diff = self.eventTimes[event][1] - self.eventTimes[event][0]
			perGroup = diff/self.subSeqGroupCount[event]
			for groupNum in range(1,self.subSeqGroupCount[event]+1):
				self.subSeqGroupTimes[event][groupNum] = ((self.eventTimes[event][0]+ (perGroup*(groupNum-1))).round(freq='S'),(self.eventTimes[event][0]+ (perGroup*(groupNum))).round(freq='S'))


	def getDaySplit(self):
		for i in range(1,len(self.events)):
			if self.events[i][1].day == self.events[i-1][1].day:
				pass
			else:
				self.daySplit.append(i)

	def eventTimeChecker(self, event1,event2): # There might be more erros with equal end times, just fixed the last one
		if (event1[2] > event2[1] and event1[2] < event2[2]) or (event1[1] > event2[1] and event1[1] < event2[2]) or (event1[2] > event2[2] and event1[1] < event2[2]) or (event1[1] < event2[1] and event2[2] <= event1[2]):
			return True
		else:
			return False
	# if I weren't lazy this should be the same function
	def groupTimeChecker(self, event1,event2): # Group1 and group2
		if (event1[1] > event2[0] and event1[1] < event2[1]) or (event1[0] > event2[0] and event1[0] < event2[1]) or (event1[1] > event2[1] and event1[0] < event2[1]) or (event1[0] < event2[0] and event2[1] <= event1[1]):
			return True
		else:
			return False

	def identifyOverlap(self): # Which events overlap
		for idx, event in enumerate(self.events):
			for event2 in self.events[idx+1:]:
				if self.eventTimeChecker(event,event2):
					self.overlappingEvents[event[0]].append(event2[0])
					self.overlappingEvents[event2[0]].append(event[0])


def competitorBasicInfo(data):
	"""
	Get all the basic information for each competitor.
	"""
	comp_dict = {}
	year = int(datetime.now().strftime("%Y"))
	organizers = set()
	delegates = []
	for person in data['persons']:
		try:
			if person['registration']['status'] == 'accepted':
				debuff = 0
				competitor = Competitor(person["name"],person['registrantId'],person['countryIso2'],person['gender'],person['wcaId'])
				for val in person["roles"]: # getOrga
					if val in ('organizer','delegate','trainee-delegate'):
						competitor.orga = 1 # Setting this for sorting by speed
						organizers.add(person['name'])
						debuff = 1
					if val in ('delegate','trainee-delegate'):
						competitor.orga = 1 # Setting this for sorting by speed
						delegates.append(person['name'])
						debuff = 1
				competitor.age = year - int(person["birthdate"][:4]) #getAge
				competitor.dob = person["birthdate"]

				for eventData in person['personalBests']:
					if eventData['eventId'] not in ('333fm','444bf','333bf','555bf'):
						if eventData['type'] == 'average':
							if int(eventData['best']) < 200 and debuff:
								temp = int(eventData['best'])*3
							elif int(eventData['best']) < 2000 and debuff:
								temp = int(eventData['best'])*2.3
							elif debuff:
								temp = int(eventData['best'])*1.5
							else:
								temp = int(eventData['best'])
							competitor.prs[eventData['eventId']] = temp
					else:
						if eventData['type'] == 'single':
							if int(eventData['best']) < 200 and debuff:
								temp = int(eventData['best'])*3
							elif int(eventData['best']) < 2500 and debuff:
								temp = int(eventData['best'])*2
							elif debuff:
								temp = int(eventData['best'])*1.5
							else:
								temp = int(eventData['best'])
							competitor.prs[eventData['eventId']] = temp
				for event in person['registration']['eventIds']:
					competitor.events.add(event)
				comp_dict[person["name"]] = competitor
		except TypeError:
			pass
	return comp_dict,organizers, delegates

def scheduleBasicInfo(data,personInfo,organizers,delegates,stations,fixed,customGroups=[False], combinedEvents=None,just1GroupofBigBLD=True): # Custom groups is a dict, combined evnets is touple
	"""
	Get all the basic information for the schedule. 
	Doesn't store which stage events appear on, but will look into if events overlap (but not fully)
	"""
	
	if combinedEvents==None:
		combinedEvents = ('k','k')
	schedule = Schedule()
	schedule.amountStations = stations
	schedule.name = data['id']
	schedule.longName = data['name']
	already_there = set()
	timezone = pytz.timezone(data["schedule"]["venues"][0]["timezone"])
	tempFm = [] # not used for its purpose in the end
	tempMb = [] # not used for its purpose in the end
	for id_room, room in enumerate(data["schedule"]["venues"][0]['rooms']): # Assumes room one is the main stage
		for val in room["activities"]:
			starttime = Timestamp(val['startTime'][:-1]).tz_localize(pytz.utc).tz_convert(timezone)
			endtime = Timestamp(val['endTime'][:-1]).tz_localize(pytz.utc).tz_convert(timezone)
			if val['activityCode'][0] != 'o':
				if len(val['activityCode']) < 9:
					if val['activityCode'][-1] not in ['3','2','4'] and val['activityCode'][:-3] not in already_there:
						tempCombined = val['activityCode'][:-3]
						roundnum = val['activityCode'][-1]
						doo = True
						if tempCombined == combinedEvents[0]:
							tempCombined += '-'+combinedEvents[1]
						elif tempCombined == combinedEvents[1]:
							doo = False
						if doo:
							schedule.events.append([tempCombined,starttime,endtime])
							schedule.eventWOTimes.append(tempCombined)
							already_there.add(val['activityCode'][:-3])
							schedule.eventTimes[tempCombined] = (starttime,endtime)
							schedule.entire.append([tempCombined+roundnum,starttime,endtime])

							if id_room > 0:
								schedule.sideStageEvents.add(tempCombined)
					elif val['activityCode'][-1] in ['3','2','4']:
						tempCombined = val['activityCode'][:-3]
						roundnum = val['activityCode'][-1]
						schedule.eventTimes[tempCombined+val['activityCode'][-1]] = (starttime,endtime)
						schedule.entire.append([tempCombined+roundnum,starttime,endtime])
				else:
					# if val['activityCode'][:4] == '333f' and val['activityCode'][-1] not in ['3','2','4']:
					if val['activityCode'][:4] == '333f':
						tempFm.append([val['activityCode'][:-6]+val['activityCode'][-1],starttime,endtime])
						schedule.events.append([val['activityCode'][:-6]+val['activityCode'][-1],starttime,endtime])
						schedule.eventWOTimes.append(val['activityCode'][:-6]+val['activityCode'][-1])
						schedule.eventTimes[val['activityCode'][:-6]+val['activityCode'][-1]] = (starttime,endtime)
						if id_room > 0:
							schedule.sideStageEvents.add(val['activityCode'][:-6]+val['activityCode'][-1])
						# schedule.eventWOTimes.append(val['activityCode'][:-6])
						# schedule.eventTimes[val['activityCode'][:-6]] = (starttime,endtime)
					# elif val['activityCode'][:4] == '333m' and val['activityCode'][-1] not in ['3','2','4']:
					elif val['activityCode'][:4] == '333m':
						tempMb.append([val['activityCode'][:-6]+val['activityCode'][-1],starttime,endtime])
						schedule.mbldCounter += 1
						if schedule.mbldCounter != int(val['activityCode'][-1]):
							schedule.mbldCounter -= 1
						schedule.events.append([val['activityCode'][:-6]+val['activityCode'][-1],starttime,endtime])
						schedule.eventWOTimes.append(f"333mbf{val['activityCode'][-1]}")
						schedule.eventTimes[f"333mbf{val['activityCode'][-1]}"] = (starttime,endtime)
						if id_room > 0:
							schedule.sideStageEvents.add(val['activityCode'][:-6]+val['activityCode'][-1])
						# schedule.eventWOTimes.append(f"333mbf")
						# schedule.eventTimes[f"333mbf"] = (starttime,endtime)
					schedule.entire.append([val['activityCode'][:-6]+val['activityCode'][-1]+val['activityCode'][-4:-3],starttime,endtime])
			else:
				fs = f"{val['activityCode']}0"
				schedule.entire.append([fs,starttime,endtime])
	# if len(tempMb) <2: # not used for its purpose in the end
	# 	schedule.events += tempMb 
	# else:
	# 	schedule.unpred.add("333mbf")
	# if len(tempFm) <2: # not used for its purpose in the end
	# 	schedule.events += tempFm
	# else:
	# 	schedule.unpred.add("333fm")
	schedule.order() # Order the events by time in schedule
	schedule.getDaySplit() # See which events are each day
	schedule.organizers = organizers # Storing list of organizers and delegates
	schedule.delegates = delegates
	schedule.timezone = timezone
	schedule.order_entire()
	schedule.identifyOverlap() # See which events overlap. Doesn't account full overlaps, i.e. for events with same start/ending time
	# just1List = ['333fm','444bf','555bf','333mbf']
	just1List = ['333fm','444bf','555bf']
	if schedule.mbldCounter:
		for person in personInfo:
			if '333mbf' in personInfo[person].events:
				personInfo[person].events.remove('333mbf')
				for i in range(1,schedule.mbldCounter+1):
					personInfo[person].events.add(f"333mbf{i}")
					personInfo[person].prs[f"333mbf{i}"] = personInfo[person].prs[f"333mbf"]
		for i in range(1,schedule.mbldCounter+1):
			just1List.append(f"333mbf{i}")
	for person in personInfo: # Counting the combined events as one
		already =False
		for event in personInfo[person].events:
			if event in [combinedEvents[0],combinedEvents[1]] and not already:
				schedule.eventCompetitors[combinedEvents[0]+'-'+combinedEvents[1]].append(person)
				already =True
			elif event not in [combinedEvents[0],combinedEvents[1]]: 
				schedule.eventCompetitors[event].append(person)
	schedule.orderCompetitors(personInfo,combinedEvents[0]+'-'+combinedEvents[1]) # Ordering competitors by rank (used in group making and getting scramblers)
	if just1GroupofBigBLD:
		getGroupCount(schedule,fixed,stations,customGroups,just1List) # Getting the amount of groups needed
	else:
		getGroupCount(schedule,fixed,stations,customGroups) # Getting the amount of groups needed
	for event in schedule.groups:
		if len(schedule.groups[event]) > schedule.maxAmountGroups:
			schedule.maxAmountGroups = len(schedule.groups[event])
	schedule.getIndividualGroupTimes() # Seeing the start/end time of each group
	getAvailableDuring(personInfo,schedule,combinedEvents) # Identify during which events people should be present based on their registration

	for event in data['events']:
		schedule.timelimits[event['rounds'][0]['id'].split('-')[0]] = (event['rounds'][0]['timeLimit'],event['rounds'][0]['cutoff'])
		schedule.advancements[event['rounds'][0]['id'].split('-')[0]] = {}
		for Round in event['rounds']:
			advancement = Round['advancementCondition']
			eventNRound = Round['id'].split('-')
			if advancement: # has more rounds
				schedule.advancements[eventNRound[0]][int(eventNRound[1][1])] = (advancement['type'],int(advancement['level']))
			else:
				schedule.advancements[eventNRound[0]][int(eventNRound[1][1])] = (None,0)
	getSubSeqGroupCount(1,schedule)
	schedule.getSubSeqGroupTimes()
	if schedule.mbldCounter:
		for i in range(1,schedule.mbldCounter+1):
			schedule.timelimits[f"333mbf{i}"] = schedule.timelimits[event['rounds'][0]['id'].split('-')[0]]

	return schedule

def getAvailableDuring(personInfo,scheduleInfo,combinedEvents=None):
	"""
	Identify during which events people should be present based on their registration. 
	People are considered to be available for an event if they compete in it, or if they are competing on that day
	and have a registration for an event before and after the event.
	"""
	if combinedEvents==None:
		combinedEvents = ('k','k')
		combinedEvents1 = ('k-k')
	else:
		combinedEvents1 = combinedEvents[0]+'-'+combinedEvents[1]
	for person in personInfo:
		for idj, days in enumerate(scheduleInfo.daySplit):
			min = 18
			max = 0
			if idj != len(scheduleInfo.daySplit)-1:
				to = scheduleInfo.daySplit[idj+1]
			else:
				to = len(scheduleInfo.events)
			for idx,event in enumerate(scheduleInfo.events[days:to]):
				if event[0] in personInfo[person].events:
					if idx < min:
						min = idx
					if idx > max:
						max = idx
				elif event[0] == combinedEvents1:
					for comSplit in combinedEvents:
						if comSplit in personInfo[person].events:
							if idx < min:
								min = idx
							if idx > max:
								max = idx
			for event in scheduleInfo.events[days+min:days+max+1]:
				personInfo[person].availableDuring.add(event[0])
				scheduleInfo.inVenue[event[0]].add(person)

def combineEvents(event1,event2): # Pretty stupid function. The combined events is used super inconsistently
	return (event1,event2)

def getGroupCount(scheduleInfo,fixedSeating,stationCount,custom=[False],just1=[False]):
	"""
	The script isn't made for specifying a different amount of stations per event.
	Use the 'custom' variable to specify the exact amount of groups you want if there is something extraordinary
	'just1' is when you only want one group of the event.
	"""
	if type(custom) == dict: # dictionary
		for event in custom:
			scheduleInfo.groups[event] = {}
			for amount in range(1,custom[event]+1):
				scheduleInfo.groups[event][amount] = []
	if just1[0]:
		for event in just1:
			if event in scheduleInfo.eventWOTimes and event not in custom:
				scheduleInfo.groups[event] = {}
				scheduleInfo.groups[event][1] = []
	if fixedSeating:
		for event in scheduleInfo.eventCompetitors:
			if (event not in just1) and (event not in custom):
				scheduleInfo.groups[event] = {}

				for amount in range(1,np.max([math.ceil(len(scheduleInfo.eventCompetitors[event])/stationCount) +1,3])):
					scheduleInfo.groups[event][amount] = []
	else:
		# stationCount *=1.15
		for event in scheduleInfo.eventCompetitors:
			if (event not in just1) and (event not in custom):
				scheduleInfo.groups[event] = {}
				for amount in range(1,(np.max([math.ceil(len(scheduleInfo.eventCompetitors[event])/stationCount) +1,3]))):
					scheduleInfo.groups[event][amount] = []

def advancementCalculation(Type,level,competitorCount):
	if Type == "percent":
		return int((level/100) * competitorCount)
	elif Type == "ranking":
		return level
	elif Type == "attemptResult":
		print('Dont know how many will get under X, setting 75%')
		return int(competitorCount * 0.75)
	else:
		print("got a non existing type")
		raise NotImplementedError

def convertCompetitorCountToGroups(count,stations):
	expectedGroupNumber = math.ceil(count/stations)
	if expectedGroupNumber < 2:
		print("just one group for a subseq rounds, check if this inteded")
		print("manually bumping to 2")
		expectedGroupNumber+=1
	return expectedGroupNumber

def getSubSeqGroupCount(fixedCompetitors,scheduleInfo):
	if fixedCompetitors:
		for event in scheduleInfo.entire:
			if event[0][-1] == '2':
				proceeding = advancementCalculation(scheduleInfo.advancements[event[0][:-1]][1][0],scheduleInfo.advancements[event[0][:-1]][1][1],len(scheduleInfo.eventCompetitors[event[0][:-1]]))
				scheduleInfo.subSeqAmountCompetitors[event[0]] = proceeding
				scheduleInfo.subSeqGroupCount[event[0]] = convertCompetitorCountToGroups(proceeding,scheduleInfo.amountStations)
			elif event[0][-1] == '3':
				proceeding = advancementCalculation(scheduleInfo.advancements[event[0][:-1]][2][0],scheduleInfo.advancements[event[0][:-1]][2][1],scheduleInfo.subSeqAmountCompetitors[event[0][:-1]+'2'])
				scheduleInfo.subSeqAmountCompetitors[event[0]] = proceeding
				scheduleInfo.subSeqGroupCount[event[0]] = convertCompetitorCountToGroups(proceeding,scheduleInfo.amountStations)
			elif event[0][-1] == '4':
				proceeding = advancementCalculation(scheduleInfo.advancements[event[0][:-1]][3][0],scheduleInfo.advancements[event[0][:-1]][3][1],scheduleInfo.subSeqAmountCompetitors[event[0][:-1]+'3'])
				scheduleInfo.subSeqAmountCompetitors[event[0]] = proceeding
				scheduleInfo.subSeqGroupCount[event[0]] = convertCompetitorCountToGroups(proceeding,scheduleInfo.amountStations)
	else: # Waiting area
		raise NotImplementedError

def specialPeopleCompeteAssign(specialCompList,p2,personInfo,event,groups):
	specialCompList.sort(key=lambda x:personInfo[x].prs[event], reverse=True)
	part1 = specialCompList[:math.ceil(len(specialCompList)/2)]
	part2 = specialCompList[math.ceil(len(specialCompList)/2):]
	while len(part1) > 0: # Place slowest half in second fastest group
		comp = part1[0]
		part1 = part1[1:]
		groups[len(groups)-1].append(comp)
		personInfo[comp].groups[event] = len(groups)-1
		p2.remove(comp)
	while len(part2) > 0: # Place fastest half in fastest group
		comp = part2[0]
		part2 = part2[1:]
		groups[len(groups)].append(comp)
		personInfo[comp].groups[event] = len(groups)
		p2.remove(comp)

def popCompetitorAssign(p2,groups,personInfo,event,groupNum,forward):
	if forward:
		comp = p2[0]
		p2 = p2[1:]
	else:
		comp = p2[-1]
		p2 = p2[:-1]
	groups[groupNum].append(comp)
	personInfo[comp].groups[event] = groupNum
	return p2

def splitNonOverlapGroups(scheduleInfo,personInfo,event,fixed=True):
	"""
	Function called for events which do not have something overlapping.
	In the regular assignments, sets aside scramblerCount scramblers for each group
	"""
	dontSpeedScramble = ['333bf','444bf','555bf'] # for some reason very import to be list, otherwise reads substring
	groups = scheduleInfo.groups[event]
	totalComp = scheduleInfo.eventCompetitors[event]
	perGroup = int(len(totalComp)/len(groups))
	if event == '444': # manual amount of scramblers...
		scramblerCount = round((len(totalComp)/len(groups))/5)
	else:
		scramblerCount = round((len(totalComp)/len(groups))/5)
	p2 = deepcopy(totalComp)
	# special stuff when there are multiple delegates
	delegateCompetitors = [compDel for compDel in scheduleInfo.delegates if compDel in totalComp]
	if len(delegateCompetitors) > 1 and len(groups) > 1: # For orga
		specialPeopleCompeteAssign(delegateCompetitors,p2,personInfo,event,groups)

	# now for organizers
		orgaCompetitors = [compOrga for compOrga in scheduleInfo.organizers if compOrga in totalComp and compOrga not in scheduleInfo.delegates]
	else:
		orgaCompetitors = [compOrga for compOrga in scheduleInfo.organizers if compOrga in totalComp and compOrga]
	if len(orgaCompetitors) > 1 and len(groups) > 1:
		specialPeopleCompeteAssign(orgaCompetitors,p2,personInfo,event,groups)

	# Regular assigning now
	if event in dontSpeedScramble: # Don't take fast people aside for faster scrambling later
		for groupNum in range(1,len(groups)+1):
			while len(groups[groupNum]) < perGroup and len(p2) > 0: # Assigning slowest first
				p2 = popCompetitorAssign(p2,groups,personInfo,event,groupNum,False)
	else:
		# for groupNum in range(1,len(groups)+1):
		if event in ['333','222','skewb','pyram']:
			for groupNum in range(len(groups),0,-1):
				for _ in range(1,scramblerCount+1): # taking best people, to ensure there are scramblers later (not all fast in same group)
					p2 = popCompetitorAssign(p2,groups,personInfo,event,groupNum,True)
		else:
			for _ in range(1,scramblerCount+1): # taking best people, to ensure there are scramblers later (not all fast in same group)
				for groupNum in range(len(groups),0,-1):
					p2 = popCompetitorAssign(p2,groups,personInfo,event,groupNum,True)
		for groupNum in range(len(groups),0,-1):
			while len(groups[groupNum]) < perGroup and len(p2) > 0: # Assigning slowest first
				p2 = popCompetitorAssign(p2,groups,personInfo,event,groupNum,False)
	while len(p2) > 0: # If some people were somehow left out, add them in the last group
		p2 = popCompetitorAssign(p2,groups,personInfo,event,groupNum,False)
		groupNum = (groupNum+1) % len(groups[groupNum])
		if not groupNum:
			groupNum += 1

def splitIntoOverlapGroups(scheduleInfo,personInfo,combination,fixed):
	"""
	Assigns groups for all overlapping events at the same time, and does assignments.
	As I could not find a proper deterministic manner of getting judges and competitors,
	I have set it to perform simulations. This should find the best combination.
	It will print out if there were some mistake.
	Failing to assign a person adds 100 to the fail score, a missing judge is 1.
	"""
	all = []
	oneGroup = []
	combination2 = deepcopy(combination)
	for event in combination:
		if len(scheduleInfo.groups[event]) == 1:
			oneGroup.append(event)
		else:
			for person in scheduleInfo.eventCompetitors[event]:
				if len(scheduleInfo.delegates) >= 4:
					if person not in scheduleInfo.delegates[:5]:
						all.append(person)
				else: 
					if person not in scheduleInfo.delegates[:2]:
						all.append(person)

	if oneGroup:
		for event in oneGroup:
			combination2.remove(event)
			for person in scheduleInfo.eventCompetitors[event]:
				scheduleInfo.groups[event][1].append(person)
				personInfo[person].groups[event] = 1
	# very ugly way to do the side stage first
	sideStageFirst = []
	for event in combination2:
		if event in scheduleInfo.sideStageEvents:
			sideStageFirst.append(event)
	sideStageFirst.append('skip')
	for event in combination2:
		if event not in scheduleInfo.sideStageEvents:
			sideStageFirst.append(event)
	
	if len(scheduleInfo.delegates) >= 4:
		twoDelegates = scheduleInfo.delegates[0:5]
	else: # assuming we have atleast two delegates
		d1 = scheduleInfo.delegates[0] 
		d2 = scheduleInfo.delegates[1] 
		twoDelegates = [d1,d2]

	stillSide = True
	for event in sideStageFirst:
		if event == 'skip':
			stillSide = False
		else:
			groupNumList = [j for j in range(len(scheduleInfo.groups[event]))]
			for idDelegate, delegate in enumerate(twoDelegates):
				assigned = False
				for idy in groupNumList:
					if not assigned:
						if stillSide:
							if len(scheduleInfo.delegates) >= 4:
								if (twoDelegates[(idDelegate+2)%4] not in scheduleInfo.groups[event][idy+1]):
									checkLegal = True
									for event2 in personInfo[delegate].groups:
										if event2 in combination:
											if (not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][idy+1],scheduleInfo.groupTimes[event2][personInfo[delegate].groups[event2]])):
												pass # Check that they don't have an overlapping event
											else:
												checkLegal = False
									if checkLegal:
										scheduleInfo.groups[event][idy+1].append(delegate)
										personInfo[delegate].groups[event] = idy+1
										assigned =True
							else:
								if (twoDelegates[(idDelegate+1)%2] not in scheduleInfo.groups[event][idy+1]):
									checkLegal = True
									for event2 in personInfo[delegate].groups:
										if event2 in combination:
											if (not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][idy+1],scheduleInfo.groupTimes[event2][personInfo[delegate].groups[event2]])):
												pass # Check that they don't have an overlapping event
											else:
												checkLegal = False
									if checkLegal:
										scheduleInfo.groups[event][idy+1].append(delegate)
										personInfo[delegate].groups[event] = idy+1
										assigned =True

						else:
							if len(scheduleInfo.delegates) >= 4 and len(scheduleInfo.groups[event]) >= 4:
								checkLegal = True
								noDelegateOverlap = True
								for delegate2 in twoDelegates[:idDelegate]:
									if delegate2 in scheduleInfo.groups[event][idy+1]:
										noDelegateOverlap = False
								if noDelegateOverlap:
									for event2 in personInfo[delegate].groups:
										if event2 in combination:
											if (not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][idy+1],scheduleInfo.groupTimes[event2][personInfo[delegate].groups[event2]])):
												pass # Check that they don't have an overlapping event
											else:
												checkLegal = False
									if checkLegal:
										scheduleInfo.groups[event][idy+1].append(delegate)
										personInfo[delegate].groups[event] = idy+1
										assigned =True
							elif len(scheduleInfo.delegates) >= 4:
								if (twoDelegates[(idDelegate+2)%4] not in scheduleInfo.groups[event][idy+1]):
										checkLegal = True
										for event2 in personInfo[delegate].groups:
											if event2 in combination:
												if (not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][idy+1],scheduleInfo.groupTimes[event2][personInfo[delegate].groups[event2]])):
													pass # Check that they don't have an overlapping event
												else:
													checkLegal = False
										if checkLegal:
											scheduleInfo.groups[event][idy+1].append(delegate)
											personInfo[delegate].groups[event] = idy+1
											assigned =True
							else:
								if (twoDelegates[(idDelegate+1)%2] not in scheduleInfo.groups[event][idy+1]):
									checkLegal = True
									for event2 in personInfo[delegate].groups:
										if event2 in combination:
											if (not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][idy+1],scheduleInfo.groupTimes[event2][personInfo[delegate].groups[event2]])):
												pass # Check that they don't have an overlapping event
											else:
												checkLegal = False
									if checkLegal:
										scheduleInfo.groups[event][idy+1].append(delegate)
										personInfo[delegate].groups[event] = idy+1
										assigned =True
				if not assigned:
					print('failed', delegate, event)
					checkLegal = True
					for idy in groupNumList:
						for event2 in personInfo[delegate].groups:
							if event2 in combination:
								if (not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][idy+1],scheduleInfo.groupTimes[event2][personInfo[delegate].groups[event2]])):
									pass # Check that they don't have an overlapping event
								else:
									checkLegal = False
						if checkLegal:
							scheduleInfo.groups[event][idy+1].append(delegate)
							personInfo[delegate].groups[event] = idy+1
							assigned =True
							break
					print('fixed',delegate,event,idy+1)


	compByCount = [[] for _ in range(len(combination2))]
	for person in collections.Counter(all):
		compByCount[collections.Counter(all)[person]-1].append(person)


	bsh2 = deepcopy(scheduleInfo)
	bpes2 = deepcopy(personInfo)
	few_fails = 200000 # Default
	few_extras = 0
	few_mis = 0
	few_comp = 0
	final_failed_people = []
	for ii in range(100): #100 simulations
		if few_fails > 1:
			sh2 = deepcopy(scheduleInfo)
			pes2 = deepcopy(personInfo)
			for val in compByCount:
				random.shuffle(val)
			j = len(compByCount) -1
			fails = 0
			extras = 0
			failed_people = []
			while j >= 0:
				p2 = deepcopy(compByCount[j])
				while p2:
					for event in sideStageFirst:
						if event != 'skip':
							assigned = False
							if p2[0] in sh2.eventCompetitors[event]:
								groups = sh2.groups[event]
								totalComp = sh2.eventCompetitors[event]
								perGroup = len(totalComp)/len(groups)
								groupNumList = [j for j in range(len(groups))]
								random.shuffle(groupNumList)
								for idy in groupNumList:
									if not assigned:
										if len(groups[idy+1]) < np.min([perGroup+np.min([int(perGroup*.2),4]),scheduleInfo.amountStations]): # Making sure there is space in the group
											checkLegal = True
											for event2 in pes2[p2[0]].groups:
												if event2 in combination:
													# if event in ('skewb','444') and event2 in ('skewb','444'):
													if not sh2.groupTimeChecker(sh2.groupTimes[event][idy+1],sh2.groupTimes[event2][pes2[p2[0]].groups[event2]]):
														pass # Check that they don't have an overlapping event
													else:
														checkLegal = False
											if checkLegal:
												sh2.groups[event][idy+1].append(p2[0])
												pes2[p2[0]].groups[event] = idy+1
												assigned = True
												if len(groups[idy+1]) > perGroup:
													extras+=0.5
								if not assigned:
									fails +=1
									failed_people.append((p2[0],event))
					p2 = p2[1:]
				j -=1
			missing = judgePQOverlap(combination,sh2,pes2,fixed) # Perform assignment of staff
			score = (fails*100) + missing +(extras*0.75)
			if score < few_fails: # If there is fewer missing staff
				few_fails = score
				few_comp = fails
				few_extras = extras
				few_mis = missing
				bsh2 = deepcopy(sh2)
				bpes2 = deepcopy(pes2)
				final_failed_people = deepcopy(failed_people)

	scheduleInfo = deepcopy(bsh2)
	personInfo = deepcopy(bpes2)

	if few_fails > 0:
		print(f"{combination}: Totally missing {few_comp} competitors, and {few_mis} assignments. Some extra people ({few_extras*2}). {final_failed_people}")
	else:
		print(f'sucess in overlapping events ({combination})')
	return scheduleInfo,personInfo # For some reason it does not update the variables

def splitIntoGroups(scheduleInfo,personInfo,fixed=True):
	already = set()
	for event in scheduleInfo.events:
		if event[0] not in already:
			if event[0] not in scheduleInfo.overlappingEvents:
				splitNonOverlapGroups(scheduleInfo, personInfo, event[0],fixed)
				already.add(event[0])
			else: # Do one set of overlapping events
				combination = set()
				combination.add(event[0])
				for i in range(4): # Should get all potential overlaps. Kind of BFS
					tempSet = set()
					for event1 in combination:
						for toAdd in scheduleInfo.overlappingEvents[event1]:
							tempSet.add(toAdd)
					combination = combination.union(tempSet)
				combinationList = deepcopy(list(combination)) # For the sake of simulations. 
				scheduleInfo, personInfo = splitIntoOverlapGroups(scheduleInfo, personInfo, combinationList,fixed) # For some reason it does not update the variables
				already = already.union(combination) # Don't repeat the same combo of overlaps

	return scheduleInfo, personInfo # For some reason it does not update the variables

def getNoAssignmentInEvent(scheduleInfo,personInfo,event,groupNum,atleast1):
	pq = MaxPQ()
	for comp in scheduleInfo.eventCompetitors[event]: # First, get only the people who aren't staffing in any group
		if comp not in scheduleInfo.delegates:
			if comp not in scheduleInfo.groups[event][groupNum]:
				if comp not in atleast1:
					pq.insert([comp,math.log((len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
	return pq

def getAssignmentAlreadyInEvent(scheduleInfo,personInfo,event,groupNum,pq,used):
	for comp in scheduleInfo.eventCompetitors[event]:
		if comp not in used and comp not in scheduleInfo.delegates:
			if comp not in scheduleInfo.groups[event][groupNum]:
				pq.insert([comp,math.log((len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])

def placePeopleInVenueInPQ(scheduleInfo,personInfo,event,groupNum,pq,used):
	print(f"Grabbing people not signed up as judges for {event} g{groupNum} ")
	for comp in scheduleInfo.inVenue[event]:
		if comp not in used and not comp in scheduleInfo.groups[event][groupNum]:
			if comp in scheduleInfo.delegates:
				pq.insert([comp,0])
			else:
				pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])

def assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,atleast1,used):
	while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed:
		judge = pq.del_max()[0]
		personInfo[judge].totalAssignments +=1
		personInfo[judge].assignments[event].append(groupNum)
		scheduleInfo.groupJudges[event][groupNum].append(judge)
		atleast1.add(judge) 
		used.add(judge)

def getNeededStaffCount(scheduleInfo,event,groupNum): # This probably needs some work
	groupSize = len(scheduleInfo.groups[event][groupNum])
	scramblerCount = round(groupSize/3.4)
	
	# if len(scheduleInfo.groups[event])> 3: # account for runners too
	# 	scramblerCount *= 2
	if event in {'333bf','444bf','555bf'}:
		needed = groupSize + 2
	else:
		needed = groupSize + scramblerCount
	return needed

def assignJudgesPQNonOverlapStyle(event,scheduleInfo,personInfo):
	print('hej')
	scheduleInfo.groupJudges[event] = {}
	groups = scheduleInfo.groups[event]
	atleast1 = set() # Make sure everyone judges at least once before giving two assignments to other people
	for groupNum in groups:
		scheduleInfo.groupJudges[event][groupNum] = []
		needed = getNeededStaffCount(scheduleInfo,event,groupNum)
		pq = getNoAssignmentInEvent(scheduleInfo,personInfo,event,groupNum,atleast1)
		used = set() # keep track of who already staff in the group
		assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,atleast1,used)
		
		# If we need to assign some people more than once to get enough staff
		if len(scheduleInfo.groupJudges[event][groupNum]) < needed: 
			getAssignmentAlreadyInEvent(scheduleInfo,personInfo,event,groupNum,pq,used)
			assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,atleast1,used)
		
		if len(scheduleInfo.groupJudges[event][groupNum]) < needed: # If more people are needed, try all in the venue
			placePeopleInVenueInPQ(scheduleInfo,personInfo,event,groupNum,pq,used)
			assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,atleast1,used)
			if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
				print(f"Not possible for {event} group {groupNum}. Got {len(scheduleInfo.groupJudges[event][groupNum])} of {needed}")

def judgePQNonOverlap(event,scheduleInfo,personInfo,fixedSeating=True):
	if fixedSeating:
		assignJudgesPQNonOverlapStyle(event,scheduleInfo,personInfo)
	else:
		if (event not in ['no event here']): # Give just one assignment in the event per competitor
			scheduleInfo.groupJudges[event] = {}
			groups = scheduleInfo.groups[event]
			for group in groups:
				scheduleInfo.groupJudges[event][group] = []
			for competitor in scheduleInfo.eventCompetitors[event]:
				group_to_place = ((personInfo[competitor].groups[event]-2)%len(groups)) +1

				scheduleInfo.groupJudges[event][group_to_place].append(competitor)
				personInfo[competitor].totalAssignments +=1
				personInfo[competitor].assignments[event].append(group_to_place)
		else: # Get more staff to reduce downtime
			assignJudgesPQNonOverlapStyle(event,scheduleInfo,personInfo)

def judgePQOverlap(combination,scheduleInfo,personInfo,fixedSeating=True): 
	random.shuffle(combination)
	if fixedSeating:
		missing = 0
		for event in combination:
			scheduleInfo.groupJudges[event] = {}
			groups = scheduleInfo.groups[event]
			competitors = scheduleInfo.eventCompetitors[event]
			maybePeople = scheduleInfo.inVenue[event]
			for groupNum in groups:
				pq = MaxPQ()
				scheduleInfo.groupJudges[event][groupNum] = []
				needed = len(scheduleInfo.groups[event][groupNum]) + min(round(3/7*(len(scheduleInfo.groups[event][groupNum]))) +1,1)
				used = set() # those that were already tried
				for comp in competitors:
					if comp not in scheduleInfo.delegates:
						if comp not in scheduleInfo.groups[event][groupNum]: # Check they aren't competing in overlapping group
							checkLegal = True
							for event2 in personInfo[comp].groups:
								if event2 in combination:
									if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][personInfo[comp].groups[event2]]):
										pass
									else:
										checkLegal = False
							for event2 in personInfo[comp].assignments:# Checking for overlapping assignments
								if event2 in combination:
									for groupAssignment in personInfo[comp].assignments[event2]:
										if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][groupAssignment]):
											pass
										else:
											checkLegal = False
							if checkLegal:
								pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
				assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,set(),used)
				if len(scheduleInfo.groupJudges[event][groupNum]) < needed: # If we didn't get enough first time, check people in venue
					for comp in maybePeople:
						if comp not in used and not comp in scheduleInfo.groups[event][groupNum]:
							checkLegal = True
							for event2 in personInfo[comp].groups:
								if event2 in combination:
									if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][personInfo[comp].groups[event2]]):
										pass
									else:
										checkLegal = False
							for event2 in personInfo[comp].assignments:
								if event2 in combination:
									for groupAssignment in personInfo[comp].assignments[event2]:
										if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][groupAssignment]):
											pass
										else:
											checkLegal = False
							if checkLegal:
								if comp in scheduleInfo.delegates:
									pq.insert([comp,0])
								else:
									pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
					assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,set(),used)
					if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
						missing += needed-len(scheduleInfo.groupJudges[event][groupNum])
						# print(f"Not possible for {event} group {groupNum}. Got {len(scheduleInfo.groupJudges[event][groupNum])} of {needed}")
		return missing
	else:
		missing = 0
		for event in combination:
			scheduleInfo.groupJudges[event] = {}
			groups = scheduleInfo.groups[event]
			competitors = scheduleInfo.eventCompetitors[event]
			maybePeople = scheduleInfo.inVenue[event]
			for groupNum in groups:
				pq = MaxPQ()
				scheduleInfo.groupJudges[event][groupNum] = []
				if event not in ['333mbf','333mbf1','333mbf2','333mbf3','555bf','444bf']:
					needed = len(scheduleInfo.groups[event][groupNum])-1
				elif event in ['555bf','444bf']:
					needed = int(len(scheduleInfo.groups[event][groupNum])/2) + 2
				else:
					needed = int(len(scheduleInfo.groups[event][groupNum])/2) + 1
				used = set() # those that were already tried
				for comp in competitors:
					if comp not in scheduleInfo.delegates:
						if comp not in scheduleInfo.groups[event][groupNum]: # Check they aren't competing in overlapping group
							checkLegal = True
							for event2 in personInfo[comp].groups:
								if event2 in combination:
									if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][personInfo[comp].groups[event2]]):
										pass
									else:
										checkLegal = False
							for event2 in personInfo[comp].assignments:# Checking for overlapping assignments
								if event2 in combination:
									for groupAssignment in personInfo[comp].assignments[event2]:
										if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][groupAssignment]):
											pass
										else:
											checkLegal = False
							if checkLegal:
								if len(event) > 4:
									if event in ['333mbf','333mbf1','333mbf2','333mbf3','555bf','444bf']:
										if personInfo[comp].wcaId:
											pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
									else:
										pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
								else:
									pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
				assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,set(),used)
				if len(scheduleInfo.groupJudges[event][groupNum]) < needed: # If we didn't get enough first time, check people in veneu
					for comp in maybePeople:
						if comp not in used and not comp in scheduleInfo.groups[event][groupNum]:
							checkLegal = True
							for event2 in personInfo[comp].groups:
								if event2 in combination:
									if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][personInfo[comp].groups[event2]]):
										pass
									else:
										checkLegal = False
							for event2 in personInfo[comp].assignments:
								if event2 in combination:
									for groupAssignment in personInfo[comp].assignments[event2]:
										if not scheduleInfo.groupTimeChecker(scheduleInfo.groupTimes[event][groupNum],scheduleInfo.groupTimes[event2][groupAssignment]):
											pass
										else:
											checkLegal = False
							if checkLegal:
								if comp in scheduleInfo.delegates:
									pq.insert([comp,0])
								if event in ['333mbf','333mbf1','333mbf2','333mbf3','555bf','444bf']:
									if personInfo[comp].wcaId:
										pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
								else:
									pq.insert([comp,(math.log(len(personInfo[comp].events)))/(personInfo[comp].totalAssignments)])
					assignJudgesFromPQ(scheduleInfo,personInfo,event,groupNum,pq,needed,set(),used)
					if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
						missing += needed-len(scheduleInfo.groupJudges[event][groupNum])
						# print(f"Not possible for {event} group {groupNum}. Got {len(scheduleInfo.groupJudges[event][groupNum])} of {needed}")
		return missing

def assignJudges(scheduleInfo,personInfo,fixedSeating= True,dontAssign=True,mixed={}):
	"""
	Judge assignments for overlapping events is being called together with splitIntoOverapGroups, 
	as I still need to do simulations to find the best combo for judges.
	"""
	if dontAssign: # Don't assign judges when there is only one group
		for event in scheduleInfo.events:
			if len(scheduleInfo.groups[event[0]]) > 1:
				if event[0] not in scheduleInfo.overlappingEvents:
					if mixed:
						if event[0] in mixed:
							judgePQNonOverlap(event[0],scheduleInfo,personInfo,True)
						else:
							judgePQNonOverlap(event[0],scheduleInfo,personInfo,False)
					else:
						judgePQNonOverlap(event[0],scheduleInfo,personInfo,fixedSeating)
	else:
		for event in scheduleInfo.events:
			if event[0] not in scheduleInfo.overlappingEvents:
				if mixed:
					if event[0] in mixed:
						judgePQNonOverlap(event[0],scheduleInfo,personInfo,True)
					else:
						judgePQNonOverlap(event[0],scheduleInfo,personInfo,False)
				else:
					judgePQNonOverlap(event[0],scheduleInfo,personInfo,fixedSeating)

def reassignJudges(scheduleInfo,personInfo,blacklist = {None},fixed=True, mixed={}):
	for event in scheduleInfo.groups:
		scheduleInfo.groupScramblers[event] = {}
		scheduleInfo.groupRunners[event] = {}
		if mixed:
			if event in mixed:
				reassignJudgesEvents(event,scheduleInfo,personInfo,blacklist,True)
			else:
				reassignJudgesEvents(event,scheduleInfo,personInfo,blacklist,False)
		else:
			reassignJudgesEvents(event,scheduleInfo,personInfo,blacklist,fixed)
		
def reassignToScrambler(event,group,scheduleInfo,personInfo,blacklist = {None},fixed=True):
	scheduleInfo.groupJudges[event][group].sort(key=lambda x:personInfo[x].prs[event]*personInfo[x].orga)
	scrambler = ''
	passed = False
	justBroke = False
	if fixed:
		for potScram in scheduleInfo.groupJudges[event][group]: # Take fastest first
			justBroke = False
			if personInfo[potScram].age > 12 and potScram not in blacklist: # Arguably can be set lower/higher for min
				for idx,g in enumerate(personInfo[potScram].assignments[event]):
					if type(g)==str:
						gg = int(g[2:])
					else:
						gg =g
					if gg < group:
						if personInfo[potScram].assignments[event][idx] != f';S{group}':
							justBroke = True
							break
				if not justBroke:
					passed = True
					scrambler = potScram
					break
			elif passed:
				break
	else: 
		for potScram in scheduleInfo.groupJudges[event][group]: # Take fastest first
			if personInfo[potScram].age > 12 and potScram not in blacklist: # Arguably can be set lower/higher for min
				passed = True
				scrambler = potScram
				break
	if not passed:
		scrambler = scheduleInfo.groupJudges[event][group][0] # Take the fastest if no one is old enough
		print('passing scram',group,event,scrambler)
	if fixed:
		for idx,g in enumerate(personInfo[scrambler].assignments[event]):
			if type(g)==str:
				gg = int(g[2:])
			else:
				gg =g
			if gg >= group:
				scheduleInfo.groupJudges[event][g].remove(scrambler)
				scheduleInfo.groupScramblers[event][g].append(scrambler)
				personInfo[scrambler].assignments[event][idx] = f';S{g}'
	else:
		scheduleInfo.groupJudges[event][group].remove(scrambler)
		scheduleInfo.groupScramblers[event][group].append(scrambler)
		for idx,assignment in enumerate(personInfo[potScram].assignments[event]):
			if assignment == group:
				personInfo[scrambler].assignments[event][idx] = f';S{group}'

def reassignToRunner(event,group,scheduleInfo,personInfo,blacklist = {None},fixed=True): 
	scheduleInfo.groupJudges[event][group].sort(key=lambda x:personInfo[x].prs[event]*personInfo[x].orga)
	runner = ''
	passed = False
	justBroke = False
	if fixed:
		for potRun in scheduleInfo.groupJudges[event][group][::-1]: # Take slowest first
			justBroke = False
			if personInfo[potRun].age > 10 and personInfo[potRun].age < 40 and potRun not in blacklist: # Arguably can be set lower/higher for min
				for idx,g in enumerate(personInfo[potRun].assignments[event]):
					if type(g)==str:
						gg = int(g[2:])
					else:
						gg =g
					if gg < group:
						if personInfo[potRun].assignments[event][idx] != f';R{group}':
							justBroke = True
							break
				if not justBroke:
					passed = True
					runner = potRun
					break
			elif passed:
				break
	else: 
		for potRun in scheduleInfo.groupJudges[event][group][::-1]: # Take slowest first
			if personInfo[potRun].age > 12 and potRun not in blacklist: # Arguably can be set lower/higher for min
				passed = True
				runner = potRun
				break
	if not passed:
		runner = scheduleInfo.groupJudges[event][group][-1]
		print('passing runner',group,event,runner)
	if fixed:
		for idx,g in enumerate(personInfo[runner].assignments[event]):
			if type(g)==str:
				gg = int(g[2:])
			else:
				gg =g
			if gg >= group:
				scheduleInfo.groupJudges[event][g].remove(runner)
				scheduleInfo.groupRunners[event][g].append(runner)
				personInfo[runner].assignments[event][idx] = f';R{g}'
	else:
		scheduleInfo.groupJudges[event][group].remove(runner)
		scheduleInfo.groupRunners[event][group].append(runner)
		for idx,assignment in enumerate(personInfo[potRun].assignments[event]):
			if assignment == group:
				personInfo[runner].assignments[event][idx] = f';R{group}'

def determineScrambleCount(scheduleInfo,personInfo,event,groupNum):
	judgeCount = len(scheduleInfo.groupJudges[event][groupNum])
	groupSize = len(scheduleInfo.groups[event][groupNum])
	if event == '333bf':
		return 1
	else:
		# scramblers = round(groupSize/3)
		scramblers = 4
		# if groupSize <= 13:
		# 	scramblers = 2
		# else:
		# 	scramblers = 4 # manual
		# while (judgeCount-scramblers)/groupSize < 0.6:
		# 	scramblers -=1
		return scramblers

def reassignJudgesEvents(event,scheduleInfo,personInfo,blacklist = {None},fixed=True):
	for groupNum in scheduleInfo.groups[event]:
			scheduleInfo.groupScramblers[event][groupNum] = []
			scheduleInfo.groupRunners[event][groupNum] = []
	if event[:-1] != '333mbf' and event not in ['444bf','555bf']:
		if fixed: #or len(scheduleInfo.groups[event]) >3
			for groupNum in scheduleInfo.groups[event]:
				if event in scheduleInfo.groupJudges:
					if len(scheduleInfo.groupJudges[event][groupNum]) > 0: # If judges are assigned for the event
						# Always at least one scrambler
						reassignToScrambler(event,groupNum,scheduleInfo,personInfo,blacklist,fixed)
						# Alternate runner/scrambler. Only continue if there is enough judges available

						while len(scheduleInfo.groups[event][groupNum])< len(scheduleInfo.groupJudges[event][groupNum]): # Scramblers
							if len(scheduleInfo.groupScramblers[event][groupNum]) <= len(scheduleInfo.groupRunners[event][groupNum]):
								reassignToScrambler(event,groupNum,scheduleInfo,personInfo,blacklist,fixed)
							else: # Runners
								reassignToRunner(event,groupNum,scheduleInfo,personInfo,blacklist,fixed)
		else: ####
			for groupNum in scheduleInfo.groups[event]:
				if event in scheduleInfo.groupJudges:
					if len(scheduleInfo.groupJudges[event][groupNum]) > 0: # If judges are assigned for the event
						# Always at least one scrambler
						reassignToScrambler(event,groupNum,scheduleInfo,personInfo,blacklist,fixed)
						
						# Just scramblers, continue until you have enough
						scramblersNeeded = determineScrambleCount(scheduleInfo,personInfo,event,groupNum)
						while scramblersNeeded> len(scheduleInfo.groupScramblers[event][groupNum]) and len(scheduleInfo.groupJudges[event][groupNum]) > 1:
							# scrmbler stuff
							reassignToScrambler(event,groupNum,scheduleInfo,personInfo,blacklist,fixed)

def convertCSV(scheduleInfo,personInfo,outfile,combined=None):
	"""
	In the accepted CSV format of https://goosly.github.io/AGE/
	"""
	if combined: # Fix the assignment back to regular events
		combHy = combined[0]+'-'+combined[1]
		for person in personInfo:
			for comSplit in combined:
				if comSplit in personInfo[person].events:
					personInfo[person].groups[comSplit] = deepcopy(personInfo[person].groups[combHy])
				if combHy in personInfo[person].assignments:
					personInfo[person].assignments[comSplit] = deepcopy(personInfo[person].assignments[combHy])
			if combHy in personInfo[person].groups:
				personInfo[person].groups.pop(combHy)
			if combHy in personInfo[person].assignments:
				personInfo[person].assignments.pop(combHy)
	header = 'Name'
	for event in scheduleInfo.events:
		if combined:
			if event[0] == combHy:
				for event in event[0].split('-'):
					header+=f',{event}'
			else:
				header+=f',{event[0]}'
		else:
			header+=f',{event[0]}'
	hCSV = header.split(',')
	header+='\n'
	for person in personInfo:
		pString = str(person)
		for event in hCSV:
			if event in personInfo[person].groups:
				pString+=f"{personInfo[person].groups[event]}"
			if event in personInfo[person].assignments:
				for assignment in personInfo[person].assignments[event]:
					if type(assignment) == int:
						pString += f";J{assignment}" # judges
					else:
						pString += assignment
			pString+=','
		pString = pString[:-1]
		header+=pString+'\n'
	writeCSVf = open(outfile,'w')
	print(header,file=writeCSVf)
	writeCSVf.close()

def makePDFOverview(scheduleInfo,outfile):
	pdf = FPDF('p','mm', 'A4')

	pdf.add_page()

	pdf.set_auto_page_break(auto=True,margin=15)
	# See main for fonts. Needed because of utf-8 stuff and names
	pdf.add_font('DejaVu','', fname='fonts/DejaVuSansCondensed.ttf', uni=True) 
	pdf.add_font('DejaVub','', fname='fonts/DejaVuSansCondensed-Bold.ttf', uni=True)

	pdf.set_font('DejaVub','',22)
	pdf.cell(65,6,f'{scheduleInfo.name} Group Overview',ln=True)
	# for event1 in scheduleInfo.events:
	# 	event = event1[0]
	for activity in scheduleInfo.entire:
		if activity[0][-1] == '1':
			event = activity[0][:-1]
			for group in scheduleInfo.groups[event]:
				pdf.set_font('DejaVub','',20)
				pdf.cell(65,6,f'Runde 1 af {event}, gruppe {group}',ln=True) # Event and group
				pdf.set_font('DejaVu','',14)
				# Time duration
				pdf.cell(65,6,f'{scheduleInfo.groupTimes[event][group][0].time()}-{scheduleInfo.groupTimes[event][group][1].time()}',ln=True)
				pdf.set_font('DejaVub','',12)
				pdf.cell(45,6,'Competitors')
				pdf.cell(45,6,'Judges')
				pdf.cell(45,6,'Scramblers')
				pdf.cell(45,6,'Runners',ln=True)
				competitors = scheduleInfo.groups[event][group]
				if event in scheduleInfo.groupJudges:
					judges = scheduleInfo.groupJudges[event][group]
					scramblers = scheduleInfo.groupScramblers[event][group]
					runners = scheduleInfo.groupRunners[event][group]
				else:
					judges = []
					scramblers = []
					runners = []
				i = 0
				if len(judges) > 0 and len(judges) < len(competitors): # Warning of few staff
					pdf.cell(45,6,f'# {len(competitors)}')
					pdf.set_text_color(194,8,8) # Highlight red
					pdf.cell(45,6,f'{len(judges)}/{len(competitors)}')
					pdf.cell(45,6,f'{len(scramblers)}')
					pdf.cell(45,6,f'{len(runners)}',ln=True)
					pdf.set_text_color(0,0,0) # Back to black
				elif len(judges) == len(competitors) and len(scramblers) <=1: # Warning of few runners/scramblers
					pdf.cell(45,6,f'# {len(competitors)}')
					pdf.cell(45,6,f'{len(judges)}/{len(competitors)}')
					pdf.set_text_color(194,8,8)
					pdf.cell(45,6,f'{len(scramblers)}')
					pdf.cell(45,6,f'{len(runners)}',ln=True)
					pdf.set_text_color(0,0,0)
				elif len(judges) == len(competitors) and len(runners) <=1: # warning of few runners
					pdf.cell(45,6,f'# {len(competitors)}')
					pdf.cell(45,6,f'{len(judges)}/{len(competitors)}')
					pdf.cell(45,6,f'{len(scramblers)}')
					pdf.set_text_color(194,8,8)
					pdf.cell(45,6,f'{len(runners)}',ln=True)
					pdf.set_text_color(0,0,0)
				else: # All good
					pdf.cell(45,6,f'# {len(competitors)}')
					pdf.set_font('DejaVu','',12)
					pdf.cell(45,6,f'{len(judges)}/{len(competitors)}')
					pdf.cell(45,6,f'{len(scramblers)}')
					pdf.cell(45,6,f'{len(runners)}',ln=True)
				while i < len(competitors) or i < len(judges): # Print everyone
					pdf.set_font('DejaVu','',8)
					if len(competitors) > i and len(judges) > i and len(scramblers) > i and len(runners) > i: # Enough for now
						pdf.cell(45,6,f'{shortenName(competitors[i])}, {scheduleInfo.stationOveriew[event][group][competitors[i]]}') # HHHHH
						pdf.cell(45,6,f'{shortenName(judges[i])}')
						pdf.cell(45,6,f'{shortenName(scramblers[i])}')
						pdf.cell(45,6,f'{shortenName(runners[i])}',ln=True)
					elif len(judges) > i and len(scramblers) > i: # Enough judges and scramblers for now
						pdf.cell(45,6,f'{shortenName(competitors[i])}, {scheduleInfo.stationOveriew[event][group][competitors[i]]}')
						pdf.cell(45,6,f'{shortenName(judges[i])}')
						pdf.cell(45,6,f'{shortenName(scramblers[i])}',ln=True)
					elif len(competitors) > i and len(judges) > i: # Enough judges and competitors for now
						pdf.cell(45,6,f'{shortenName(competitors[i])}, {scheduleInfo.stationOveriew[event][group][competitors[i]]}')
						pdf.cell(45,6,f'{shortenName(judges[i])}',ln=True)
					elif len(competitors) > i and len(scramblers) > i: # If there are more scramblers than judges
						pdf.cell(45,6,f'{shortenName(competitors[i])}, {scheduleInfo.stationOveriew[event][group][competitors[i]]}')
						pdf.cell(45,9)
						pdf.cell(45,6,f'{shortenName(scramblers[i])}',ln=True)
					elif len(judges) > i: # only used in case there is 'bonus judge'
						pdf.cell(45,6,f'-')
						pdf.cell(45,6,f'{shortenName(judges[i])}',ln=True)
					else: # Only competitors left
						pdf.cell(45,6,f'{shortenName(competitors[i])}, {scheduleInfo.stationOveriew[event][group][competitors[i]]}',ln=True)
					i+=1
		elif activity[0][-1] in ['2','3','4']:
			event,roundNumber = activity[0][:-1],activity[0][-1]
			for group in scheduleInfo.subSeqGroupTimes[event+roundNumber]:
				pdf.set_font('DejaVub','',20)
				pdf.cell(65,6,f'Runde {roundNumber} af {event}, gruppe {group}',ln=True) # Event and group
				pdf.set_font('DejaVu','',14)
				pdf.cell(65,6,f'{scheduleInfo.subSeqGroupTimes[event+roundNumber][group][0].time()}-{scheduleInfo.subSeqGroupTimes[event+roundNumber][group][1].time()}',ln=True)
				pdf.set_font('DejaVu','',12)
				pdf.cell(65,6,f'Forventer {round(scheduleInfo.subSeqAmountCompetitors[event+roundNumber]/len(scheduleInfo.subSeqGroupTimes[event+roundNumber]),2)} deltagere',ln=True)
		else:
			pdf.set_font('DejaVub','',20)
			pdf.cell(65,6,f'{activity[0][:-1]}',ln=True)
			pdf.set_font('DejaVu','',14)
			# Time duration
			pdf.cell(65,6,f'{activity[1].time()}-{activity[2].time()}',ln=True)
				
				
	pdf.output(outfile)

def shortenName(name):
	while len(name) > 26:
		lname = name.split(' ')
		lname = lname[:-2] + [lname[-1]]
		name = ' '.join(lname)
	return name

def writeNames(personlist,progress,ln,pdf):
	pdf.set_font('DejaVuB','',9.2)
	pdf.cell(50,3.2,f'{shortenName(personlist[progress].name)}')
	pdf.cell(16,3.2,f'ID: {personlist[progress].id}',ln=ln)

def writeCompeteLine(personInfo,personlist,progress,ln,pdf):
	pdf.set_font('DejaVu','',6)
	compete = 'Deltager (Gælder kun for første runder)' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Competitor (Only applies for first rounds)'
	pdf.cell(19.5,2.3,'')
	pdf.cell(16.5,2.3,compete)
	pdf.cell(30.5,2.3,'',ln=ln)

def writeHeaderCards(personInfo,personlist,progress,ln,pdf):
	pdf.set_font('DejaVu','',6)
	table = 'Bord' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Table'
	group = 'Gruppe' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Group'
	event = 'Disciplin' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Event'
	helping = 'Hjælper' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Helper'
	pdf.cell(18.5,2,event)
	pdf.cell(7.8,2,group)
	pdf.cell(8,2,table)
	pdf.cell(31.5,2,helping,ln=ln)

def eventPatch(personInfo,personlist,scheduleInfo,progress,event,ln,pdf,mixed={}):
	translate = {'333':'3x3','222':'2x2','444':'4x4','555':'5x5','666':'6x6','777':'7x7',
	'333oh':'3x3 OH','333fm':'333fm','333mbf':'Multi','333bf':'3BLD','minx':'Megaminx','pyram':'Pyraminx',
	'skewb':'Skewb','clock':'Clock','555bf':'5BLD','444bf':'4BLD','sq1':'Square-1','333mbf1':'Multi A1','333mbf2':'Multi A2','333mbf3':'Multi A3'}
	pdf.set_font('DejaVu','',8.8)
	line_height = pdf.font_size *1.5
	col_width = pdf.epw / 10

	# Event
	pdf.multi_cell(18,line_height,translate[event],border=1, ln=3)

	# Group and station
	if event in personInfo[personlist[progress].name].groups:
		if personInfo[personlist[progress].name].stationNumbers[event] < 10:
			pdf.multi_cell(16,line_height,f" G{str(personInfo[personlist[progress].name].groups[event])}  |  {personInfo[personlist[progress].name].stationNumbers[event]} ",border=1, ln=3)
		else:
			pdf.multi_cell(16,line_height,f" G{str(personInfo[personlist[progress].name].groups[event])}  |  {personInfo[personlist[progress].name].stationNumbers[event]}",border=1, ln=3)
	else:
		pdf.multi_cell(16,line_height,'  ',border=1, ln=3)

	# assignments
	if mixed:
	# if mixed:
		if event in mixed:
			judge = 'Døm(sid):' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Judge(sit):'
		else:
			judge = 'Døm(løb):' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Judge(run):'
	# elif scheduleInfo.maxAmountGroups > 3:
	# 	if len(scheduleInfo.groups[event]) > 3:
	# 		judge = 'Døm(sid):' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Judge(sit):'
	# 	else:
	# 		judge = 'Døm(løb):' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Judge(run):'
	else:
		judge = 'Døm:' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Judge:'
	scram = 'Bland:' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Scramb:'
	run = 'Løb:' if personInfo[personlist[progress].name].citizenship == 'DK' else 'Run:'

	strlist = sorted([f'{val}' if len(str(val)) ==1 else f'{val[1:]}' for val in personInfo[personlist[progress].name].assignments[event]])
	if strlist:
		if str(strlist[0][0]) in '123456789':
			sttr = f"{judge} "+', '.join(strlist)
		elif strlist[0][0] == 'S':
			sstrlist = [val[1:] for val in strlist]
			sttr = f"{scram} " + ', '.join(sstrlist)
		elif strlist[0][0] == 'R':
			sstrlist = [val[1:] for val in strlist]
			sttr = f"{run} " + ', '.join(sstrlist)
		else:
			sttr = ', '.join(strlist)
	else:
		sttr = ', '.join(strlist)

	pdf.multi_cell(28,line_height,sttr,border=1, ln=3,align='R')
	pdf.multi_cell(4,line_height,'',border=0, ln=3)
	if ln:
		pdf.ln(line_height)

def compCards(scheduleInfo,personInfo,outfile,mixed={}):
	pdf = FPDF()
	pdf.set_top_margin(4.5)
	pdf.set_left_margin(4.5)
	pdf.set_auto_page_break(False)
	pdf.add_page()
	pdf.add_font('DejaVu','', fname='fonts/DejaVuSansCondensed.ttf', uni=True)
	pdf.add_font('DejaVub','', fname='fonts/DejaVuSansCondensed-Bold.ttf', uni=True)
	pdf.set_font('DejaVu','',7)
	# personInfo.sort(key=lambda x:x['name'])
	personlist = [val for val in personInfo.values()]
	personlist.sort(key=lambda x:x.name)
	progress = 0
	event_list = []
	for event in scheduleInfo.events:
		sevent = event[0].split('-')
		for event_ in sevent:
			event_list.append(event_)
	while progress < len(personlist):
		if pdf.get_y() > 220: # Potentially adjust this based on the amount of competitors
			pdf.add_page()
		if progress+2 < len(personlist):
			writeNames(personlist,progress,False,pdf)
			writeNames(personlist,progress+1,False,pdf)
			writeNames(personlist,progress+2,True,pdf)
			writeCompeteLine(personInfo,personlist,progress,False,pdf)
			writeCompeteLine(personInfo,personlist,progress+1,False,pdf)
			writeCompeteLine(personInfo,personlist,progress+2,True,pdf)
			writeHeaderCards(personInfo,personlist,progress,False,pdf)
			writeHeaderCards(personInfo,personlist,progress+1,False,pdf)
			writeHeaderCards(personInfo,personlist,progress+2,True,pdf)
			for event in event_list:
				eventPatch(personInfo,personlist,scheduleInfo,progress,event,False,pdf,mixed)
				eventPatch(personInfo,personlist,scheduleInfo,progress+1,event,False,pdf,mixed)
				eventPatch(personInfo,personlist,scheduleInfo,progress+2,event,True,pdf,mixed)

		elif progress+1 < len(personlist):
			writeNames(personlist,progress,False,pdf)
			writeNames(personlist,progress+1,True,pdf)
			writeCompeteLine(personInfo,personlist,progress,False,pdf)
			writeCompeteLine(personInfo,personlist,progress+1,True,pdf)
			writeHeaderCards(personInfo,personlist,progress,False,pdf)
			writeHeaderCards(personInfo,personlist,progress+1,True,pdf)
			for event in event_list:
				eventPatch(personInfo,personlist,scheduleInfo,progress,event,False,pdf,mixed)
				eventPatch(personInfo,personlist,scheduleInfo,progress+1,event,True,pdf,mixed)
		else:
			writeNames(personlist,progress,True,pdf)
			writeCompeteLine(personInfo,personlist,progress,True,pdf)
			writeHeaderCards(personInfo,personlist,progress,True,pdf)
			for event in event_list:
				eventPatch(personInfo,personlist,scheduleInfo,progress,event,True,pdf,mixed)
		pdf.ln(5)
		progress +=3

	pdf.output(outfile)

def getRegList(personInfo,outfile):
	pdf = FPDF()
	pdf.add_page()
	pdf.add_font('DejaVu','', fname='fonts/DejaVuSansCondensed.ttf', uni=True)
	pdf.set_font('DejaVu','',8)
	line_height = pdf.font_size *3
	col_width = pdf.epw / 9
	personlist = [val for val in personInfo.values()]
	personlist.sort(key=lambda x:x.name)
	for person in personlist:
		pdf.multi_cell(10,line_height,' ',border=1, ln=3)
		pdf.multi_cell(60,line_height,person.name,border=1, ln=3)
		if person.wcaId:
			pdf.multi_cell(col_width,line_height,person.wcaId,border=1, ln=3)
		else:
			pdf.multi_cell(col_width,line_height,'newcomer',border=1, ln=3)
			pdf.multi_cell(10,line_height,person.citizenship,border=1, ln=3)
			pdf.multi_cell(6,line_height,person.gender,border=1, ln=3)
			pdf.multi_cell(col_width,line_height,person.dob,border=1, ln=3)
			pdf.multi_cell(col_width,line_height,'DSF medlem?',border=1, ln=3)
			pdf.multi_cell(10,line_height,' ',border=1, ln=3)
		pdf.ln(line_height)
	pdf.output(outfile)

def getStationNumbers(scheduleInfo,personInfo,combined,stages):
	if not stages:
		for event in scheduleInfo.eventWOTimes:
			scheduleInfo.stationOveriew[event] = {}
			for groupNum in scheduleInfo.groups[event]:
				scheduleInfo.stationOveriew[event][groupNum] = {}
				for idx,person in enumerate(scheduleInfo.groups[event][groupNum]):
					personInfo[person].stationNumbers[event] = idx+1
					scheduleInfo.stationOveriew[event][groupNum][person] = idx+1
		# if scheduleInfo.maxAmountGroups > 3:
		# 	for event in scheduleInfo.eventWOTimes:
		# 		scheduleInfo.judgeStationOveriew = {}
		# 		if len(scheduleInfo.groups[event]) > 3:
		# 			scheduleInfo.judgeStationOveriew[event] = {}
		# 			for groupNum in scheduleInfo.groups[event]:
		# 				scheduleInfo.judgeStationOveriew[event][groupNum] = {}
		# 				for idx,person in enumerate(scheduleInfo.groupJudges[event][groupNum]):
		# 					scheduleInfo.judgeStationOveriew[event][groupNum][person] = idx+1
	else:
		for event in scheduleInfo.eventWOTimes:
			scheduleInfo.stationOveriew[event] = {}
			for groupNum in scheduleInfo.groups[event]:
				scheduleInfo.stationOveriew[event][groupNum] = {}
				counter = 0
				realCounter = 0
				while realCounter < len(scheduleInfo.groups[event][groupNum]):
					for stage in range(stages):
						if stage == 0:
							counter +=1
						if realCounter < len(scheduleInfo.groups[event][groupNum]):
							person = scheduleInfo.groups[event][groupNum][realCounter]
							personInfo[person].stationNumbers[event] = int(stage*(scheduleInfo.amountStations/stages) + (counter))
							scheduleInfo.stationOveriew[event][groupNum][person] = int(stage*(scheduleInfo.amountStations/stages) + (counter))
							realCounter += 1

		# if scheduleInfo.maxAmountGroups > 3:
		# 	scheduleInfo.judgeStationOveriew = {}
		# 	for event in scheduleInfo.eventWOTimes:
		# 		scheduleInfo.judgeStationOveriew[event] = {}
		# 		if len(scheduleInfo.groups[event]) > 3:
		# 			scheduleInfo.judgeStationOveriew[event][groupNum] = {}
		# 			for groupNum in scheduleInfo.groups[event]:
		# 				scheduleInfo.judgeStationOveriew[event][groupNum] = {}
		# 				counter = 0
		# 				realCounter = 0
		# 				while realCounter < len(scheduleInfo.groupJudges[event][groupNum]):
		# 					for stage in range(stages):
		# 						if stage == 0:
		# 							counter +=1
		# 						if realCounter < len(scheduleInfo.groupJudges[event][groupNum]):
		# 							person = scheduleInfo.groupJudges[event][groupNum][realCounter]
		# 							scheduleInfo.judgeStationOveriew[event][groupNum][person] = int(stage*(scheduleInfo.amountStations/stages) + (counter))
		# 							realCounter += 1
					
	if combined: # Fix the assignment back to regular events
		combHy = combined[0]+'-'+combined[1]
		for person in personInfo:
			for comSplit in combined:
				if comSplit in personInfo[person].events:
					personInfo[person].stationNumbers[comSplit] = deepcopy(personInfo[person].stationNumbers[combHy])
			if combHy in personInfo[person].stationNumbers:
				personInfo[person].stationNumbers.pop(combHy)

def CSVForScorecards(scheduleInfo,personInfo,combined,outfile):
	header = 'Name,Id'
	mbldDone = False
	if combined:
		combHy = combined[0]+'-'+combined[1]
	for event in scheduleInfo.events:
		if combined:
			if event[0] == combHy:
				for event in event[0].split('-'):
					header+=f',{event}'
			elif scheduleInfo.mbldCounter and not mbldDone:
				if event[0][:-1] == '333mbf':
					mbldDone = True
					header+=',333mbf'
				else:
					header+=f',{event[0]}'
			elif event[0][:-1] != '333mbf':
				header+=f',{event[0]}'
		else:
			if scheduleInfo.mbldCounter and not mbldDone:
				if event[0][:-1] == '333mbf':
					mbldDone = True
					header+=',333mbf'
			elif event[0][:-1] != '333mbf':
				header+=f',{event[0]}'

	hCSV = header.split(',')
	header+='\n'
	# personlist = [val[0] for val in sorted(personInfo.items(),key= lambda x:x[1].id)] # should not be needed, as it should be sorted already
	for person in personInfo:
		pString = str(person) + ',' + str(personInfo[person].id)
		for event in hCSV[1:]:
			if event in personInfo[person].groups:
				pString+=f"{personInfo[person].groups[event]};{personInfo[person].stationNumbers[event]}"
			elif mbldDone and event =='333mbf' and '333mbf1' in personInfo[person].groups:
				pString+=f"{personInfo[person].groups['333mbf1']};{personInfo[person].stationNumbers['333mbf1']}"
			pString+=','
		pString = pString[:-1]
		header+=pString+'\n'
	writeCSVf = open(outfile,'w')
	print(header,file=writeCSVf)
	writeCSVf.close()

def CSVForTimeLimits(scheduleInfo,personInfo,combined,outfile):
	header = ''
	mbldDone = False
	if combined:
		combHy = combined[0]+'-'+combined[1]
	for event in scheduleInfo.events:
		if combined:
			if event[0] == combHy:
				for event in event[0].split('-'):
					header+=f',{event}'
			elif scheduleInfo.mbldCounter and not mbldDone:
				if event[0][:-1] == '333mbf':
					mbldDone = True
					header+=',333mbf'
				else:
					header+=f',{event[0]}'
			elif event[0][:-1] != '333mbf':
				header+=f',{event[0]}'
		else:
			if scheduleInfo.mbldCounter and not mbldDone:
				if event[0][:-1] == '333mbf':
					mbldDone = True
					header+=',333mbf'
			elif event[0][:-1] != '333mbf':
				header+=f',{event[0]}'
	header = header[1:]
	hCSV = header.split(',')

	header+='\n'
	for event in hCSV:
		t, c = scheduleInfo.timelimits[event]
		if t:
			if (not t['cumulativeRoundIds']) and (not c):
				header += f"T;{t['centiseconds']},"
			elif len(t['cumulativeRoundIds']) > 1:
				eventstring = ''
				for tlevent in t['cumulativeRoundIds']:
					eventstring += f";{tlevent.split('-')[0]}"
				header += f"S;{t['centiseconds']}{eventstring}," # HHHHH
			elif t['cumulativeRoundIds']:
				for tlevent in t['cumulativeRoundIds']:
					eventstring = f"{tlevent.split('-')[0]}"
				header += f"C;{t['centiseconds']},"
			elif c:
				header += f"K;{c['attemptResult']};{t['centiseconds']},"
		else: # multi bld
			header += f"M,"
	header = header[:-1]
	writeCSVf = open(outfile,'w')
	print(header,file=writeCSVf)
	writeCSVf.close()

def competitorForOTS(personInfo,name,id,citizenship,gender,wcaid,events,age):
	comp = Competitor(name,id,citizenship,gender, wcaid)
	for event in events:
		comp.events.add(event)
	comp.age = age
	personInfo[name] = comp

# def clientTest():
# 	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	client.connect(('localhost', 8001))
# # 	webpage = "https://www.worldcubeassociation.org/oauth/authorize?client_id=8xB-6U1fFcZ9PAy80pALi9E7nzfoF44W4cMPyIUXrgY&redirect_uri=http%3A%2F%2Flocalhost%3A8001&response_type=token&scope=manage_competitions+public"
# # 	webbrowser.get("x-www-browser").open(webpage,new=0)
# 	token = client.recv(64).decode()
# 	return token

def genTokenLengthy():
	subprocess.Popen(["python3 flaskServer.py"], shell=True,stdin=None, stdout=None, stderr=None, close_fds=True)
	webpage = "https://www.worldcubeassociation.org/oauth/authorize?client_id=8xB-6U1fFcZ9PAy80pALi9E7nzfoF44W4cMPyIUXrgY&redirect_uri=http%3A%2F%2Flocalhost%3A8001&response_type=code&scope=manage_competitions+public"
	webbrowser.get("x-www-browser").open(webpage,new=0)
	# token = clientTest()
	# print(token)
	sleep(1)
	# print(token)
	# return token


def genTokenNoob():
	# webpage = "https://www.worldcubeassociation.org/oauth/authorize?client_id=8xB-6U1fFcZ9PAy80pALi9E7nzfoF44W4cMPyIUXrgY&redirect_uri=http%3A%2F%2Flocalhost%3A8001&response_type=token&scope=manage_competitions+public"
	webpage = "https://www.worldcubeassociation.org/oauth/authorize?client_id=8xB-6U1fFcZ9PAy80pALi9E7nzfoF44W4cMPyIUXrgY&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=token&scope=manage_competitions+public" # copy manually
	webbrowser.get("x-www-browser").open(webpage,new=0)

	token = input("A browser should open. Copy the token from the URL and paste it here") # old when manually input

	return token

def getHeaderForWCIF():
	# genTokenLengthy()
	token = genTokenNoob()
	with open('authcode','w') as f:
		f.write(token.strip())
	return {'Authorization':f"Bearer {token}"}

def getWcif(id):
	if not os.path.exists("authcode"):
		header = getHeaderForWCIF()
	else:
		with open('authcode','r') as f:
			token = f.readline().strip('\n')
			header = {'Authorization':f"Bearer {token}"}
	while True:
		wcif = requests.get(f"https://www.worldcubeassociation.org/api/v0/competitions/{id}/wcif",headers=header)
		if wcif.status_code == 401:
			header = getHeaderForWCIF()
			wcif = requests.get(f"https://www.worldcubeassociation.org/api/v0/competitions/{id}/wcif",headers=header)
		else:
			break
	assert wcif.status_code == 200
	return wcif,header

def postWcif(id,wcif,header):
	r = requests.patch(f"https://www.worldcubeassociation.org/api/v0/competitions/{id}/wcif", json=wcif,headers=header)
	print(r)
	print(r.content)

def updateScrambleCount(data,scheduleInfo): 
	for idx,event in enumerate(data['events']): 
		scrambleSetCount = len(scheduleInfo.groups[event['id']])
		data['events'][idx]['rounds'][0]['scrambleSetCount'] = scrambleSetCount
		for rid,round in enumerate(event['rounds']): # Subsequent rounds
			roundNumber = round['id'].split('-')[1][1:]
			if roundNumber != '1':
				scrambleSetCount = scheduleInfo.subSeqGroupCount[event['id']+roundNumber]
				data['events'][idx]['rounds'][rid]['scrambleSetCount'] = scrambleSetCount

def cleanChildActivityWCIF(data,scheduleInfo):
	for vid, venue in enumerate(data['schedule']['venues']):
		for rid,room in enumerate(venue['rooms']):
			for aid,activity in enumerate(room['activities']):
				eventSplit = activity['activityCode'].split('-')
				# if eventSplit[1][-1] == '1' and eventSplit[0] in scheduleInfo.groupTimes: # just for r1
				data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'] = []
				data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['extensions'] = []

def cleanAssignmentsWCIF(data):
	for pid,person in enumerate(data['persons']):
		if type(person['registration']) == dict:
			if person['registration']['status'] == 'accepted':
				data['persons'][pid]['assignments'] = []

def createChildActivityWCIF(data,scheduleInfo):
	childIdCounter= max([int(activity['id']) for vid, venue in enumerate(data['schedule']['venues'])
		for rid,room in enumerate(venue['rooms'])
			for aid,activity in enumerate(room['activities'])])+1
	extensionTemplate = {'id': 'groupifier.CompetitionConfig', 
	'specUrl': 'https://groupifier.jonatanklosko.com/wcif-extensions/CompetitionConfig.json', 
	'data': {'capacity': 1, 'groups': 1, 'scramblers': 2, 'runners': 2, 'assignJudges': True}}
	childTemplate = {'id': 0, 'name': 'Event Name, Round 0, Group 0', 
	'activityCode': 'wcaeventid-r0-g0', 'startTime': 'yyyy-mm-ddThh:mm:ssZ', 'endTime': 'yyyy-mm-ddThh:mm:ssZ', 
	'childActivities': [], 'extensions': []}
	for vid, venue in enumerate(data['schedule']['venues']):
		for rid,room in enumerate(venue['rooms']):
			for aid,activity in enumerate(room['activities']):
				eventSplit = activity['activityCode'].split('-')
				if eventSplit[1][-1] == '1' and eventSplit[0] in scheduleInfo.groupTimes:
					scheduleInfo.childActivityMapping[eventSplit[0]] = {}
					data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['extensions'].append(deepcopy(extensionTemplate))
					data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['extensions'][0]['data']['groups'] = len(scheduleInfo.groupTimes[eventSplit[0]])
					data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['extensions'][0]['data']['scramblers'] = len(scheduleInfo.groupScramblers[eventSplit[0]][1])
					data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['extensions'][0]['data']['runners'] = len(scheduleInfo.groupRunners[eventSplit[0]][1])
					for gid,groupNum in enumerate(scheduleInfo.groupTimes[eventSplit[0]]):
						data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'].append(deepcopy(childTemplate))
						data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][gid]['id'] = childIdCounter
						scheduleInfo.childActivityMapping[eventSplit[0]][groupNum] =childIdCounter
						childIdCounter += 1
						data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][gid]['name'] = f"{data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['name']}, Round 1 Group {groupNum}"
						data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][gid]['activityCode'] = f"{data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['activityCode']}-g{groupNum}"
						startTime = str(scheduleInfo.groupTimes[eventSplit[0]][groupNum][0].tz_convert(pytz.utc).to_datetime64()).split('.')[0]+'Z'
						endTime = str(scheduleInfo.groupTimes[eventSplit[0]][groupNum][1].tz_convert(pytz.utc).to_datetime64()).split('.')[0]+'Z'
						data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][gid]['startTime'] = startTime
						data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][gid]['endTime'] = endTime
				elif eventSplit[0]+eventSplit[1][-1] in scheduleInfo.subSeqGroupCount: # subsequent round extension for groupifier
					data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['extensions'].append(deepcopy(extensionTemplate))
					data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['extensions'][0]['data']['groups'] = scheduleInfo.subSeqGroupCount[eventSplit[0]+eventSplit[1][-1]]
					# for groupNum in range(1,scheduleInfo.subSeqGroupCount[eventSplit[0]+eventSplit[1][-1]]+1):
					# 	data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'].append(deepcopy(childTemplate))
						
					# 	data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][groupNum-1]['id'] = childIdCounter
					# 	# scheduleInfo.childActivityMapping[eventSplit[0]][groupNum] =childIdCounter # not fixed for subseq
					# 	childIdCounter += 1
					# 	data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][groupNum-1]['name'] = f"{data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['name']}, Round {eventSplit[1][-1]} Group {groupNum}"
					# 	data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][groupNum-1]['activityCode'] = f"{data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['activityCode']}-g{groupNum}"
						
					# 	startTime = str(scheduleInfo.subSeqGroupTimes[eventSplit[0]+eventSplit[1][-1]][groupNum][0].tz_convert(pytz.utc).to_datetime64()).split('.')[0]+'Z'
					# 	endTime = str(scheduleInfo.subSeqGroupTimes[eventSplit[0]+eventSplit[1][-1]][groupNum][1].tz_convert(pytz.utc).to_datetime64()).split('.')[0]+'Z'
					# 	data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][groupNum-1]['startTime'] = startTime
					# 	data['schedule']['venues'][vid]['rooms'][rid]['activities'][aid]['childActivities'][groupNum-1]['endTime'] = endTime
				else:
					pass
		data['schedule']['venues'][vid]['rooms'][rid]['extensions'] = [{"id":"groupifier.RoomConfig","specUrl":"https://groupifier.jonatanklosko.com/wcif-extensions/RoomConfig.json","data":{"stations":scheduleInfo.amountStations}}]
	data['extensions'] = [{"id":"groupifier.CompetitionConfig",
	"specUrl":"https://groupifier.jonatanklosko.com/wcif-extensions/CompetitionConfig.json",
	"data":{"localNamesFirst":False,"scorecardsBackgroundUrl":"","competitorsSortingRule":"balanced",
	"noTasksForNewcomers":False,"tasksForOwnEventsOnly":True,
	"noRunningForForeigners":True,"printStations":False,
	"scorecardPaperSize":"a4"}}]

def enterPersonActivitiesWCIF(data,personInfo,scheduleInfo):
	assignmentTemplate = {"activityId":66,"stationNumber":None,"assignmentCode":"competitor"}
	for pid,person in enumerate(data['persons']):
		depth = 0
		if type(person['registration']) == dict:
			if person['registration']['status'] == 'accepted':
				for event in personInfo[person['name']].groups:
					data['persons'][pid]['assignments'].append(deepcopy(assignmentTemplate))
					data['persons'][pid]['assignments'][depth]['activityId'] = scheduleInfo.childActivityMapping[event][personInfo[person['name']].groups[event]]
					data['persons'][pid]['assignments'][depth]['stationNumber'] = personInfo[person['name']].stationNumbers[event]
					depth+=1

				for event in personInfo[person['name']].assignments:
					for assignment in personInfo[person['name']].assignments[event]:
						data['persons'][pid]['assignments'].append(deepcopy(assignmentTemplate))
						if type(assignment) == int:
							data['persons'][pid]['assignments'][depth]['activityId'] = scheduleInfo.childActivityMapping[event][assignment]
							# if scheduleInfo.maxAmountGroups > 3:
							# 	if len(scheduleInfo.groups[event]) > 3:
							# 		data['persons'][pid]['assignments'][depth]['assignmentCode'] = "staff-seatedJudge"
							# 		# Don't tell the judge where to sit by commenting the below line out
							# 		# data['persons'][pid]['assignments'][depth]['stationNumber'] = scheduleInfo.judgeStationOveriew[event][assignment][person['name']]
							# 	else:
							# 		data['persons'][pid]['assignments'][depth]['assignmentCode'] = "staff-runningJudge"
							# else:
							data['persons'][pid]['assignments'][depth]['assignmentCode'] = "staff-judge"
							# data['persons'][pid]['assignments'].append(deepcopy(assignmentTemplate))
							# depth+=1
							# data['persons'][pid]['assignments'][depth]['activityId'] = scheduleInfo.childActivityMapping[event][assignment]
							# data['persons'][pid]['assignments'][depth]['assignmentCode'] = "staff-runner"
						else:
							assignment = assignment[1:]
							if assignment[0] == 'S':
								assignment = int(assignment[1:])
								data['persons'][pid]['assignments'][depth]['activityId'] = scheduleInfo.childActivityMapping[event][assignment]
								data['persons'][pid]['assignments'][depth]['assignmentCode'] = "staff-scrambler"
							else: # should be runner
								assignment = int(assignment[1:])
								data['persons'][pid]['assignments'][depth]['activityId'] = scheduleInfo.childActivityMapping[event][assignment]
								data['persons'][pid]['assignments'][depth]['assignmentCode'] = "staff-runner"
						depth+=1

def genScorecards(scheduleInfo,target,stations,stages,differentColours):
	name = scheduleInfo.name
	if not os.path.isdir("WCA_Scorecards"):
		os.system('git clone https://github.com/Daniel-Anker-Hermansen/WCA_Scorecards.git')
	os.chdir("WCA_Scorecards")

	# get direct path from running 'whereis cargo'
	# os.system(f" /home/degdal/.cargo/bin/cargo run --release -- --r1 ../{target}/{name}stationNumbers{filenameSave}.csv  ../{target}/{name}timeLimits.csv  '{schedule.longName}'")
	if differentColours:
		perStage = int(stations/stages)
		# print(perStage)
		if stations%stages != 0:
			print("stages and stations is not properly divisible")
		if stages == 2:
			j = f"R-{perStage} G-{perStage}"
		elif stages == 3:
			j = f"R-{perStage} G-{perStage} B-{perStage}"
		else:
			print("number of stations in code not fitted to print this many colours. Easy fix in the code")
		os.system(f"target/release/wca_scorecards --r1 ../{target}/{name}stationNumbers.csv  ../{target}/{name}timeLimits.csv  '{scheduleInfo.longName}' --stages {j}")
	else:
		os.system(f"target/release/wca_scorecards --r1 ../{target}/{name}stationNumbers.csv  ../{target}/{name}timeLimits.csv  '{scheduleInfo.longName}'")
	
	filenameToMove = "".join(scheduleInfo.longName.split(' '))
	if differentColours:
		os.system(f'mv {filenameToMove}_scorecards.zip ../{target}/{filenameToMove}Scorecards.zip')
		# os.system(f"unzip ../{target}/{filenameToMove}Scorecards.zip")
	else:
		os.system(f'mv {filenameToMove}_scorecards.pdf ../{target}/{filenameToMove}Scorecards.pdf')

def callAll(id,stations,stages,differentColours,postToWCIF,mixed,fixed,customGroups,combined,just1GroupofBigBLD):
	path = f"../{id}"
	if not os.path.isdir(path):
		os.mkdir(path)
	response,header = getWcif(id)
	data = json.loads(response.content)

	target = path+'/outfiles'
	if not os.path.isdir(target):
		os.mkdir(target)

	people,organizers,delegates = competitorBasicInfo(data)

	schedule = scheduleBasicInfo(data,people,organizers,delegates,stations,fixed=fixed,customGroups= customGroups,combinedEvents=combined,just1GroupofBigBLD=just1GroupofBigBLD)

	schedule, people = splitIntoGroups(schedule,people,fixed=fixed)

	assignJudges(schedule,people,fixed,mixed=mixed)
	set_sblacklist = set()
	if os.path.exists('sblacklist.txt'):
		with open('sblacklist.txt') as f:
			for line in f:
				set_sblacklist.add(line.strip())

	reassignJudges(schedule,people,set_sblacklist,fixed,mixed=mixed)

	name = schedule.name
	convertCSV(schedule,people,f'{target}/{name}Groups.csv',combined=combined)
	getStationNumbers(schedule,people,combined,stages)
	makePDFOverview(schedule,f'{target}/{name}Overview.pdf')

	compCards(schedule,people,f'{target}/{name}compCards.pdf',mixed=mixed)
	getRegList(people,f'{target}/{name}CheckinList.pdf')
	
	CSVForScorecards(schedule,people,combined,f'{target}/{name}stationNumbers.csv')
	CSVForTimeLimits(schedule,people,combined,f'{target}/{name}timeLimits.csv')
	genScorecards(schedule,target,stations,stages,differentColours)
	if postToWCIF:
		confirm = input(f"{id}, Confirm you want to post with 1")
		updateScrambleCount(data,schedule)
		cleanChildActivityWCIF(data,schedule)
		cleanAssignmentsWCIF(data)
		createChildActivityWCIF(data,schedule)
		enterPersonActivitiesWCIF(data,people,schedule)
		if confirm == '1':
			postWcif(id,data,header)

def main():
	postToWCIF = TRUE # Should be False when playing
	# fil = open(f"{path}/wcif.json")
	id = 'OdsherredJulehygge2022'

	fixed = False # Bool, fixed judges 
	# fixed = True
	# mixed = {'333':True,'pyram':True} # Event -> Bool. True meaning seated judges and runners
	mixed = {}
	stations = 24
	# stages = None
	stages = 2 # Equally sized, should really be divisible by stations, otherwise some people will be placed on the same station
	differentColours = False # Only set this to true if the stages above is set to more than 1
	combined = None
	# combined = combineEvents('666','777')
	just1GroupofBigBLD = True
	# customGroups={'333bf':3,'sq1':4,'333mbf1':1}
	customGroups = {} # event -> number

	callAll(id,stations,stages,differentColours,postToWCIF,mixed,fixed,customGroups,combined,just1GroupofBigBLD)


main()
