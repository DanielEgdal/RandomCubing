import collections
import json
from datetime import datetime
from copy import deepcopy
from collections import defaultdict
import random
import math
import numpy as np
import pandas as pd
from typing import Dict, Generic, Iterator, List, Optional, TypeVar # For the priority queue
from fpdf import FPDF # For pdfs
import pytz # for timezones

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
		self.timezone = ''
		self.events = [] # list of lists. Inner lists have three values: Event name, s time, and e time of r1.
		self.eventWOTimes = []
		self.timelimits = {}
		self.eventTimes = {} # event -> touple of start and end time
		self.eventCompetitors = defaultdict(list)
		self.daySplit = [0] # the index where a day changes. Len = days-1
		self.groups = {} # event -> groupnum -> group
		self.stations = {}
		self.groupJudges = {} # event -> groupnum -> group. Made later
		self.groupRunners = {} # Will be event -> groupnum -> group. Made later
		self.groupScramblers = {} # Will be event -> groupnum -> group. Made later
		self.inVenue = defaultdict(set) # event -> set of people in venue
		self.unpred = set() # I didn't use this, but was planning on using it to account for some people not being present for all individual attempts for certain events. 
		self.overlappingEvents = defaultdict(list) # Event -> list of events happening during the timespan of it.
		self.groupTimes = {} # event -> groupnum -> time
		self.organizers = None # List of organizers and delegates
		self.delegates = None # List of delegates
		self.entire = []

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

	def orderForStations(self,personInfo): # For stations
		for event in self.eventCompetitors:
			for group in self.groups[event]:
				self.groups[event][group].sort(key=lambda x:personInfo[x].prs[event])

	def getIndividualGroupTimes(self):
		for event in self.groups:
			self.groupTimes[event] = {}
			amountOfGroups = len(self.groups[event])
			diff = self.eventTimes[event][1] - self.eventTimes[event][0]
			perGroup = diff/amountOfGroups
			for groupNum in self.groups[event]:
				self.groupTimes[event][groupNum] = (self.eventTimes[event][0]+ (perGroup*(groupNum-1)),self.eventTimes[event][0]+ (perGroup*(groupNum)))
				# self.groupTimes[event][groupNum] = ("tid 1", "tid 2")

	def getDaySplit(self):
		for i in range(1,len(self.events)):
			if self.events[i][1].day == self.events[i-1][1].day:
				pass
			else:
				self.daySplit.append(i)

	def eventTimeChecker(self, event1,event2):
		if (event1[2] > event2[1] and event1[2] < event2[2]) or (event1[1] > event2[1] and event1[1] < event2[2]) or (event1[2] > event2[2] and event1[1] < event2[2]) or (event1[1] < event2[1] and event2[2] < event1[2]):
			return True
		else:
			return False
	# if I weren't lazy this should be the same function
	def groupTimeChecker(self, event1,event2): # Group1 and group2
		if (event1[1] > event2[0] and event1[1] < event2[1]) or (event1[0] > event2[0] and event1[0] < event2[1]) or (event1[1] > event2[1] and event1[0] < event2[1]) or (event1[0] < event2[0] and event2[1] < event1[1]):
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
	delegates = set()
	for person in data['persons']:
		try:
			if person['registration']['status'] == 'accepted':
				competitor = Competitor(person["name"],person['registrantId'],person['countryIso2'],person['gender'],person['wcaId'])
				for val in person["roles"]: # getOrga
					if val in ('organizer','delegate','trainee-delegate'):
						competitor.orga = 3 # Setting this for sorting by speed
						organizers.add(person['name'])
					if val in ('delegate','trainee-delegate'):
						competitor.orga = 3 # Setting this for sorting by speed
						delegates.add(person['name'])
				competitor.age = year - int(person["birthdate"][:4]) #getAge
				competitor.dob = person["birthdate"]

				for eventData in person['personalBests']:
					if eventData['eventId'] not in ('333fm','444bf','333bf','555bf'):
						if eventData['type'] == 'average':
							competitor.prs[eventData['eventId']] = int(eventData['best'])
					else:
						if eventData['type'] == 'single':
							competitor.prs[eventData['eventId']] = int(eventData['best'])
				for event in person['registration']['eventIds']:
					competitor.events.add(event)
				comp_dict[person["name"]] = competitor
		except TypeError:
			pass
	return comp_dict,organizers, delegates

