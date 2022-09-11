from collections import deque
from copy import copy
import os

solved = {189889725001869015647844142637570925,376852987872208983050224706027707245,563816250742546293545156266973125485,750779469037373440117088264631278445}

start = 189889725001869015647844142637570925

def swap3(k, pos1, pos2):
	set1 =  (k >> pos1) & 7
	set2 =  (k >> pos2) & 7
	xor = (set1 ^ set2)
	xor = (xor << pos1) | (xor << pos2)
	return k ^ xor

# triggers = {"R U R'":["R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R' U' R'","R' U R'","F","F'","R","U","U'","U2","D","D'"],
# "R U2 R'":["R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R' U' R'","R' U R'","F","F'","R","U","U'","U2","D","D'"],
# "R U' R'":["R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R' U' R'","R' U R'","F","F'","R","U","U'","U2","D","D'"],
# "R' U' R":["R U R'","R U2 R'","R U' R'","f","f'","S","S'","r","r'","R D R'","R D' R'","R U' R","R U R","F","F'","R","U","U'","U2","D","D'"],
# "R' U R":["R U R'","R U2 R'","R U' R'","f","f'","S","S'","r","r'","R D R'","R D' R'","R U' R","R U R","F","F'","R","U","U'","U2","D","D'"],
# "R' U2 R":["R U R'","R U2 R'","R U' R'","f","f'","S","S'","r","r'","R D R'","R D' R'","R U' R","R U R","F","F'","R","U","U'","U2","D","D'"],
# "R' D R":["R U R'","R U2 R'","R U' R'","f","f'","S","S'","r","r'","R D R'","R D' R'","R U' R","R U R","F","F'","R","U","U'","U2","D","D'"],
# "R' D' R":["R U R'","R U2 R'","R U' R'","f","f'","S","S'","r","r'","R D R'","R D' R'","R U' R","R U R","F","F'","R","U","U'","U2","D","D'"],
# "R D R'":["R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R' U' R'","R' U R'","F","F'","R'","U","U'","U2","D","D'"],
# "R D' R'":["R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R' U' R'","R' U R'","F","F'","R'","U","U'","U2","D","D'"],
# "R' U' R'":["R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R' U' R'","R' U R'","F","F'","R'","U","U'","U2","D","D'"],
# "R' U R'":["R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R' U' R'","R' U R'","F","F'","R'","U","U'","U2","D","D'"],
# "R U' R":["R U R'","R U2 R'","R U' R'","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R U' R","R U R","F","F'","R","U","U'","U2","D","D'"],
# "R U R":["R U R'","R U2 R'","R U' R'","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R U' R","R U R","F","F'","R","U","U'","U2","D","D'"],
# "F":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'","U","U'","U2","D","D'"],
# "F'":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'","U","U'","U2","D","D'"],
# "R":["R U R'","R U2 R'","R U' R'","R D R'","R D' R'","R U' R","R U R","f","f'","S","S'","r","r'","F","F'","R","U","U'","U2","D","D'"],
# "R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","f","f'","S","S'","r","r'","F","F'","U","U'","U2","D","D'"],
# "U":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","D","D'"],
# "U'":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","D","D'"],
# "U2":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","D","D'"],
# "D":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'"],
# "D'":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'"],
# "r":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","U","U'","U2","D","D'"],
# "r'":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","U","U'","U2","D","D'"],
# "S": ["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","f","f'","S","r","r'","F'","R","R'","U","U'","U2","D","D'"],
# "S'": ["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","f","f'","r","r'","F","R","R'","U","U'","U2","D","D'"],
# "f": ["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","S","r","r'","F","F'","R","R'","U","U'","U2","D","D'"],
# "f'": ["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","S'","r","r'","F","F'","R","R'","U","U'","U2","D","D'"],
# "k":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","f","f'","S","S'","r","r'","F","F'","R","R'","U","U'","U2","D","D'"]}

