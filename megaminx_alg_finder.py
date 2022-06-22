from copy import copy
import os
from collections import deque

solved = {5846006548539749907562085968704121571881223454793,
5846006545436192427117968858812016819630321434697,
5846006546213980694309325083506633208355753033801,
5846006546991768932638883004787161850479915302985,
5846006547769542393727709578054764232754180653129}

start = 5846006547769542393727709578054764232754180653129
oll_cube_start = 5846006543879093802079845542824892081549462208585
oll_cube = 5846006543879093802079845542824892081549462208585

def swap3(k, pos1, pos2):
	set1 =  (k >> pos1) & 7
	set2 =  (k >> pos2) & 7
	xor = (set1 ^ set2)
	xor = (xor << pos1) | (xor << pos2)
	return k ^ xor

def oll_check(k):
	return k & 5846006543879093802079878657956049032249801179135 == 5846006543879093802079845542824892081549462208585

colourmap = {'111':'grey','110':'lgreen','101':'orange','100':'lblue','011':'cream','010':'lilla','001':'dgreen','000':'blue/red'}

def printp(k):
	idx = 3
	ans = []
	j = bin(k)[2:]
	add = len(j)%3
	if add == 1:
		j = '00'+j
	elif add == 2:
		j = '0'+j
	# grey
	line = []
	for i in range(10):
		line.append(colourmap[j[idx-3:idx]])
		idx+=3
	ans.append(copy(line))
	line = []
	for i in range(15):
		line.append(colourmap[j[idx-3:idx]])
		idx+=3
	ans.append(copy(line))
	for lin in ans:
		print(lin)
	# print(line)
	

triggers ={
	"R U R'":["R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R'","R2'",'U2',"U2'"],
	"R U2 R'":["R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R'","R2'",'U2',"U2'"],
	"R U2' R'":["R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R'","R2'",'U2',"U2'"],
	"R U' R'":["R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R'","R2'",'U2',"U2'"],
	"R' F R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R' F' R'":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R' F2 R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R' U2 R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R' U R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R' U' R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R' U2' R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R2 U2' R2'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R'",'U2',"U2'"],
	"R2 U2 R2'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R'",'U2',"U2'"],
	"R2' U2' R2":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R'",'U2',"U2'"],
	"R2' U2 R2":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R'",'U2',"U2'"],
	"R U R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R U' R":["R U R'","R U2 R'","R U2' R'","R U' R'","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R2","R2'",'U2',"U2'"], 
	"R' U R'":["R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R'","R2'",'U2',"U2'"],
	"R' U' R'":["R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2' U2' R2","R2' U2 R2","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R'","R2'",'U2',"U2'"],
	"F U' F'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","U","U'","F'","R","R'","R2","R2'",'U2',"U2'"],
	"F' U F":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","U","U'","F","R","R'","R2","R2'",'U2',"U2'"],
	"F U F'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","U","U'","F","R","R'","R2","R2'",'U2',"U2'"],
	"F' U' F":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","U","U'","F'","R","R'","R2","R2'",'U2',"U2'"],
	"U":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","F","F'","R","R'","R2","R2'"],
	"U'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","F","F'","R","R'","R2","R2'"],
	"F":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F U F'","U","U'","F","R","R'","R2","R2'",'U2',"U2'"],
	"F'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F' U F","F' U' F","U","U'","F'","R","R'","R2","R2'",'U2',"U2'"],
	"R":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'",'U2',"U2'"],
	"R'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'",'U2',"U2'"],
	"R2":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'",'U2',"U2'"],
	"R2'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'",'U2',"U2'"],
	'U2':["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","F","F'","R","R'","R2","R2'"],
	"U2'":["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","F","F'","R","R'","R2","R2'"],
	'k':["R U R'","R U2 R'","R U2' R'","R U' R'","R' F R", "R' F' R'","R' F2 R","R' U2 R","R' U R","R' U' R","R' U2' R","R2 U2' R2'","R2 U2 R2'","R2' U2' R2","R2' U2 R2","R U R","R U' R","R' U R'","R' U' R'","F U' F'","F' U F","F U F'","F' U' F","U","U'","F","F'","R","R'","R2","R2'",'U2',"U2'"]
}