def scheduleBasicInfo(data,personInfo,organizers,delegates,stations,customGroups=[False], combinedEvents=None): # Custom groups is a dict, combined evnets is touple
	"""
	Get all the basic information for the schedule. 
	Doesn't store which stage events appear on, but will look into if events overlap (but not fully)
	"""
	
	if combinedEvents==None:
		combinedEvents = ('k','k')
	schedule = Schedule()
	schedule.name = data['id']
	already_there = set()
	timezone = pytz.timezone(data["schedule"]["venues"][0]["timezone"])
	tempFm = [] # not used for its purpose in the end
	tempMb = [] # not used for its purpose in the end
	for room in data["schedule"]["venues"][0]['rooms']:
		for val in room["activities"]:
			starttime = pd.Timestamp(val['startTime'][:-1]).tz_localize(pytz.utc).tz_convert(timezone)
			endtime = pd.Timestamp(val['endTime'][:-1]).tz_localize(pytz.utc).tz_convert(timezone)
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
							# print(tempCombined+roundnum)
					elif val['activityCode'][-1] in ['3','2','4']:
						tempCombined = val['activityCode'][:-3]
						roundnum = val['activityCode'][-1]
						schedule.entire.append([tempCombined+roundnum,starttime,endtime])
						# print(tempCombined+roundnum,'should be weird')
				else:
					if val['activityCode'][:4] == '333f' and val['activityCode'][-1] not in ['3','2','4']:
						tempFm.append([val['activityCode'][:-6],starttime,endtime])
						schedule.eventWOTimes.append('333fm')
						schedule.eventTimes[val['activityCode'][:-6]] = (starttime,endtime)
					elif val['activityCode'][:4] == '333m' and val['activityCode'][-1] not in ['3','2','4']:
						tempMb.append([val['activityCode'][:-6],starttime,endtime])
						schedule.eventWOTimes.append('333mbf')
						schedule.eventTimes[val['activityCode'][:-6]] = (starttime,endtime)
					schedule.entire.append([val['activityCode'][:-6]+val['activityCode'][-1],starttime,endtime])
			else:
				fs = f"{val['activityCode']}0"
				schedule.entire.append([fs,starttime,endtime])
	if len(tempMb) <2: # not used for its purpose in the end
		schedule.events += tempMb 
	else:
		schedule.unpred.add("333mbf")
	if len(tempFm) <2: # not used for its purpose in the end
		schedule.events += tempFm
	else:
		schedule.unpred.add("333fm")
	schedule.order() # Order the events by time in schedule
	schedule.getDaySplit() # See which events are each day
	for person in personInfo: # Counting the combined events as one
		already =False
		for event in personInfo[person].events:
			if event in [combinedEvents[0],combinedEvents[1]] and not already:
				schedule.eventCompetitors[combinedEvents[0]+'-'+combinedEvents[1]].append(person)
				already =True
			elif event not in [combinedEvents[0],combinedEvents[1]]: 
				schedule.eventCompetitors[event].append(person)
	schedule.organizers = organizers # Storing list of organizers and delegates
	schedule.delegates = delegates
	schedule.timezone = timezone
	schedule.order_entire()
	# print(schedule.entire)
	schedule.orderCompetitors(personInfo,combinedEvents[0]+'-'+combinedEvents[1]) # Ordering competitors by rank (used in group making and getting scramblers)
	schedule.identifyOverlap() # See which events overlap. Doesn't account full overlaps, i.e. for events with same start/ending time
	getGroupCount(schedule,True,stations,customGroups,just1=['333fm','333mbf','444bf','555bf']) # Getting the amount of groups needed
	schedule.getIndividualGroupTimes() # Seeing the start/end time of each group
	getAvailableDuring(personInfo,schedule,combinedEvents) # Identify during which events people should be present based on their registration

	for event in data['events']:
		schedule.timelimits[event['rounds'][0]['id'].split('-')[0]] = (event['rounds'][0]['timeLimit'],event['rounds'][0]['cutoff'])
		# print(event['rounds'][0]['id'],event['rounds'][0]['timeLimit'],event['rounds'][0]['cutoff'])
		# for round in event['rounds'][0]:
		# 	print(round)

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
			if event in scheduleInfo.eventWOTimes:
				scheduleInfo.groups[event] = {}
				scheduleInfo.groups[event][1] = []
	if fixedSeating:
		for event in scheduleInfo.eventCompetitors:
			if event not in just1 and event not in custom:
				scheduleInfo.groups[event] = {}
				for amount in range(1,math.ceil(len(scheduleInfo.eventCompetitors[event])/stationCount) +1):
					scheduleInfo.groups[event][amount] = []
	else:
		# stationCount *=1.15
		for event in scheduleInfo.eventCompetitors:
			if event not in just1:
				scheduleInfo.groups[event] = {}
				for amount in range(1,(np.max([math.floor(len(scheduleInfo.eventCompetitors[event])/stationCount) +1,3]))):
					scheduleInfo.groups[event][amount] = []
	
