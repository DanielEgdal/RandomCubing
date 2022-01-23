from collections import deque
from copy import deepcopy

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
    #100100000100000000110011001100000011 38722024195
    #100100000100110000001111000000000011 38734458883
    #--- opp
    #100100000100000000101000000100000000 38721978624
    #100100000100000000100010000100000011 38721954051
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
    #100000100100000000100000000101001100 34963849548
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
        return ([],0)
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
                        return (newpath,0)
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

dist = dist()

en = vDist(dist)