def R(k):
	# edges
	k = swap3(swap3(swap3(swap3(k,138,69),12,3),138,3),138,78)
	k = swap3(swap3(swap3(swap3(k,99,72),45,39),99,39),99,75) # inner

	# corners
	k = swap3(swap3(swap3(swap3(k,135,33),15,6),135,6),135,105)
	k = swap3(swap3(swap3(swap3(k,93,0),51,9),93,9),93,141)
	k = swap3(swap3(swap3(swap3(k,96,36),48,42),96,42),96,102) # inner
	return k

def Rp(k):
	# edges
	k = swap3(swap3(swap3(swap3(k,138,69),12,3),69,12),12,78)
	k = swap3(swap3(swap3(swap3(k,99,72),45,39),72,45),45,75) # inner

	# corners

	k = swap3(swap3(swap3(swap3(k,135,33),15,6),33,15),15,105)
	k = swap3(swap3(swap3(swap3(k,93,0),51,9),0,51),51,141)
	k = swap3(swap3(swap3(swap3(k,96,36),48,42),36,48),48,102) # inner
	return k

def U(k):
	# edges
	k = swap3(swap3(swap3(swap3(k,117,108),99,90),126,108),108,90)
	k = swap3(swap3(swap3(swap3(k,150,144),138,132),156,144),144,132) # inner

	# corners
	k = swap3(swap3(swap3(swap3(k,120,111),102,93),129,111),111,93)
	k = swap3(swap3(swap3(swap3(k,123,114),105,96),87,114),114,96)
	k = swap3(swap3(swap3(swap3(k,153,147),141,135),159,147),147,135) # inner
	return k

def Up(k):
	k = swap3(swap3(swap3(swap3(k,117,108),99,90),126,117),126,99)
	k = swap3(swap3(swap3(swap3(k,150,144),138,132),156,150),156,138) # inner

	# corners
	k = swap3(swap3(swap3(swap3(k,120,111),102,93),129,120),129,102)
	k = swap3(swap3(swap3(swap3(k,123,114),105,96),87,123),87,105)
	k = swap3(swap3(swap3(swap3(k,153,147),141,135),159,153),159,141) # inner
	return k

def F(k):
	k = swap3(swap3(swap3(swap3(k,84,144),18,27),18,84),18,75)
	k = swap3(swap3(swap3(swap3(k,81,108),54,60),54,81),54,78) # inner

	k = swap3(swap3(swap3(swap3(k,114,141),21,30),21,114),21,48)
	k = swap3(swap3(swap3(swap3(k,147,102),24,66),24,147),24,15)
	k = swap3(swap3(swap3(swap3(k,111,105),57,63),57,111),57,51)
	return k

def Fp(k):
	k = swap3(swap3(swap3(swap3(k,84,144),18,27),27,144),144,75)
	k = swap3(swap3(swap3(swap3(k,81,108),54,60),60,108),108,78) # inner

	k = swap3(swap3(swap3(swap3(k,114,141),21,30),30,141),141,48)
	k = swap3(swap3(swap3(swap3(k,147,102),24,66),66,102),102,15)
	k = swap3(swap3(swap3(swap3(k,111,105),57,63),63,105),105,51)
	return k

def U2(k):
	return U(U(k))

def U2p(k):
	return Up(Up(k))

def R2(k):
	return R(R(k))

def R2p(k):
	return Rp(Rp(k))

def F2(k):
	return F(F(k))

def F2p(k):
	return Fp(Fp(k))

mdic = {"R":R,"R'":Rp,"R2":R2,"R2'":R2p,"U":U,"U'":Up,"U2":U2,"U2'":U2p,"F":F,"F'":Fp,"F2":F2,"F2'": F2p}

def mk_inv(li):
	inverted = []
	li = li[1:]
	for trigger in li[::-1]:
		t = trigger.split(' ')
		for move in t[::-1]:
			if move[-1] == "'":
				inverted.append(move[:-1])
			# elif move[-1] == '2':
			# 	inverted.append(f"{move}'")
			else:
				inverted.append(f"{move}'")
	return inverted

def get_dist_6():
	dist = {}
	i = 0
	# q = deque([(k, [], 'k')])
	q = deque()
	for solved_case in solved:
		# print(solved_case)
		q.append((solved_case, ['k']))
	while q:
		s, path = q.popleft()
		if len(path) < 5:
			for trigger in triggers[path[-1]]:
				npos = s
				for move in trigger.split(' '):
					npos = mdic[move](npos)
				#print(self.pos)
				newpath = copy(path)
				newpath.append(trigger)
				if npos not in dist:
					dist[npos] = newpath
					q.append((npos,newpath))
					i+=1
					if i%100000 == 0:
						print(i,len(newpath))
		else:
			break
	return dist

