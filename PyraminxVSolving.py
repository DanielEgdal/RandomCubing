from collections import deque, defaultdict
from copy import deepcopy
import joblib

# solved c = 100  
# green = 00
# red = 10
# blue = 01
# yellow = 11
# Pyra:
# 3333333 2222222222222 11111111111111 00000000000000
# 543 210 987 654 21 09 87 65 43 21 09 87 65 43 21 0- # center shift +2 is on purpose
# 100 100 100 100 00 00 00 10 10 10 01 01 01 11 11 11
#   1 100 100 100| 01 11 11| 11 10 01| 00 01 10| 10 00 00
#---
# 100100100000111100001100110000000000 39207357440
#100100100000110011001100000000110000 39204995120
#100100100000001111000000110000110000 39195511856
#---
#100100000100110000111100001100000000 38734643968
#100100000100000000110011001100000011 38722024195
#100100000100110000001111000000000011 38734458883
#---
#100000100100000000110000001111001100 34963915724
#100000100100001100110000111100000000 34967064320
#100000100100001100000000110011001100 34966867148
#---
#000100100100000011000011000000110011 4899745843
#000100100100000000000011000011001111 4898959567
#000100100100000011000000000011111100 4899733756

##--- bar check
# 100 000 000 000 11 00 00 00 11 00 00 00 00 00 00 00
# 100 000 000 000 00 11 00 00 00 00 11 00 00 00 00 00
# 100 000 000 000 00 00 00 11 00 00 00 11 00 00 00 00

# 001 000 000 000 11 00 00 00 11 00 00 00 00 00 00 00 # blå grøn
# 001 000 000 000 00 11 00 00 00 00 11 00 00 00 00 00 # blå rød
# 001 000 000 000 00 00 00 11 00 00 00 11 00 00 00 00 # grøn rød

# 010 000 000 000 11 00 00 00 11 00 00 00 00 00 00 00 # rød blå
# 010 000 000 000 00 11 00 00 00 00 11 00 00 00 00 00 # rød grøn
# 010 000 000 000 00 00 00 11 00 00 00 11 00 00 00 00 # blå grøn
#--
# 000 100 000 000 11 00 00 00 11 00 00 00 00 00 00 00
# 000 100 000 000 00 00 11 00 00 00 00 00 00 11 00 00
# 000 100 000 000 00 00 00 00 00 11 00 00 00 00 00 11

# 000 001 000 000 11 00 00 00 11 00 00 00 00 00 00 00 #rød gul
# 000 001 000 000 00 00 11 00 00 00 00 00 00 11 00 00 #rød grøn
# 000 001 000 000 00 00 00 00 00 11 00 00 00 00 00 11 #gul grøn

# 000 010 000 000 11 00 00 00 11 00 00 00 00 00 00 00 # gul grøn
# 000 010 000 000 00 00 11 00 00 00 00 00 00 11 00 00 #gul rød
# 000 010 000 000 00 00 00 00 00 11 00 00 00 00 00 11 #grøn rød
#---
# 000 000 100 000 00 11 00 00 00 00 11 00 00 00 00 00
# 000 000 100 000 00 00 11 00 00 00 00 00 00 11 00 00
# 000 000 100 000 00 00 00 00 00 00 00 00 11 00 11 00

# 000 000 001 000 00 11 00 00 00 00 11 00 00 00 00 00 #gul grøn
# 000 000 001 000 00 00 11 00 00 00 00 00 00 11 00 00 #gul blå
# 000 000 001 000 00 00 00 00 00 00 00 00 11 00 11 00 #grøn blå

# 000 000 010 000 00 11 00 00 00 00 11 00 00 00 00 00 # blå gul
# 000 000 010 000 00 00 11 00 00 00 00 00 00 11 00 00 #blå grøn
# 000 000 010 000 00 00 00 00 00 00 00 00 11 00 11 00 #gul grøn
#---
# 000 000 000 100 00 00 00 11 00 00 00 11 00 00 00 00
# 000 000 000 100 00 00 00 00 00 11 00 00 00 00 00 11
# 000 000 000 100 00 00 00 00 00 00 00 00 11 00 11 00

