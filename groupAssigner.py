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
    def __init__(self,name):
        self.name = name
        self.events = set()
        self.prs = defaultdict(basicPr)
        self.availableDuring = set() # a set of events where they will be in the venue
        self.orga = 1 # for calculation. Actual orga get 3, for the time being 
        self.groups = {} # Event -> groupnum
        self.assignments = defaultdict(list)
        self.age = 0
        self.totalAssignments = 1 # so addition works

    def __str__(self):
        return self.name + " + info"

class Schedule():
    def __init__(self):
        self.name = ''
        self.events = [] # list of lists. Inner lists have three values: Event name, s time, and e time of r1.
        self.eventWOTimes = []
        self.eventTimes = {} # event -> touple of start and end time
        self.eventCompetitors = defaultdict(list)
        self.daySplit = [0] # the index where a day changes. Len = days-1
        self.groups = {} # event -> groupnum -> group
        self.groupJudges = {} # event -> groupnum -> group. Made later
        self.groupRunners = {} # Will be event -> groupnum -> group. Made later
        self.groupScramblers = {} # Will be event -> groupnum -> group. Made later
        self.inVenue = defaultdict(set) # event -> set of people in venue
        self.unpred = set() # I didn't use this, but was planning on using it to account for some people not being present for all individual attempts for certain events. 
        self.overlappingEvents = defaultdict(list) # Event -> list of events happening during the timespan of it.
        self.groupTimes = {} # event -> groupnum -> time
        self.organizers = None # List of organizers and delegates

    def order(self): # ordering events in schedule
        self.events.sort(key=lambda x:x[1]) 

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
                self.groupTimes[event][groupNum] = (self.eventTimes[event][0]+ (perGroup*(groupNum-1)),self.eventTimes[event][0]+ (perGroup*(groupNum)))
                # self.groupTimes[event][groupNum] = ("tid 1", "tid 2")

    def getDaySplit(self):
        """
        There will be an error for some time zones, see use case
        """

        for i in range(1,len(self.events)):
            if self.events[i][1][:10] == self.events[i-1][1][:10]:
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
    for person in data['persons']:
        try:
            if person['registration']['status'] == 'accepted':
                competitor = Competitor(person["name"])
                for val in person["roles"]: # getOrga
                    if val in ('delegate','organizer'):
                        competitor.orga = 3 # Setting this for sorting by speed
                        organizers.add(person['name'])
                competitor.age = year - int(person["birthdate"][:4]) #getAge

                for eventData in person['personalBests']:
                    if eventData['eventId'] not in ('333fm','444bf','333bf','555bf'):
                        if eventData['type'] == 'average':
                            competitor.prs[eventData['eventId']] = int(eventData['worldRanking'])
                    else:
                        if eventData['type'] == 'single':
                            competitor.prs[eventData['eventId']] = int(eventData['worldRanking'])
                for event in person['registration']['eventIds']:
                    competitor.events.add(event)
                comp_dict[person["name"]] = competitor
        except TypeError:
            pass
    return comp_dict,organizers

def scheduleBasicInfo(data,personInfo,organizers,stations,customGroups=[False], combinedEvents=None): # Custom groups is a dict, combined evnets is touple
    """
    Get all the basic information for the schedule. 
    Doesn't store which stage events appear on, but will look into if events overlap (but not fully)
    """
    
    if combinedEvents==None:
        combinedEvents = ('k','k')
    schedule = Schedule()
    schedule.name = data['id']
    already_there = set()
    tempFm = [] # not used for its purpose in the end
    tempMb = [] # not used for its purpose in the end
    for room in data["schedule"]["venues"][0]['rooms']:
        for val in room["activities"]:
            if val['activityCode'][0] != 'o':
                if len(val['activityCode']) < 9:
                    if val['activityCode'][-1] not in ['3','2','4'] and val['activityCode'][:-3] not in already_there:
                        tempCombined = val['activityCode'][:-3]
                        doo = True
                        if tempCombined == combinedEvents[0]:
                            tempCombined += '-'+combinedEvents[1]
                        elif tempCombined == combinedEvents[1]:
                            doo = False
                        if doo:
                            schedule.events.append([tempCombined,val['startTime'],val['endTime']])
                            schedule.eventWOTimes.append(tempCombined)
                            already_there.add(val['activityCode'][:-3])
                            schedule.eventTimes[tempCombined] = (pd.Timestamp(val['startTime'][:-1]),pd.Timestamp(val['endTime'][:-1]))
                else:
                    if val['activityCode'][:4] == '333f' and val['activityCode'][-1] not in ['3','2','4']:
                        tempFm.append([val['activityCode'][:-6],val['startTime'],val['endTime']])
                        schedule.eventWOTimes.append('333fm')
                        schedule.eventTimes[val['activityCode'][:-6]] = (pd.Timestamp(val['startTime'][:-1]),pd.Timestamp(val['endTime'][:-1]))
                    elif val['activityCode'][:4] == '333m' and val['activityCode'][-1] not in ['3','2','4']:
                        tempMb.append([val['activityCode'][:-6],val['startTime'],val['endTime']])
                        schedule.eventWOTimes.append('333mbf')
                        schedule.eventTimes[val['activityCode'][:-6]] = (pd.Timestamp(val['startTime'][:-1]),pd.Timestamp(val['endTime'][:-1]))
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
    schedule.orderCompetitors(personInfo,combinedEvents[0]+'-'+combinedEvents[1]) # Ordering competitors by rank (used in group making and getting scramblers)
    schedule.identifyOverlap() # See which events overlap. Doesn't account full overlaps, i.e. for events with same start/ending time
    getGroupCount(schedule,True,stations,customGroups,just1=['333fm','333mbf','444bf','555bf']) # Getting the amount of groups needed
    schedule.getIndividualGroupTimes() # Seeing the start/end time of each group
    getAvailableDuring(personInfo,schedule,combinedEvents) # Identify during which events people should be present based on their registration
    return schedule