def hit_dist(k,dist,dest):
	with open(f"{dest}.txt",'a') as dd:
		i=0
		if k in dist:
			return dist[k]
		visited = set()
		q = deque([(k, ['k'])])
		while q:
			s, path = q.popleft()
			if s not in visited:
				visited.add(s)
				for trigger in triggers[path[-1]]:
					npos = s
					for move in trigger.split(' '):
						npos = mdic[move](npos)
					#print(self.pos)
					newpath = copy(path)
					newpath.append(trigger)
					if npos in dist:
						# print(" ".join(newpath))
						# print(" ".join(dist[npos]))
						# print('---')
						temp = " ".join(newpath[1:]) + ' ' + " ".join(mk_inv(dist[npos]))
						print(temp)
						# print(temp,file=dd)
						dd.write(temp + os.linesep)
						print(i)
						i+=1
						# printbin(npos)
						# return (" ".join(newpath)," ".join(dist[npos]))
					else:
						q.append((npos,newpath))
						# i+=1
						# if i%100000 == 0:
						# 	print(i,len(newpath))

# kk = start

def get_oll_dist_6():
	dist = {}
	i = 0
	# q = deque([(k, [], 'k')])
	q = deque()
	
	q.append((oll_cube_start, ['k']))
	while q:
		s, path = q.popleft()
		if len(path) < 5:
			for trigger in triggers[path[-1]]:
				npos = s
				for move in trigger.split(' '):
					npos = mdic[move](npos)
				#print(self.pos)
				newpath = copy(path)
				newpath.append(trigger)
				if npos not in dist:
					dist[npos] = newpath
					q.append((npos,newpath))
					i+=1
					if i%100000 == 0:
						print(i,len(newpath))
		else:
			break
	return dist

def oll_hit_dist(k,dist,dest):
	with open(f"{dest}.txt",'a') as dd:
		i=0
		if k in dist:
			return dist[k]
		visited = set()
		q = deque([(k, ['k'])])
		while q:
			s, path = q.popleft()
			if s not in visited:
				visited.add(s)
				for trigger in triggers[path[-1]]:
					npos = s
					for move in trigger.split(' '):
						npos = mdic[move](npos)
					#print(self.pos)
					newpath = copy(path)
					newpath.append(trigger)
					if npos in dist:
						# print(" ".join(newpath))
						# print(" ".join(dist[npos]))
						# print('---')
						temp = " ".join(newpath[1:]) + ' ' + " ".join(mk_inv(dist[npos]))
						print(temp)
						# print(temp,file=dd)
						dd.write(temp + os.linesep)
						print(i)
						i+=1
						# printbin(npos)
						# return (" ".join(newpath)," ".join(dist[npos]))
					else:
						q.append((npos,newpath))
						# i+=1
						# if i%100000 == 0:
						# 	print(i,len(newpath))

scramble = "R' F' U F U' F' U2' F U R".split(' ') # The alg to setup of the case, inverse of solving
for move in scramble:
	# start = mdic[move](start) # For pll
	oll_cube = mdic[move](oll_cube) # For oll

import pickle
import time
# # Generate PLL pattern DB, run this separately first
# t0 = time.time()
# dist = get_dist_6()
# t1 = time.time()
# print(t1-t0)
# print('dumping')
# t0 = time.time()
# Ff = open('mega_dist_6.pickle','wb')
# pickle.dump(dist,Ff)
# t1 = time.time()
# print(t1-t0)

# # Load pattern DB, run this after having a local pattern DB
# t0 = time.time()
# Ff = open('mega_dist_6.pickle','rb')
# dist = pickle.load(Ff)
# Ff.close()
# t1 = time.time()
# print('loaded')
# print(hit_dist(start,dist,'z3'))

### _____ OLL

# # Generate OLL pattern DB, run this separately first
# t0 = time.time()
# dist = get_oll_dist_6()
# t1 = time.time()
# print(t1-t0)
# print('dumping')
# t0 = time.time()
# Ff = open('mega_oll_dist_6.pickle','wb')
# pickle.dump(dist,Ff)
# t1 = time.time()
# print(t1-t0)

# # Load pattern DB, run this after having a local pattern DB
t0 = time.time()
Ff = open('mega_oll_dist_6.pickle','rb')
dist = pickle.load(Ff)
Ff.close()
t1 = time.time()
print('loaded')
print(oll_hit_dist(oll_cube,dist,'oll_test')) # Change the string for the file name