# 000 000 000 001 00 00 00 11 00 00 00 11 00 00 00 00 # blå gul
# 000 000 000 001 00 00 00 00 00 11 00 00 00 00 00 11 # blå rød
# 000 000 000 001 00 00 00 00 00 00 00 00 11 00 11 00 # gul rød

# 000 000 000 010 00 00 00 11 00 00 00 11 00 00 00 00 # gul rød
# 000 000 000 010 00 00 00 00 00 11 00 00 00 00 00 11 #gul blå
# 000 000 000 010 00 00 00 00 00 00 00 00 11 00 11 00 # rød blå


def dB(n):
	return "{0:b}".format(int(n))

def swap2(k, pos1, pos2):
	set1 =  (k >> pos1) & 3
	set2 =  (k >> pos2) & 3
	xor = (set1 ^ set2)
	xor = (xor << pos1) | (xor << pos2)
	return k ^ xor

def swap1(k, pos1, pos2):
	set1 =  (k >> pos1) & 1
	set2 =  (k >> pos2) & 1
	xor = (set1 ^ set2)
	xor = (xor << pos1) | (xor << pos2)
	return k ^ xor

def twistC(k,pos): # pos = pos start
	k = swap1(k,pos,pos-1)
	k = swap1(k,pos-1,pos-2)
	return k

def twistCC(k,pos): # pos = pos start
	k = swap1(k,pos-1,pos-2)
	k = swap1(k,pos,pos-1)
	return k

def U(k):
	k = twistC(k,35) #center
	# print(dB(k))
	k = swap2(k,22,10)
	# print(dB(k))
	k = swap2(k,10,16)
	# print(dB(k))
	k = swap2(k,20,8)
	# print(dB(k))
	k = swap2(k,8,14)
	# print(dB(k))

	return(k)

def Up(k):
	k = twistCC(k,35) #center

	k = swap2(k,10,16)
	k = swap2(k,22,10)

	k = swap2(k,8,14)
	k = swap2(k,20,8)

	return(k)

def R(k):
	k = twistC(k,29) #center

	k = swap2(k,20,4)
	k = swap2(k,4,6)

	k = swap2(k,10,18)
	k = swap2(k,18,2)

	return(k)

def Rp(k):
	k = twistCC(k,29) #center

	k = swap2(k,4,6)
	k = swap2(k,20,4)

	k = swap2(k,18,2)
	k = swap2(k,10,18)

	return(k)

def L(k):
	k = twistC(k,32) #center

	k = swap2(k,22,12)
	k = swap2(k,12,4)

	k = swap2(k,14,0)
	k = swap2(k,0,18)

	return(k)

def Lp(k):
	k = twistCC(k,32) #center

	k = swap2(k,12,4)
	k = swap2(k,22,12)

	k = swap2(k,0,18)
	k = swap2(k,14,0)

	return(k)

def B(k):
	k = twistC(k,26) #center

	k = swap2(k,8,2)
	k = swap2(k,2,12)

	k = swap2(k,16,6)
	k = swap2(k,6,0)

	return(k)

def Bp(k):
	k = twistCC(k,26) #center

	k = swap2(k,2,12)
	k = swap2(k,8,2)

	k = swap2(k,6,0)
	k = swap2(k,16,6)

	return(k)


mdic = {"R":R,"R'":Rp,"B":B,"B'":Bp,"L":L,"L'":Lp,"U":U,"U'":Up}

solved = 39258858879
start = solved
# print(dB(solved))
# print(dB(B(j)))

# scramble = "R' B R B L R B' U' L' R' B'".split(' ')
# scramble = "L' U R B' U' L' R L' R B R'".split(' ')
# scramble = "U L' R' L B' U' L U".split(' ')
# scramble = "R' U R U' R U' B U B' R B R' B' L' B'".split(' ')
# scramble = "U' R B' R' B U' B L' B' L' R' L' R".split(' ')