#only rud
triggers = {"R U R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","R","U","U'","U2","D","D'"],
"R U2 R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","R","U","U'","U2","D","D'"],
"R U' R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","R","U","U'","U2","D","D'"],
"R' U' R":["R U R'","R U2 R'","R U' R'","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R' U R":["R U R'","R U2 R'","R U' R'","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R' U2 R":["R U R'","R U2 R'","R U' R'","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R' D R":["R U R'","R U2 R'","R U' R'","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R' D' R":["R U R'","R U2 R'","R U' R'","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R D R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","R'","U","U'","U2","D","D'"],
"R D' R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","R'","U","U'","U2","D","D'"],
"R' U' R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","R'","U","U'","U2","D","D'"],
"R' U R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","R'","U","U'","U2","D","D'"],
"R U' R":["R U R'","R U2 R'","R U' R'","R' D R","R' D' R","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R U R":["R U R'","R U2 R'","R U' R'","R' D R","R' D' R","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R":["R U R'","R U2 R'","R U' R'","R D R'","R D' R'","R U' R","R U R","R","U","U'","U2","D","D'"],
"R'":["R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R' U' R'","R' U R'","U","U'","U2","D","D'"],
"U":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'","D","D'"],
"U'":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'","D","D'"],
"U2":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'","D","D'"],
"D":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'"],
"D'":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'"],
"k":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","R","R'","U","U'","U2","D","D'"]}

# "R' F R":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","U","U'","U2","D","D'","r","r'"],
# "R' F' R":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","U","U'","U2","D","D'","r","r'"],
# "R2 D' R2":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","U","U'","U2","D","D'"],
# "R2 D R2":["R U R'","R U2 R'","R U' R'","R' U' R","R' U R","R' U2 R","f","f'","S","S'","r","r'","R' D R","R' D' R","R D R'","R D' R'","R' U' R'","R' U R'","R U' R","R U R","F","F'","R","R'","U","U'","U2","D","D'"],


def R(k):
	# corners
	k=swap3(swap3(swap3(k,90,18),39,138),138,18)
	k=swap3(swap3(swap3(k,132,45),84,12),12,132)
	k=swap3(swap3(swap3(k,69,66),63,60),60,69) 

	# edges
	k=swap3(swap3(swap3(k,78,126),6,27),78,27)
	k=swap3(swap3(swap3(k,57,54),51,48),57,48) 
	return k

def Rp(k):
	# corners
	k=swap3(swap3(swap3(k,90,18),39,138),39,90)
	k=swap3(swap3(swap3(k,132,45),84,12),84,45)
	k=swap3(swap3(swap3(k,69,66),63,60),63,66)

	# edges
	k=swap3(swap3(swap3(k,78,126),6,27),126,6)
	k=swap3(swap3(swap3(k,57,54),51,48),54,51)
	return k

def R2(k):
	# corners
	k=swap3(swap3(k,90,39),18,138)
	k=swap3(swap3(k,132,12),84,45)
	k=swap3(swap3(k,69,60),63,66)

	# edges
	k=swap3(swap3(k,6,126),78,27)
	k=swap3(swap3(k,51,54),57,48) 
	return k

def U(k):
	# corners
	k=swap3(swap3(swap3(k,90,114),66,42),90,42)
	k=swap3(swap3(swap3(k,69,93),117,45),69,117)
	k=swap3(swap3(swap3(k,132,135),138,141),132,141)

	# edges
	k=swap3(swap3(swap3(k,81,105),57,33),81,33)
	k=swap3(swap3(swap3(k,120,123),126,129),120,129)
	return k

def Up(k):
	# corners
	k=swap3(swap3(swap3(k,90,114),66,42),114,66)
	k=swap3(swap3(swap3(k,69,93),117,45),93,45)
	k=swap3(swap3(swap3(k,132,135),138,141),135,138) 

	# edges
	k=swap3(swap3(swap3(k,81,105),57,33),105,57)
	k=swap3(swap3(swap3(k,120,123),126,129),123,126) 
	return k

def U2(k):
	# corners
	k=swap3(swap3(k,90,42),114,66)
	k=swap3(swap3(k,117,69),93,45)
	k=swap3(swap3(k,132,141),135,138) 

	# edges
	k=swap3(swap3(k,81,33),105,57)
	k=swap3(swap3(k,120,129),123,126) 
	return k

def D(k):
	# corners
	k=swap3(swap3(swap3(k,87,63),111,39),87,39)
	k=swap3(swap3(swap3(k,84,108),36,60),108,60)
	k=swap3(swap3(swap3(k,21,18),15,12),21,12)

	# edges
	k=swap3(swap3(swap3(k,72,48),96,24),72,24)
	k=swap3(swap3(swap3(k,9,6),3,0),9,0)
	return k

def Dp(k):
	# corners
	k=swap3(swap3(swap3(k,87,63),111,39),63,111)
	k=swap3(swap3(swap3(k,84,108),36,60),84,36)
	k=swap3(swap3(swap3(k,21,18),15,12),18,15)

	# edges
	k=swap3(swap3(swap3(k,72,48),96,24),48,96)
	k=swap3(swap3(swap3(k,9,6),3,0),6,3)
	return k

def F(k):
	# corners
	k=swap3(swap3(swap3(k,135,69),18,108),135,18)
	k=swap3(swap3(swap3(k,132,114),21,63),114,63)
	k=swap3(swap3(swap3(k,93,90),87,84),93,84)

	# edges
	k=swap3(swap3(swap3(k,120,51),102,9),9,120)
	k=swap3(swap3(swap3(k,81,78),72,75),81,72)
	return k

def Fp(k):
	# corners
	k=swap3(swap3(swap3(k,135,69),18,108),69,108)
	k=swap3(swap3(swap3(k,132,114),21,63),132,21)
	k=swap3(swap3(swap3(k,93,90),87,84),90,87)

	# edges
	k=swap3(swap3(swap3(k,120,51),102,9),102,51)
	k=swap3(swap3(swap3(k,81,78),72,75),78,75)
	return k

def r(k):
	# normal R
	k = R(k)

	# middle layer
	k = swap3(swap3(swap3(k,9,81),129,24),9,129)
	k = swap3(swap3(swap3(k,0,72),120,33),0,120)
	return k

def rp(k):
	# normal R
	k = Rp(k)

	# middle layer
	k = swap3(swap3(swap3(k,9,81),129,24),81,24)
	k = swap3(swap3(swap3(k,0,72),120,33),72,33)
	return k

def f(k):
	k = F(k)
	k = swap3(swap3(swap3(k,123,57),6,96),123,6)
	k = swap3(swap3(swap3(k,3,48),126,105),105,48)
	return k

def fp(k):
	k = Fp(k)
	k = swap3(swap3(swap3(k,123,57),6,96),57,96)
	k = swap3(swap3(swap3(k,3,48),126,105),126,3)
	return k

def S(k):
	k = swap3(swap3(swap3(k,123,57),6,96),123,6)
	k = swap3(swap3(swap3(k,3,48),126,105),105,48)
	return k

def Sp(k):
	k = swap3(swap3(swap3(k,123,57),6,96),57,96)
	k = swap3(swap3(swap3(k,3,48),126,105),126,3)
	return k


num_to_colour = {'000':'w','001':'o','010':'g','011':'r','100':'b','101':'y','110':'wwww'}
# print(num_to_colour['000'])
def printbin(k):
	i = []
	p = format(k,'b')
	while len(p) < 144:
		p = '0'+p
	for j in range(0,144,3):
		# print(j)
		i.append(num_to_colour[p[j:j+3]])
	print(i,len(i))

# printbin(Dp(start))

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
		if len(path) < 6:
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

def mk_inv(li):
	inverted = []
	li = li[1:]
	for trigger in li[::-1]:
		t = trigger.split(' ')
		for move in t[::-1]:
			if move[-1] == "'":
				inverted.append(move[0])
			elif move[-1] == '2':
				inverted.append(move)
			else:
				inverted.append(f"{move}'")
	return inverted

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
	
# scramble = "R' U R U R' U' R' D' R U2 R' D R U R".split(' ')
# scramble = "R' U R U' R' U R U R' U2 R U' R' U' R' D' R U' R' D R2".split(' ')
# scramble = "R' U' R U' R' U R U' R' U2 R' D' R U2 R' D R U2 R".split(' ')
scramble = "r U2 R' U' R U' r' U R U2 R' U2 R' F R F'".split(' ')
mdic = {"R":R,"R'":Rp,"R2":R2,"U":U,"U'":Up,"U2":U2,"D":D,"D'":Dp,"F":F,"F'":Fp,"r":r,"r'":rp,"f":f,"f'":fp,'S':S,"S'":Sp}

for move in scramble:
	start = mdic[move](start)

# printbin(rp(start))

import pickle
import time
# dist = get_dist_6()
# print('dumping')
# t0 = time.time()
# Ff = open('dist_6RUD.pickle','wb')
# pickle.dump(dist,Ff)
# t1 = time.time()
# print(t1-t0)

t0 = time.time()
# Ff = open('dist_6_s.pickle','rb')
Ff = open('dist_6RUD.pickle','rb')
dist = pickle.load(Ff)
Ff.close()
t1 = time.time()
print('loaded')

print(hit_dist(start,dist,'pi5'))