def splitNonOverlapGroups(scheduleInfo,personInfo,event,fixed=True):
	"""
	Function called for events which do not have something overlapping.
	In the regular assignments, sets aside scramblerCount scramblers for each group
	"""
	# dontSpeedScramble = ('333bf','444bf','555bf') # In these events, do not pick aside some fast people to scramble other groups.
	# if event in ('555','sq1'):
	# 	dontSpeedScramble = set()
	# else:
	# 	dontSpeedScramble = event
	dontSpeedScramble = ['333bf'] # for some reason very import to be list, otherwise reads substring
	groups = scheduleInfo.groups[event]
	totalComp = scheduleInfo.eventCompetitors[event]
	perGroup = len(totalComp)/len(groups)
	if fixed:
		scramblerCount = round(2/7*perGroup)
	else:
		scramblerCount = round(2/7*perGroup)
	p2 = deepcopy(totalComp)
	# special stuff when there are multiple delegates
	delegateCompetitors = [compDel for compDel in scheduleInfo.delegates if compDel in totalComp]
	if len(delegateCompetitors) > 1 and len(groups) > 1: # For orga
		delegateCompetitors.sort(key=lambda x:personInfo[x].prs[event], reverse=True)
		part1 = delegateCompetitors[:math.ceil(len(delegateCompetitors)/2)]
		part2 = delegateCompetitors[math.ceil(len(delegateCompetitors)/2):]
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

	# now for organizers
		orgaCompetitors = [compOrga for compOrga in scheduleInfo.organizers if compOrga in totalComp and compOrga not in scheduleInfo.delegates]
	else:
		orgaCompetitors = [compOrga for compOrga in scheduleInfo.organizers if compOrga in totalComp and compOrga]
	if len(orgaCompetitors) > 1 and len(groups) > 1:
		orgaCompetitors.sort(key=lambda x:personInfo[x].prs[event], reverse=True)
		part1 = orgaCompetitors[:math.ceil(len(orgaCompetitors)/2)]
		part2 = orgaCompetitors[math.ceil(len(orgaCompetitors)/2):]
		while len(part1) > 0: 
			comp = part1[0]
			part1 = part1[1:]
			groups[len(groups)-1].append(comp)
			personInfo[comp].groups[event] = len(groups)-1
			p2.remove(comp)
		while len(part2) > 0: 
			comp = part2[0]
			part2 = part2[1:]
			groups[len(groups)].append(comp)
			personInfo[comp].groups[event] = len(groups)
			p2.remove(comp)

	# Regular assigning now
	if event in dontSpeedScramble: # Don't take fast people aside for faster scrambling later
		
		for groupNum in range(1,len(groups)+1):
			while len(groups[groupNum]) < perGroup and len(p2) > 0: # Assigning slowest first
				comp = p2[-1]
				p2 = p2[:-1]
				groups[groupNum].append(comp)
				personInfo[comp].groups[event] = groupNum
		while len(p2) > 0: # If some people were somehow left out, add them in the last group
			comp = p2[-1]
			p2 = p2[:-1]
			groups[groupNum].append(comp)
			personInfo[comp].groups[event] = groupNum
	else:
		for groupNum in range(1,len(groups)+1):
			# offsetScramblers = 0
			for _ in range(1,scramblerCount+1): # taking best people, to ensure there are scramblers later (not all fast in same group)
				# comp = p2[offsetScramblers]
				comp = p2[0]
				p2 = p2[1:]
				groups[groupNum].append(comp)
				personInfo[comp].groups[event] = groupNum
				# offsetScramblers +=1
			while len(groups[groupNum]) < perGroup and len(p2) > 0: # Assigning slowest first
				comp = p2[-1]
				p2 = p2[:-1]
				groups[groupNum].append(comp)
				personInfo[comp].groups[event] = groupNum
		while len(p2) > 0: # If some people were somehow left out, add them in the last group
			comp = p2[-1]
			p2 = p2[:-1]
			groups[groupNum].append(comp)
			personInfo[comp].groups[event] = groupNum

def splitIntoOverlapGroups(scheduleInfo,personInfo,combination):
	"""
	Assigns groups for all overlapping events at the same time, and does assignments.
	As I could not find a proper deterministic manner of getting judges and competitors,
	I have set it to perform simulations. This should find the best combination.
	It will print out if there were some mistake.
	Failing to assign a person adds 100 to the fail score, a missing judge is 1.
	"""
	compByCount = [[] for _ in range(len(combination))]
	all = []
	for event in combination:
		for person in scheduleInfo.eventCompetitors[event]:
			all.append(person)
	for person in collections.Counter(all):
		compByCount[collections.Counter(all)[person]-1].append(person)

	bsh2 = deepcopy(scheduleInfo)
	bpes2 = deepcopy(personInfo)
	few_fails = 100 # Default
	for ii in range(100): #100 simulations
		random.shuffle(combination)
		if few_fails > 0:
			sh2 = deepcopy(scheduleInfo)
			pes2 = deepcopy(personInfo)
			for val in compByCount:
				random.shuffle(val)
			random.shuffle(compByCount)
			j = len(compByCount) -1
			fails = 0
			while j >= 0:
				p2 = deepcopy(compByCount[j])
				while p2:
					for event in combination:
						assigned = False
						if p2[0] in sh2.eventCompetitors[event]:
							groups = sh2.groups[event]
							totalComp = sh2.eventCompetitors[event]
							perGroup = len(totalComp)/len(groups)
							groupNumList = [j for j in range(len(groups))]
							random.shuffle(groupNumList)
							for idy in groupNumList:
								if not assigned:
									if len(groups[idy+1]) < perGroup: # Making sure there is space in the group
										checkLegal = True
										for event2 in pes2[p2[0]].groups:
											if event2 in combination:
												if not sh2.groupTimeChecker(sh2.groupTimes[event][idy+1],sh2.groupTimes[event2][pes2[p2[0]].groups[event2]]):
													pass # Check that they don't have an overlapping event
												else:
													checkLegal = False
										if checkLegal:
											sh2.groups[event][idy+1].append(p2[0])
											pes2[p2[0]].groups[event] = idy+1
											assigned = True
							if not assigned:
								# print(f"failed {p2[0]} for {event}")
								fails +=1
					p2 = p2[1:]
				j -=1
			missing = judgePQOverlap(combination,sh2,pes2) # Perform assignment of staff
			score = fails*100 + missing
			if score < few_fails: # If there is fewer missing staff
				few_fails = score
				bsh2 = deepcopy(sh2)
				bpes2 = deepcopy(pes2)

	scheduleInfo = deepcopy(bsh2)
	personInfo = deepcopy(bpes2)

	if few_fails > 0:
		print(f"A total fail score for the overlapping events ({combination}) of {few_fails}")
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
				combination = list(combination) # For the sake of simulations
				scheduleInfo, personInfo = splitIntoOverlapGroups(scheduleInfo, personInfo, combination) # For some reason it does not update the variables
				combination = set(combination)
				already = already.union(combination) # Don't repeat the same combo of overlaps

	return scheduleInfo, personInfo # For some reason it does not update the variables