# for move in scramble:
#     start = mdic[move](start)
# #     # print(dB(start))
# print(start)

def dist():
	possmoves = ["U", "U'", "R", "R'", "L", "L'", "B","B'"]
	idx = 0
	lmove = {solved:'k'}
	overview = [set(),set(),set(),set(),set(),set(),set(),set(),set(),set(),set(),set()]
	overview[0].add(solved)
	for i in range(12):
		for pos in overview[i]:
			for move in possmoves:
				if move[0] != lmove[pos]:
					#print(pos)
					posn = mdic[move](pos)
					if posn not in lmove:
						lmove[posn] = move[0]
						overview[i+1].add(posn)
					# if posn not in overview[(i-1)%12] and posn not in overview[i]:
					#     overview[i+1].add(posn)
						idx+=1
						if idx%100000 == 0:
							print(idx,i)
							for kk, k in enumerate(overview):
								print(kk,len(k))

	for kk, k in enumerate(overview):
		print(kk,len(k))
	return overview

def checkCenters(k):
	c = 0
	ans = [0,0,0,0]
	if k >> 33 == 4: # u
		c +=1
		ans[0] = 1
	if (k >> 30) & 4 == 4: # l
		c +=1
		ans[1] = 1
	if (k >> 27) & 4 == 4: # r
		c +=1
		ans[2] = 1
	if (k >> 24) & 4 == 4: # b
		c +=1
		ans[3] = 1
	return c, ans

def vCheck(k,ans):
	if ans[0] and ans[1] and ans[2]: # green
		c = 0
		if (k >> 22) & 3 == 0 and (k >> 14) & 3 == 2:
			c += 1
		if (k >> 20) & 3 == 0 and (k >> 10) & 3 == 1:
			c += 1
		if (k >> 18) & 3 == 0 and (k >> 4) & 3 == 3:
			c += 1
		if c > 1:
			return True
	if ans[0] and ans[1] and ans[3]: # red
		c = 0
		if (k >> 16) & 3 == 2 and (k >> 8) & 3 == 1:
			c += 1
		if (k >> 14) & 3 == 2 and (k >> 22) & 3 == 0:
			c += 1
		if (k >> 12) & 3 == 2 and k & 3 == 3:
			c += 1
		if c > 1:
			return True
	if ans[0] and ans[2] and ans[3]: # blue
		c = 0
		if (k >> 20) & 3 == 0 and (k >> 10) & 3 == 1:
			c += 1
		if (k >> 16) & 3 == 2 and (k >> 8) & 3 == 1:
			c += 1
		if (k >> 2) & 3 == 3 and (k >> 6) & 3 == 1:
			c += 1
		if c > 1:
			return True
	if ans[1] and ans[2] and ans[3]: # yellow
		c = 0
		if (k >> 18) & 3 == 0 and (k >> 4) & 3 == 3:
			c += 1
		if (k >> 12) & 3 == 2 and k & 3 == 3:
			c += 1
		if (k >> 2) & 3 == 3 and (k >> 6) & 3 == 1:
			c += 1
		if c > 1:
			return True
	return False