def getAvailableDuring(personInfo,scheduleInfo,combinedEvents=None):
    """
    Identify during which events people should be present based on their registration. 
    People are considered to be available for an event if they compete in it, or if they are competing on that day
    and have a registration for an event before and after the event.
    Note, the day split will be wrong if you use this in a time zone where a UTC date shift appears during the comp day.
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
    
def splitNonOverlapGroups(scheduleInfo,personInfo,event,scramblerCount):
    """
    Function called for events which do not have something overlapping.
    In the regular assignments, sets aside scramblerCount scramblers for each group
    """
    dontSpeedScramble = ('333bf','444bf','555bf') # These events do not pick aside some fast people to scramble other groups.
    groups = scheduleInfo.groups[event]
    totalComp = scheduleInfo.eventCompetitors[event]
    perGroup = len(totalComp)/len(groups)
    if event in dontSpeedScramble:
        i = 0
        for groupNum in range(1,len(groups)+1):
            while perGroup*(groupNum) > i:
                groups[groupNum].append(totalComp[i])
                personInfo[totalComp[i]].groups[event] = groupNum
                i+=1
        if i < len(totalComp): # If some people were somehow left out, add them in the last group
            groups[groupNum].append(totalComp[i])
            personInfo[totalComp[i]].groups[event] = groupNum
            i+=1
    else:
        i = len(totalComp)-1
        sCount = 0
        for groupNum in range(1,len(groups)+1):
            for _ in range(1,scramblerCount+1):
                # Take the x best people yet to be assigned into group
                groups[groupNum].append(totalComp[sCount])
                personInfo[totalComp[sCount]].groups[event] = groupNum
                i-=1
                sCount+=1
            while perGroup*(len(groups)-groupNum) < i+1:
                # Take the slower people left and assign
                groups[groupNum].append(totalComp[i+sCount])
                personInfo[totalComp[i+sCount]].groups[event] = groupNum
                i-=1
        if i > -1: # If some people were somehow left out, add them in the last group
            personInfo[totalComp[i+sCount]].groups[event] = groupNum
            i-=1

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
                                    if len(groups[idy+1]) < perGroup: # If there is more than one group
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

def splitIntoGroups(scheduleInfo,personInfo,scramblerCount):
    already = set()
    for event in scheduleInfo.events:
        if event[0] not in already:
            if event[0] not in scheduleInfo.overlappingEvents:
                splitNonOverlapGroups(scheduleInfo, personInfo, event[0],scramblerCount)
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
            needed = len(scheduleInfo.groups[event][groupNum]) + round(2/7*(len(scheduleInfo.groups[event][groupNum])))
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
                needed = len(scheduleInfo.groups[event][groupNum]) + round(2/7*(len(scheduleInfo.groups[event][groupNum])))
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

def reassignJudges(scheduleInfo,personInfo):
    for event in scheduleInfo.groups:
        scheduleInfo.groupScramblers[event] = {}
        scheduleInfo.groupRunners[event] = {}
        for group in scheduleInfo.groups[event]:
            scheduleInfo.groupScramblers[event][group] = []
            scheduleInfo.groupRunners[event][group] = []
            if event in scheduleInfo.groupJudges:
                if len(scheduleInfo.groupJudges[event][group]) > 0: # If judges are assigned for the event
                    # Always at least one scrambler
                    scheduleInfo.groupJudges[event][group].sort(key=lambda x:personInfo[x].prs[event]*personInfo[x].orga)
                    best = scheduleInfo.groupJudges[event][group][0]
                    scheduleInfo.groupJudges[event][group] = scheduleInfo.groupJudges[event][group][1:]
                    scheduleInfo.groupScramblers[event][group].append(best)
                    for idx,assignment in enumerate(personInfo[best].assignments[event]):
                        if assignment == group:
                            personInfo[best].assignments[event][idx] = f';S{group}' #Update assignment to scrambler
                    
                    runSc = 1 # If divisible by 2 make scrambler, otherwise runner
                    # Alternate runner/scrambler. Only continue if there is enough judges available
                    while len(scheduleInfo.groups[event][group])< len(scheduleInfo.groupJudges[event][group]):
                        if runSc%2 == 0:
                            # scrmbler stuff
                            best = scheduleInfo.groupJudges[event][group][0] # Fastest
                            scheduleInfo.groupJudges[event][group] = scheduleInfo.groupJudges[event][group][1:]
                            scheduleInfo.groupScramblers[event][group].append(best)
                            for idx,assignment in enumerate(personInfo[best].assignments[event]):
                                if assignment == group:
                                    personInfo[best].assignments[event][idx] = f';S{group}'
                        else: # Runners
                            for potRun in scheduleInfo.groupJudges[event][group][::-1]: # Take slowest first
                                if personInfo[potRun].age > 14 and personInfo[potRun].age < 40:
                                    break
                            scheduleInfo.groupJudges[event][group].remove(potRun)
                            scheduleInfo.groupRunners[event][group].append(potRun)
                            for idx,assignment in enumerate(personInfo[potRun].assignments[event]):
                                if assignment == group:
                                    personInfo[potRun].assignments[event][idx] = f';R{group}'
                        runSc += 1

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
    # None

def makePDF(scheduleInfo,personInfo,outfile):
    pdf = FPDF('p','mm', 'A4')

    pdf.add_page()

    pdf.set_auto_page_break(auto=True,margin=15)
    # See main for fonts. Needed because of utf-8 stuff and names
    pdf.add_font('DejaVu','', fname='fonts/DejaVuSansCondensed.ttf', uni=True) 
    pdf.add_font('DejaVub','', fname='fonts/DejaVuSansCondensed-Bold.ttf', uni=True)

    pdf.set_font('DejaVub','',22)
    pdf.cell(65,9,f'{scheduleInfo.name} Group Overview',ln=True)
    for event1 in scheduleInfo.events:
        event = event1[0]
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
            while i < len(competitors): # Print everyone
                # print(i)
                pdf.set_font('DejaVu','',8)
                if len(judges) > i and len(scramblers) > i and len(runners) > i: # Enough for now
                    pdf.cell(45,9,f'{competitors[i]}')
                    pdf.cell(45,9,f'{judges[i]}')
                    pdf.cell(45,9,f'{scramblers[i]}')
                    pdf.cell(45,9,f'{runners[i]}',ln=True)
                elif len(judges) > i and len(scramblers) > i: # Enough judges and scramblers for now
                    pdf.cell(45,9,f'{competitors[i]}')
                    pdf.cell(45,9,f'{judges[i]}')
                    pdf.cell(45,9,f'{scramblers[i]}',ln=True)
                elif len(judges) > i: # Enough judges for now
                    pdf.cell(45,9,f'{competitors[i]}')
                    pdf.cell(45,9,f'{judges[i]}',ln=True)
                else: # Only competitors left
                    pdf.cell(45,9,f'{competitors[i]}',ln=True)
                i+=1
                
    pdf.output(outfile)


def main():
    # Download the file from here (Replace the comp id): https://www.worldcubeassociation.org/api/v0/competitions/VestkystCubing2021/wcif
    # Fonts needed because of utf-8. Document: https://pyfpdf.github.io/fpdf2/Unicode.html. Direct link: https://github.com/reingart/pyfpdf/releases/download/binary/fpdf_unicode_font_pack.zip
    # Make a folder with the ones used in the file.
    # fil = open("dm21/wcif.json")
    # fil = open("../vestkyst/wcif.json")
    fil = open("../jontwix/wcif.json")

    data = json.load(fil)
    # combined = combineEvents('666','777')
    people,organizers = competitorBasicInfo(data)
    stations = 16
    # schedule = scheduleBasicInfo(data,people,organizers,stations,{'333bf':3},combined)
    schedule = scheduleBasicInfo(data,people,organizers,stations)

    # schedule = scheduleBasicInfo(data,people,organizers,stations,combinedEvents=combined)
    scramblers = 3
    schedule, people = splitIntoGroups(schedule,people,scramblers)

    assignJudges(schedule,people)

    reassignJudges(schedule,people)
    # print(people['Martin Vædele Egdal'].groups)
    # print(people['Martin Vædele Egdal'].assignments)

    filenameSave = str(datetime.now().strftime("%m%d_%T")).replace(':','').replace('/','') # Ensure unique name
    # convertCSV(schedule,people,'vestkystcsva.csv',combined)
    # convertCSV(schedule,people,'dmcsva.csv',combined)
    name = schedule.name
    convertCSV(schedule,people,f'out/{name}Groups{filenameSave}.csv')
    makePDF(schedule,people,f'out/{name}Overview{filenameSave}.pdf')


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