def judgePQNonOverlap(event,scheduleInfo,personInfo,fixedSeating=True): ## Needs fixing. Assigns judge multiple times in same event
	if fixedSeating:
		scheduleInfo.groupJudges[event] = {}
		groups = scheduleInfo.groups[event]
		competitors = scheduleInfo.eventCompetitors[event]
		maybePeople = scheduleInfo.inVenue[event]
		atleast1 = set() # Make sure everyone judges at least once before giving two assignments to other people
		for groupNum in groups:
			pq = MaxPQ()
			scheduleInfo.groupJudges[event][groupNum] = []
			if event!= '333bf':
				needed = len(scheduleInfo.groups[event][groupNum]) + np.min([round(2/7*(len(scheduleInfo.groups[event][groupNum]))) +1,6])
			else:
				needed = len(scheduleInfo.groups[event][groupNum]) + np.min([round(2/7*(len(scheduleInfo.groups[event][groupNum]))) +1,4])
			used = set() # those that were already tried
			for comp in competitors: # First, get only the people who haven't judged in the event
				if comp not in scheduleInfo.organizers:
					if comp not in scheduleInfo.groups[event][groupNum]:
						if comp not in atleast1:
							pq.insert([comp,math.log((len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
			while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed:
					judge = pq.del_max()[0]
					personInfo[judge].totalAssignments +=1
					personInfo[judge].assignments[event].append(groupNum)
					scheduleInfo.groupJudges[event][groupNum].append(judge)
					atleast1.add(judge) 
					used.add(judge)
			
			if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
				for comp in competitors: # second try competitors in the event
					if comp not in used and comp not in scheduleInfo.organizers:
						if comp not in scheduleInfo.groups[event][groupNum]:
							pq.insert([comp,math.log((len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
				while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed:
					judge = pq.del_max()[0]
					personInfo[judge].totalAssignments +=1
					personInfo[judge].assignments[event].append(groupNum)
					scheduleInfo.groupJudges[event][groupNum].append(judge)
					atleast1.add(judge) 
					used.add(judge)
			
			if len(scheduleInfo.groupJudges[event][groupNum]) < needed: # If more people are needed, try all in the venue
				for comp in maybePeople:
					if comp not in used and not comp in scheduleInfo.groups[event][groupNum]:
						if comp in scheduleInfo.organizers:
							pq.insert([comp,0])
						else:
							pq.insert([comp,(math.log(len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
				while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed: # Refactor later for scramblers and judges
					judge = pq.del_max()[0]
					personInfo[judge].totalAssignments +=1
					personInfo[judge].assignments[event].append(groupNum)
					scheduleInfo.groupJudges[event][groupNum].append(judge)
				if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
					print(f"Not possible for {event} group {groupNum}. Got {len(scheduleInfo.groupJudges[event][groupNum])} of {needed}")
	else:
		scheduleInfo.groupJudges[event] = {}
		groups = scheduleInfo.groups[event]
		for group in groups:
			scheduleInfo.groupJudges[event][group] = []
		competitors = scheduleInfo.eventCompetitors[event]
		maybePeople = scheduleInfo.inVenue[event]
		atleast1 = set() # Make sure everyone judges at least once before giving two assignments to other people
		if event not in ('555'):
			for competitor in competitors:
				group_to_place = ((personInfo[competitor].groups[event]-2)%len(groups)) +1

				scheduleInfo.groupJudges[event][group_to_place].append(competitor)
				personInfo[competitor].totalAssignments +=1
				personInfo[competitor].assignments[event].append(group_to_place)
		else:
			for groupNum in groups:
				pq = MaxPQ()
				# scheduleInfo.groupJudges[event][groupNum] = []
				# if event!= '333bf':
					# needed = len(scheduleInfo.groups[event][groupNum]) + np.min([round(1/7*(len(scheduleInfo.groups[event][groupNum]))) +1,6])
				# else:
				needed = len(scheduleInfo.groups[event][groupNum]) + min(round(2/7*(len(scheduleInfo.groups[event][groupNum]))) +1,4)
				# needed = len(scheduleInfo.groups[event][groupNum]) + min(round(1/7*(len(scheduleInfo.groups[event][groupNum]))) +1,4)
				# needed = min(needed,len(competitors)/len(groups) - min(round(1/7*(len(scheduleInfo.groups[event][groupNum]))) +1,4))
				used = set() # those that were already tried

				for comp in competitors: # First, get only the people who haven't judged in the event
					if comp not in scheduleInfo.organizers:
						if comp not in scheduleInfo.groups[event][groupNum]:
							if comp not in atleast1:
								pq.insert([comp,math.log((len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
				while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed:
						judge = pq.del_max()[0]
						personInfo[judge].totalAssignments +=1
						personInfo[judge].assignments[event].append(groupNum)
						scheduleInfo.groupJudges[event][groupNum].append(judge)
						atleast1.add(judge) 
						used.add(judge)
				
				if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
					for comp in competitors: # second try competitors in the event
						if comp not in used and comp not in scheduleInfo.organizers:
							if comp not in scheduleInfo.groups[event][groupNum]:
								pq.insert([comp,math.log((len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
					while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed:
						judge = pq.del_max()[0]
						personInfo[judge].totalAssignments +=1
						personInfo[judge].assignments[event].append(groupNum)
						scheduleInfo.groupJudges[event][groupNum].append(judge)
						atleast1.add(judge) 
						used.add(judge)
				
				if len(scheduleInfo.groupJudges[event][groupNum]) < needed: # If more people are needed, try all in the venue
					for comp in maybePeople:
						if comp not in used and not comp in scheduleInfo.groups[event][groupNum]:
							if comp in scheduleInfo.organizers:
								pq.insert([comp,0])
							else:
								pq.insert([comp,(math.log(len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
					while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed: # Refactor later for scramblers and judges
						judge = pq.del_max()[0]
						personInfo[judge].totalAssignments +=1
						personInfo[judge].assignments[event].append(groupNum)
						scheduleInfo.groupJudges[event][groupNum].append(judge)
					if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
						print(f"Not possible for {event} group {groupNum}. Got {len(scheduleInfo.groupJudges[event][groupNum])} of {needed}")

def judgePQOverlap(combination,scheduleInfo,personInfo,fixedSeating=True): ## Needs fixing. Assigns judge multiple times in same event
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
					if comp not in scheduleInfo.organizers:
						used.add(comp)
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
								pq.insert([comp,(math.log(len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
				while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed: # Refactor later for scramblers and judges
					judge = pq.del_max()[0]
					personInfo[judge].totalAssignments +=1
					personInfo[judge].assignments[event].append(groupNum)
					scheduleInfo.groupJudges[event][groupNum].append(judge)
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
								if comp in scheduleInfo.organizers:
									pq.insert([comp,0])
								else:
									pq.insert([comp,(math.log(len(personInfo[comp].events)))/personInfo[comp].totalAssignments])
					while not pq.is_empty() and len(scheduleInfo.groupJudges[event][groupNum]) < needed: # Refactor later for scramblers and judges
						judge = pq.del_max()[0]
						personInfo[judge].totalAssignments +=1
						personInfo[judge].assignments[event].append(groupNum)
						scheduleInfo.groupJudges[event][groupNum].append(judge)
					if len(scheduleInfo.groupJudges[event][groupNum]) < needed:
						missing += needed-len(scheduleInfo.groupJudges[event][groupNum])
						# print(f"Not possible for {event} group {groupNum}. Got {len(scheduleInfo.groupJudges[event][groupNum])} of {needed}")
		return missing

def assignJudges(scheduleInfo,personInfo,fixedSeating= True,dontAssign=True):
	if dontAssign: # Don't assign judges when there is only one group
		for event in scheduleInfo.events:
			if len(scheduleInfo.groups[event[0]]) > 1:
				if event[0] not in scheduleInfo.overlappingEvents:
					judgePQNonOverlap(event[0],scheduleInfo,personInfo,fixedSeating)
	else:
		for event in scheduleInfo.events:
			if event[0] not in scheduleInfo.overlappingEvents:
				judgePQNonOverlap(event[0],scheduleInfo,personInfo,fixedSeating)

def reassignJudges(scheduleInfo,personInfo,blacklist = {None},fixed=True):
	if fixed:
		for event in scheduleInfo.groups:
			scheduleInfo.groupScramblers[event] = {}
			scheduleInfo.groupRunners[event] = {}
			for group in scheduleInfo.groups[event]:
				scheduleInfo.groupScramblers[event][group] = []
				scheduleInfo.groupRunners[event][group] = []
				if event in scheduleInfo.groupJudges:
					if len(scheduleInfo.groupJudges[event][group]) > 0: # If judges are assigned for the event
						# Always at least one scrambler
						passed = False
						scheduleInfo.groupJudges[event][group].sort(key=lambda x:personInfo[x].prs[event]*personInfo[x].orga)
						for potScram in scheduleInfo.groupJudges[event][group]: # Take fastest first
							if personInfo[potScram].age > 14 and potScram not in blacklist: # Arguably can be set lower/higher for min
								passed = True
								break
						if not passed:
							potScram = scheduleInfo.groupJudges[event][group][0] # Take the fastest if no one is old enough
						scheduleInfo.groupJudges[event][group].remove(potScram)
						scheduleInfo.groupScramblers[event][group].append(potScram)
						for idx,assignment in enumerate(personInfo[potScram].assignments[event]):
							if assignment == group:
								personInfo[potScram].assignments[event][idx] = f';S{group}'
						
						runSc = 1 # If divisible by 2 make scrambler, otherwise runner
						# Alternate runner/scrambler. Only continue if there is enough judges available
						while len(scheduleInfo.groups[event][group])< len(scheduleInfo.groupJudges[event][group]):
							if runSc%2 == 0:
								# scrmbler stuff
								passed = False
								for potScram in scheduleInfo.groupJudges[event][group]: # Take fastest first
									if personInfo[potScram].age > 14 and potScram not in blacklist: # Arguably can be set lower/higher for min
										passed = True
										break
								if not passed:
									potScram = scheduleInfo.groupJudges[event][group][0] # Take the fastest if no one is old enough
								scheduleInfo.groupJudges[event][group].remove(potScram)
								scheduleInfo.groupScramblers[event][group].append(potScram)
								for idx,assignment in enumerate(personInfo[potScram].assignments[event]):
									if assignment == group:
										personInfo[potScram].assignments[event][idx] = f';S{group}'
							else: # Runners
								passed = False
								for potRun in scheduleInfo.groupJudges[event][group][::-1]: # Take slowest first
									if personInfo[potRun].age > 14 and personInfo[potRun].age < 40 and potRun not in blacklist: # Arguably can be set to lower/higher for min/max
										passed = True
										break
								if not passed:
									potRun = scheduleInfo.groupJudges[event][group][-1]
								scheduleInfo.groupJudges[event][group].remove(potRun)
								scheduleInfo.groupRunners[event][group].append(potRun)
								for idx,assignment in enumerate(personInfo[potRun].assignments[event]):
									if assignment == group:
										personInfo[potRun].assignments[event][idx] = f';R{group}'
							runSc += 1
	else:
		for event in scheduleInfo.groups:
			scheduleInfo.groupScramblers[event] = {}
			scheduleInfo.groupRunners[event] = {}
			for group in scheduleInfo.groups[event]:
				scheduleInfo.groupScramblers[event][group] = []
				scheduleInfo.groupRunners[event][group] = []
				if event in scheduleInfo.groupJudges:
					if len(scheduleInfo.groupJudges[event][group]) > 0: # If judges are assigned for the event
						# Always at least one scrambler
						passed = False
						scheduleInfo.groupJudges[event][group].sort(key=lambda x:personInfo[x].prs[event]*personInfo[x].orga)
						for potScram in scheduleInfo.groupJudges[event][group]: # Take fastest first
							if personInfo[potScram].age > 14 and potScram not in blacklist: # Arguably can be set lower/higher for min
								passed = True
								break
						if not passed:
							potScram = scheduleInfo.groupJudges[event][group][0] # Take the fastest if no one is old enough
						scheduleInfo.groupJudges[event][group].remove(potScram)
						scheduleInfo.groupScramblers[event][group].append(potScram)
						for idx,assignment in enumerate(personInfo[potScram].assignments[event]):
							if assignment == group:
								personInfo[potScram].assignments[event][idx] = f';S{group}'
						
						# Just scramblers, continue until you have enough
						am_scramblers = 4
						if event == 'sq1':
							am_scramblers = 2
						elif event == '333bf':
							am_scramblers = 0
						while am_scramblers> len(scheduleInfo.groupScramblers[event][group]):
							# scrmbler stuff
							passed = False
							for potScram in scheduleInfo.groupJudges[event][group]: # Take fastest first
								if personInfo[potScram].age > 14 and potScram not in blacklist: # Arguably can be set lower/higher for min
									passed = True
									break
							if not passed:
								potScram = scheduleInfo.groupJudges[event][group][0] # Take the fastest if no one is old enough
							scheduleInfo.groupJudges[event][group].remove(potScram)
							scheduleInfo.groupScramblers[event][group].append(potScram)
							for idx,assignment in enumerate(personInfo[potScram].assignments[event]):
								if assignment == group:
									personInfo[potScram].assignments[event][idx] = f';S{group}'

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

def makePDFOverview(scheduleInfo,outfile):
	pdf = FPDF('p','mm', 'A4')

	pdf.add_page()

	pdf.set_auto_page_break(auto=True,margin=15)
	# See main for fonts. Needed because of utf-8 stuff and names
	pdf.add_font('DejaVu','', fname='fonts/DejaVuSansCondensed.ttf', uni=True) 
	pdf.add_font('DejaVub','', fname='fonts/DejaVuSansCondensed-Bold.ttf', uni=True)

	pdf.set_font('DejaVub','',22)
	pdf.cell(65,9,f'{scheduleInfo.name} Group Overview',ln=True)
	# for event1 in scheduleInfo.events:
	# 	event = event1[0]
	for activity in scheduleInfo.entire:
		if activity[0][-1] == '1':
			event = activity[0][:-1]
			for group in scheduleInfo.groups[event]:
				# print(event,group)
				pdf.set_font('DejaVub','',20)
				pdf.cell(65,9,f'{event} {group}',ln=True) # Event and group
				pdf.set_font('DejaVu','',14)
				# Time duration
				pdf.cell(65,9,f'{scheduleInfo.groupTimes[event][group][0].time()}-{scheduleInfo.groupTimes[event][group][1].time()}',ln=True)
				pdf.set_font('DejaVub','',12)
				pdf.cell(45,9,'Competitors')
				pdf.cell(45,9,'Judges')
				pdf.cell(45,9,'Scramblers')
				pdf.cell(45,9,'Runners',ln=True)
				# print(scheduleInfo.groups[event][group])
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
				# print(competitors)
				if len(judges) > 0 and len(judges) < len(competitors): # Warning of few staff
					pdf.cell(45,9,f'# {len(competitors)}')
					pdf.set_text_color(194,8,8) # Highlight red
					pdf.cell(45,9,f'{len(judges)}/{len(competitors)}')
					pdf.cell(45,9,f'{len(scramblers)}')
					pdf.cell(45,9,f'{len(runners)}',ln=True)
					pdf.set_text_color(0,0,0) # Back to black
				elif len(judges) == len(competitors) and len(scramblers) <=1: # Warning of few runners/scramblers
					pdf.cell(45,9,f'# {len(competitors)}')
					pdf.cell(45,9,f'{len(judges)}/{len(competitors)}')
					pdf.set_text_color(194,8,8)
					pdf.cell(45,9,f'{len(scramblers)}')
					pdf.cell(45,9,f'{len(runners)}',ln=True)
					pdf.set_text_color(0,0,0)
				elif len(judges) == len(competitors) and len(runners) <=1: # warning of few runners
					pdf.cell(45,9,f'# {len(competitors)}')
					pdf.cell(45,9,f'{len(judges)}/{len(competitors)}')
					pdf.cell(45,9,f'{len(scramblers)}')
					pdf.set_text_color(194,8,8)
					pdf.cell(45,9,f'{len(runners)}',ln=True)
					pdf.set_text_color(0,0,0)
				else: # All good
					pdf.cell(45,9,f'# {len(competitors)}')
					pdf.set_font('DejaVu','',12)
					pdf.cell(45,9,f'{len(judges)}/{len(competitors)}')
					pdf.cell(45,9,f'{len(scramblers)}')
					pdf.cell(45,9,f'{len(runners)}',ln=True)
				while i < len(competitors) or i < len(judges): # Print everyone
					# print(i)
					pdf.set_font('DejaVu','',8)
					if len(competitors) > i and len(judges) > i and len(scramblers) > i and len(runners) > i: # Enough for now
						pdf.cell(45,9,f'{competitors[i]}, {scheduleInfo.stations[event][group][competitors[i]]}') # HHHHH
						pdf.cell(45,9,f'{judges[i]}')
						pdf.cell(45,9,f'{scramblers[i]}')
						pdf.cell(45,9,f'{runners[i]}',ln=True)
					elif len(judges) > i and len(scramblers) > i: # Enough judges and scramblers for now
						pdf.cell(45,9,f'{competitors[i]}, {scheduleInfo.stations[event][group][competitors[i]]}')
						pdf.cell(45,9,f'{judges[i]}')
						pdf.cell(45,9,f'{scramblers[i]}',ln=True)
					elif len(competitors) > i and len(judges) > i: # Enough judges and competitors for now
						pdf.cell(45,9,f'{competitors[i]}, {scheduleInfo.stations[event][group][competitors[i]]}')
						pdf.cell(45,9,f'{judges[i]}',ln=True)
					elif len(judges) > i: # only used in case there is 'bonus judge'
						pdf.cell(45,9,f'-')
						pdf.cell(45,9,f'{judges[i]}',ln=True)
					else: # Only competitors left
						pdf.cell(45,9,f'{competitors[i]}, {scheduleInfo.stations[event][group][competitors[i]]}',ln=True)
					i+=1
		else:
			pdf.set_font('DejaVub','',20)
			pdf.cell(65,9,f'Round {activity[0][-1]} of {activity[0][:-1]}',ln=True) # Event and group
			pdf.set_font('DejaVu','',14)
			# Time duration
			pdf.cell(65,9,f'{activity[1].time()}-{activity[2].time()}',ln=True)
				
				
	pdf.output(outfile)

def writeNames(personlist,progress,ln,pdf):
	pdf.cell(65,9,f'{personlist[progress].name}, ID: {personlist[progress].id}',ln=ln)

def eventPatch(personInfo,personlist,progress,event,ln,pdf):
	translate = {'333':'3x3','222':'2x2','444':'4x4','555':'5x5','666':'6x6','777':'7x7',
	'333oh':'3x3 OH','333fm':'333fm','333mbf':'Multi','333bf':'3BLD','minx':'Megaminx','pyram':'Pyraminx',
	'skewb':'Skewb','clock':'Clock','555bf':'5BLD','444bf':'4BLD','sq1':'Square-1'}
	line_height = pdf.font_size *2
	col_width = pdf.epw / 10
	
	pdf.multi_cell(col_width,line_height,translate[event],border=1, ln=3)

	if event in personInfo[personlist[progress].name].groups:
		pdf.multi_cell(25,line_height,f"Grp. {str(personInfo[personlist[progress].name].groups[event])}, Bord {personInfo[personlist[progress].name].stationNumbers[event]}",border=1, ln=3)
	else:
		pdf.multi_cell(25,line_height,' ',border=1, ln=3)
	# pdf.multi_cell(col_width,line_height,str(personInfo[personlist[progress].name].groups[event]),border=1, ln=3)

	strlist = [str(val) if len(str(val)) ==1 else val[1:] for val in personInfo[personlist[progress].name].assignments[event]]
	sttr = ','.join(strlist)
	pdf.multi_cell(col_width,line_height,sttr,border=1, ln=3)
	pdf.multi_cell(2,line_height,'',border=0, ln=3)
	if ln:
		pdf.ln(line_height)

def compCards(scheduleInfo,personInfo):
	pdf = FPDF()
	pdf.add_page()
	pdf.add_font('DejaVu','', fname='fonts/DejaVuSansCondensed.ttf', uni=True)
	pdf.set_font('DejaVu','',8)
	# personInfo.sort(key=lambda x:x['name'])
	personlist = [val for val in personInfo.values()]
	personlist.sort(key=lambda x:x.name)
	progress = 0
	event_list = []
	for event in scheduleInfo.eventWOTimes:
		sevent = event.split('-')
		for event_ in sevent:
			event_list.append(event_)
	while progress < len(personlist):
		
		if progress+2 < len(personlist):
			writeNames(personlist,progress,False,pdf)
			writeNames(personlist,progress+1,False,pdf)
			writeNames(personlist,progress+2,True,pdf)
			for event in event_list:
				eventPatch(personInfo,personlist,progress,event,False,pdf)
				eventPatch(personInfo,personlist,progress+1,event,False,pdf)
				eventPatch(personInfo,personlist,progress+2,event,True,pdf)

		elif progress+1 < len(personlist):
			writeNames(personlist,progress,False,pdf)
			writeNames(personlist,progress+1,True,pdf)
			for event in event_list:
				eventPatch(personInfo,personlist,progress,event,False,pdf)
				eventPatch(personInfo,personlist,progress+1,event,True,pdf)
		else:
			writeNames(personlist,progress,True,pdf)
			for event in event_list:
				eventPatch(personInfo,personlist,progress,event,True,pdf)
		progress +=3
	# for idx,person in enumerate(personlist):
	# 	print(person.name)
	# 	if (idx+1)%split == 0:
	# 		pdf.ln(line_height)
	
	# for idx,person in enumerate(personInfo):
	# 	pdf.cell(45,9,f'{person.name}, {person.id}')
	# 	pdf.multi_cell(col_width,line_height,person,border=1, ln=3)
	# 	if (idx+1)%split == 0:
	# 		pdf.ln(line_height)
			# personInfo[person].groups[event]
	pdf.output('tabletry.pdf')

def getRegList(personInfo):
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
	pdf.output('checkinlist.pdf')

def getStationNumbers(scheduleInfo,personInfo,combined):
	for event in scheduleInfo.eventWOTimes:
		scheduleInfo.stations[event] = {}
		for groupNum in scheduleInfo.groups[event]:
			scheduleInfo.stations[event][groupNum] = {}
			for idx,person in enumerate(scheduleInfo.groups[event][groupNum]):
				personInfo[person].stationNumbers[event] = idx+1
				scheduleInfo.stations[event][groupNum][person] = idx+1

	if combined: # Fix the assignment back to regular events
		combHy = combined[0]+'-'+combined[1]
		for person in personInfo:
			for comSplit in combined:
				if comSplit in personInfo[person].events:
					personInfo[person].stationNumbers[comSplit] = deepcopy(personInfo[person].stationNumbers[combHy])
			if combHy in personInfo[person].stationNumbers:
				personInfo[person].stationNumbers.pop(combHy)

def CSVForScorecards(scheduleInfo,personInfo,combined,outfile):
	header = 'Name'
	combHy = combined[0]+'-'+combined[1]
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
				pString+=f"{personInfo[person].groups[event]};{personInfo[person].stationNumbers[event]}"
			pString+=','
		pString = pString[:-1]
		header+=pString+'\n'
	writeCSVf = open(outfile,'w')
	print(header,file=writeCSVf)

def CSVForTimeLimits(scheduleInfo,personInfo,combined,outfile):
	header = ''
	combHy = combined[0]+'-'+combined[1]
	for event in scheduleInfo.events:
		if combined:
			if event[0] == combHy:
				for event in event[0].split('-'):
					header+=f',{event}'
			else:
				header+=f',{event[0]}'
		else:
			header+=f',{event[0]}'
	header = header[1:]
	hCSV = header.split(',')

	header+='\n'
	for event in hCSV:
		# print('w,',event)
		t, c = scheduleInfo.timelimits[event]
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
	header = header[:-1]
	print(header)
	writeCSVf = open(outfile,'w')
	print(header,file=writeCSVf)

def main():
	# Download the file from here (Replace the comp id): https://www.worldcubeassociation.org/api/v0/competitions/VestkystCubing2021/wcif
	# Fonts needed because of utf-8. Document: https://pyfpdf.github.io/fpdf2/Unicode.html. Direct link: https://github.com/reingart/pyfpdf/releases/download/binary/fpdf_unicode_font_pack.zip
	# Make a folder with the ones used in the file.
	fil = open("../odsherred/wcif.json")
	# fil = open("../dåstrup/wcif.json")
	
	fixed = False # Bool 
	stations = 20
	combined = None
	combined = combineEvents('666','777')
	data = json.load(fil)
	
	people,organizers,delegates = competitorBasicInfo(data)
	
	# schedule = scheduleBasicInfo(data,people,organizers,stations,{'333bf':3},combined)
	schedule = scheduleBasicInfo(data,people,organizers,delegates,stations,{'333bf':2},combinedEvents=combined)

	# schedule = scheduleBasicInfo(data,people,organizers,stations,combinedEvents=combined)
	schedule, people = splitIntoGroups(schedule,people,fixed=fixed)

	assignJudges(schedule,people,fixed)
	
	sblacklist = open('sblacklist.txt').readlines()
	set_sblacklist = set()
	for i in sblacklist:
		set_sblacklist.add(i.strip('\n'))

	reassignJudges(schedule,people,set_sblacklist,fixed)

	filenameSave = str(datetime.now().strftime("%m%d_%T")).replace(':','').replace('/','') # Ensure unique name

	name = schedule.name
	convertCSV(schedule,people,f'out/{name}Groups{filenameSave}.csv',combined=combined)
	getStationNumbers(schedule,people,combined)
	makePDFOverview(schedule,f'out/{name}Overview{filenameSave}.pdf')

	compCards(schedule,people)
	getRegList(people)
	
	CSVForScorecards(schedule,people,combined,f'out/{name}stationNumbers{filenameSave}.csv')
	CSVForTimeLimits(schedule,people,combined,f'out/{name}timeLimits.csv')
	# makePDFCards(schedule,people,f'out/{name}Cards{filenameSave}.pdf') # not made


main()

# checking overlaps
#print(schedule.overlappingEvents)
# for event in schedule.overlappingEvents:
#     for group in schedule.groups[event]:
#         for event2 in schedule.overlappingEvents:
#             for group2 in schedule.groups[event2]:
#                 g = schedule.groupTimes[event][group]
#                 h = schedule.groupTimes[event2][group2]
#                 print(event,group,event2,group2,schedule.groupTimeChecker(g,h))