def fastVcheck(k):
	#---
	#100 100 100 000 11 11 00 00 11 00 11 00 00 00 00 00 39207357440
	#100 100 100 000 110011001100000000110000 39204995120
	#100 100 100 000 00 11 11 00 00 00 11 00 00 11 00 00 39195511856
	#-- opp
	#100 100 100 000 00 00 00 00 10 00 01 00 00 00 00 00 39191610368
	#100100100000000000001000000000110000 39191609392
	#100 100 100 000 00 00 00 00 00 00 01 00 00 11 00 00 39191577648
	if k & 39207357440 == 39191610368:
		return True,1
	if k & 39204995120 == 39191609392:
		return True,2
	if k & 39195511856 == 39191577648:
		return True,3
	#---
	#100100000100110000111100001100000000 38734643968
	# 100 100 000 100 | 00 00 00 | 11 00 11 | 00 11 00 | 00 00 11 38722024195
	#100100000100110000001111000000000011 38734458883
	#--- opp
	# 100100000100000000101000000100000000 38721978624
	# 100 100 000 100 00 00 00 10 00 10 00 01 00000011 38721954051
	#100100000100000000001010000000000011 38721855491
	if k & 38734643968 == 38721978624:
		return True,4
	if k & 38722024195 == 38721954051:
		return True,5
	if k & 38734458883 == 38721855491:
		return True,6
	#---
	#100000100100000000110000001111001100 34963915724
	#100000100100001100110000111100000000 34967064320
	#100000100100001100000000110011001100 34966867148
	# --op
	# 100000100100000000100000000101001100 34963849548
	#100000100100000000100000010100000000 34963850496
	#100000100100000000000000010001001100 34963719244
	if k & 34963915724 == 34963849548:
		return True,7
	if k & 34967064320 == 34963850496:
		return True,8
	if k & 34966867148 == 34963719244:
		return True,9
	#---
	#000100100100000011000011000000110011 4899745843
	#000100100100000000000011000011001111 4898959567
	#000100100100000011000000000011111100 4899733756
	#--- op
	#000100100100000000000010000000110011 4898955315
	#000100100100000000000010000001001111 4898955343
	#000100100100000000000000000001111100 4898947196
	
	if k & 4899745843 == 4898955315:
		return True,10
	if k & 4898959567 == 4898955343:
		return True,11
	if k & 4899733756 == 4898947196:
		return True,12
	else:
		return False,0

def vSolve(pos):
	res = fastVcheck(pos)
	if res[0]:
		return []
	possmoves = ["U", "U'", "R", "R'", "L", "L'", "B","B'"]
	# possmoves = ["U", "U'"]
	visited = set()
	q = deque([(pos, [], 'k')])
	while q:
		s, path, last_move = q.popleft()
		if s not in visited:
			visited.add(s)
			for move in possmoves:
				if move[0] != last_move[0]:
					npos = mdic[move](s)
					#print(self.pos)
					newpath = deepcopy(path)
					newpath.append(move)
					res = fastVcheck(npos)
					# print(res)
					if res[0]:
						return newpath
					q.append((npos,newpath,move))

def vDist(dist):
	idx = 0
	overview = [set(),set(),set(),set(),set(),set(),set(),set(),set(),set()]
	for positions in dist:
		for state in positions:
			sol= vSolve(state)
			overview[len(sol)].add(state)
			idx +=1
			if idx%5000 == 0:
				print(idx)
				for kk, k in enumerate(overview):
					print(kk,len(k))
	for kk, k in enumerate(overview):
		print(kk,len(k))
	return overview

def barcheck(k):
	bars = set()
	# 100000000000000000001000000000000000
	# 100000000000000000000000010000000000
	#100000000000000000100000000100000000
	if k&34372370432==34359771136:
		bars.add(1)
		bars.add(2)
		bars.add(4)
		bars.add(6)
	if k&34362887168==34359739392:
		bars.add(1)
		bars.add(3)
		bars.add(8)
		bars.add(9)
	if k&34359935744==34359869696:
		bars.add(4)
		bars.add(5)
		bars.add(7)
		bars.add(8)

	#001000000000010000000000000000000000#blågrøn
	#001000000000000100000000100000000000#blårød
	#001000000000000000000000001000000000#grønrød
	if k&8602566656==8594128896:
		bars.add(1)
		bars.add(3)
		bars.add(8)
		bars.add(9)
	if k&8593083392==8590985216:
		bars.add(4)
		bars.add(5)
		bars.add(7)
		bars.add(8)
	if k&8590131968==8589935104:
		bars.add(1)
		bars.add(2)
		bars.add(4)
		bars.add(6)

	#010000000000100000000100000000000000#rødblå
	#010000000000001000000000000000000000#rødgrøn
	#010000000000000000010000000000000000#blågrøn
	if k&17192501248==17188274176:
		bars.add(4)
		bars.add(5)
		bars.add(7)
		bars.add(8)
	if k&17183017984==17181966336:
		bars.add(1)
		bars.add(2)
		bars.add(4)
		bars.add(6)
	if k&17180066560==17179934720:
		bars.add(1)
		bars.add(3)
		bars.add(8)
		bars.add(9)
	#--
	#000100000000000000001000000000000000
	#000100000000000000000000000000110000
	#000100000000000000000010000000000011
	if k&4307599360==4295000064:
		bars.add(1)
		bars.add(2)
		bars.add(4)
		bars.add(6)
	if k&4295753776==4294967344:
		bars.add(2)
		bars.add(3)
		bars.add(10)
		bars.add(12)
	if k&4294979587==4294975491:
		bars.add(5)
		bars.add(6)
		bars.add(10)
		bars.add(11)
	#000001000000100000001100000000000000#rødgul
	#000001000000000010000000000000000000#rødgrøn
	#000001000000000000000011000000000000#gulgrøn
	if k&1086373888==1082179584:
		bars.add(5)
		bars.add(6)
		bars.add(10)
		bars.add(11)
	if k&1074528304==1074266112:
		bars.add(1)
		bars.add(2)
		bars.add(4)
		bars.add(6)
	if k&1073754115==1073754112:
		bars.add(2)
		bars.add(3)
		bars.add(10)
		bars.add(12)

	#000010000000110000000000000000000000#gulgrøn
	#000010000000000011000000000000100000#gulrød
	#000010000000000000000000000000000010#grønrød
	if k&2160115712==2160066560:
		bars.add(2)
		bars.add(3)
		bars.add(10)
		bars.add(12)
	if k&2148270128==2148270112:
		bars.add(5)
		bars.add(6)
		bars.add(10)
		bars.add(11)
	if k&2147495939==2147483650:
		bars.add(1)
		bars.add(2)
		bars.add(4)
		bars.add(6)
	#---
	#000000100000000000000000010000000000
	#000000100000000000000000000000110000
	#000000100000000000000000000001001100
	if k&540019712==536871936:
		bars.add(8)
		bars.add(9)
		bars.add(1)
		bars.add(3)
	if k&537657392==536870960:
		bars.add(2)
		bars.add(3)
		bars.add(10)
		bars.add(12)
	if k&536871116==536870988:
		bars.add(7)
		bars.add(9)
		bars.add(11)
		bars.add(12)

	#000000001000001100000000000000000000#gulgrøn
	#000000001000000011000000000000010000#gulblå
	#000000001000000000000000000000000100#grønblå
	if k&137366528==137363456:
		bars.add(2)
		bars.add(3)
		bars.add(10)
		bars.add(12)
	if k&135004208==135004176:
		bars.add(7)
		bars.add(9)
		bars.add(11)
		bars.add(12)
	if k&134217932==134217732:
		bars.add(8)
		bars.add(9)
		bars.add(1)
		bars.add(3)

	#000000010000000100000000110000000000#blågul
	#000000010000000001000000000000000000#blågrøn
	#000000010000000000000000000011000000#gulgrøn
	if k&271584256==269487104:
		bars.add(7)
		bars.add(9)
		bars.add(11)
		bars.add(12)
	if k&269221936==268697600:
		bars.add(8)
		bars.add(9)
		bars.add(1)
		bars.add(3)
	if k&268435660==268435648:
		bars.add(2)
		bars.add(3)
		bars.add(10)
		bars.add(12)
	#---
	#000000000100000000100000000100000000
	#000000000100000000000010000000000011
	#000000000100000000000000000001001100
	if k&67306240==67240192:
		bars.add(7)
		bars.add(8)
		bars.add(4)
		bars.add(5)
	if k&67121155==67117059:
		bars.add(5)
		bars.add(6)
		bars.add(10)
		bars.add(11)
	if k&67109068==67108940:
		bars.add(11)
		bars.add(12)
		bars.add(7)
		bars.add(9)

	#000000000001000000010000001100000000#blågul
	#000000000001000000000001000000000010#blårød
	#000000000001000000000000000011001000#gulrød
	if k&16974592==16843520:
		bars.add(11)
		bars.add(12)
		bars.add(7)
		bars.add(9)
	if k&16789507==16781314:
		bars.add(7)
		bars.add(8)
		bars.add(4)
		bars.add(5)
	if k&16777420==16777416:
		bars.add(5)
		bars.add(6)
		bars.add(10)
		bars.add(11)

	#000000000010000000110000001000000000#gulrød
	#000000000010000000000011000000000001#gulblå
	#000000000010000000000000000010000100# rød blå
	if k&33751808==33751552:
		bars.add(5)
		bars.add(6)
		bars.add(10)
		bars.add(11)
	if k&33566723==33566721:
		bars.add(11)
		bars.add(12)
		bars.add(7)
		bars.add(9)
	if k&33554636==33554564:
		bars.add(7)
		bars.add(8)
		bars.add(4)
		bars.add(5)
	return bars

# print(barcheck(start))

fast_lookup = {1:(39207357440,39191610368),2:(39204995120,39191609392),3:(39195511856,39191577648),
4:(38734643968,38721978624),5:(38722024195,38721954051),6:(38734458883,38721855491),
7:(34963915724,34963849548),8:(34967064320,34963850496),9:(34966867148,34963719244),
10:(4899745843,4898955315),11:(4898959567,4898955343),12:(4899733756,4898947196)}

def maskPerform(k,n):
    return k & fast_lookup[n][0] == fast_lookup[n][1]

def vBarSolve(pos,bars):
	res = fastVcheck(pos) # if there is a v, there is also a bar
	if res[0]:
		return [],0
	possmoves = ["U", "U'", "R", "R'", "L", "L'", "B","B'"]
	# possmoves = ["U", "U'"]
	visited = set()
	q = deque([(pos, [], 'k')])
	while q:
		s, path, last_move = q.popleft()
		if s not in visited:
			visited.add(s)
			for move in possmoves:
				if move[0] != last_move[0]:
					npos = mdic[move](s)
					#print(self.pos)
					newpath = deepcopy(path)
					newpath.append(move)
					for bar in bars:
						if maskPerform(npos,bar): 
							return newpath,bar
					q.append((npos,newpath,move))

def vBarDist(vdist):
	idx = 0
	overview = {}
	for i in range(8):
		overview[i] = defaultdict(set)
	# overview = [set(),set(),set(),set(),set(),set(),set(),set(),set(),set()]
	for idxx,positions in enumerate(vdist):
		for state in positions:
			bars = barcheck(state)
			if bars:
				sol,bar= vBarSolve(state,bars)
				overview[idxx][len(sol)].add(state)
			else:
				overview[idxx]['no bar'].add(state)
				# sol= vSolve(state)
			idx +=1
			if idx%5000 == 0:
				print(idx)
				for k in overview:
					for j in overview[k]:
						print(k,j,len(overview[k][j]))
	print("Final:")
	for k in overview:
		for j in overview[k]:
			print(k,j,len(overview[k][j]))
	return overview


# print(vSolve(start))
# print(vSolveLookup(start,{}))

dist = dist()

vdist = vDist(dist)

# joblib.dump(vdist,"pyra_v_dist.joblib")
# print("saved")

# vdist = joblib.load("pyra_v_dist.joblib")

vbars = vBarDist(vdist)

# joblib.dump(vbars,"pyra_bars_v_dist.joblib")
# print("saved")

# vbardist = joblib.load("pyra_bars_v_dist.joblib")

# for k in vbardist:
# 	for j in vbardist[k]:
# 		print(k,j,len(vbardist[k][j]))
