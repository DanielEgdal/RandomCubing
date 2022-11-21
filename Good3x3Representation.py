from collections import deque
import pickle
import os
# from copy import copy,deepcopy
starte = 407901468851537952
startc = 247132686368
solvedC = 247132686368
solvedE = 407901468851537952

def swap5(k, pos1, pos2):
	set1 =  (k >> pos1) & 31
	set2 =  (k >> pos2) & 31
	xor = (set1 ^ set2)
	xor = (xor << pos1) | (xor << pos2)
	return k ^ xor

def swap1(k, pos1, pos2):
	set1 =  (k >> pos1) & 1
	set2 =  (k >> pos2) & 1
	xor = (set1 ^ set2)
	xor = (xor << pos1) | (xor << pos2)
	return k ^ xor

def flipE(k,pos1,pos2,pos3,pos4):
    k ^= (1 << pos1 | 1 << pos2 | 1 << pos3 | 1 << pos4)
    return k

def twistCornerC(k,pos1):
    u = k >> pos1
    c = u & 3
    t = c + 3
    c = (t - ((t & 2)>>1)) & 3
    suffix = k & ((2**(pos1)) -1) 
    n = ((((u >> 2) << 2) + c) << (pos1)) + suffix
    return n

def twistCorner(k,pos1):
    u = k >> pos1
    c = u & 3
    c = (c + 1 + ((c & 2)>>1)) & 3
    suffix = k & ((2**(pos1)) -1) 
    n = ((((u >> 2) << 2) + c) << (pos1)) + suffix
    return n

def R(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,10,20),0,30),10,30)
    c =  twistCornerC(c,3)
    c =  twistCorner(c,13)
    c =  twistCornerC(c,23)
    c =  twistCorner(c,33)

    # Edges
    e = swap5(swap5(swap5(e,10,30),25,50),10,50)
    # Edge flipping not needed
    return c,e

def Rp(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,10,20),0,30),20,0)
    c =  twistCornerC(c,3)
    c =  twistCorner(c,13)
    c =  twistCornerC(c,23)
    c =  twistCorner(c,33)

    # Edges
    e = swap5(swap5(swap5(e,10,30),25,50),30,25)
    # Edge flipping not needed
    return c,e

def R2(c,e):
    # Corners
    c =  swap5(swap5(c,10,30),0,20)
    # Corner twisting not needed

    # Edges
    e = swap5(swap5(e,10,50),30,25)
    # Edge flipping not needed
    return c,e

def U(c,e):
    c =  swap5(swap5(swap5(c,20,25),30,35),20,35)
    # Corner twisting not needed
    e =  swap5(swap5(swap5(e,40,45),55,50),40,55)
    # Edge flipping not needed
    return c,e

def Up(c,e):
    c =  swap5(swap5(swap5(c,20,25),30,35),25,30)
    # Corner twisting not needed
    e =  swap5(swap5(swap5(e,40,45),55,50),45,50)
    # Edge flipping not needed
    return c,e

def U2(c,e):
    c =  swap5(swap5(c,20,35),30,25)
    # Corner twisting not needed
    e =  swap5(swap5(e,40,55),45,50)
    # Edge flipping not needed
    return c,e

def D(c,e):
    c =  swap5(swap5(swap5(c,0,5),10,15),0,15)
    # Corner twisting not needed
    e =  swap5(swap5(swap5(e,0,5),10,15),0,15)
    # Edge flipping not needed
    return c,e

def Dp(c,e):
    c =  swap5(swap5(swap5(c,0,5),10,15),5,10)
    # Corner twisting not needed
    e =  swap5(swap5(swap5(e,0,5),10,15),5,10)
    # Edge flipping not needed
    return c,e

def D2(c,e):
    c =  swap5(swap5(c,0,15),5,10)
    # Corner twisting not needed
    e =  swap5(swap5(e,0,15),5,10)
    # Edge flipping not needed
    return c,e

def F(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,10,15),25,20),10,25)
    c =  twistCorner(c,23)
    c =  twistCornerC(c,13)
    c =  twistCorner(c,18)
    c =  twistCornerC(c,28)

    # Edges
    e = swap5(swap5(swap5(e,15,35),30,40),40,15)
    e = flipE(e,19,34,39,44)
    return c,e

def Fp(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,10,15),25,20),15,20)
    c =  twistCorner(c,23)
    c =  twistCornerC(c,13)
    c =  twistCorner(c,18)
    c =  twistCornerC(c,28)

    # Edges
    e = swap5(swap5(swap5(e,15,35),30,40),30,35)
    e = flipE(e,19,34,39,44)
    return c,e

def F2(c,e):
    # Corners
    c =  swap5(swap5(c,20,15),25,10)

    # Edges
    e = swap5(swap5(e,15,40),30,35)
    return c,e

def L(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,35,25),15,5),15,35)
    c =  twistCorner(c,8)
    c =  twistCornerC(c,18)
    c =  twistCorner(c,28)
    c =  twistCornerC(c,38)
    # Edges

    e = swap5(swap5(swap5(e,35,5),45,20),35,20)
    # no edge flips
    return c,e

def Lp(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,35,25),15,5),5,25)
    c =  twistCorner(c,8)
    c =  twistCornerC(c,18)
    c =  twistCorner(c,28)
    c =  twistCornerC(c,38)
    # Edges

    e = swap5(swap5(swap5(e,35,5),45,20),5,45)
    # no edge flips
    return c,e

def L2(c,e):
    # Corners
    c = swap5(swap5(c,35,15),25,5)
    # Edges

    e = swap5(swap5(e,45,5),35,20)
    # no edge flips
    return c,e

def B(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,35,30),0,5),30,5)
    c =  twistCornerC(c,8)
    c =  twistCorner(c,3)
    c =  twistCornerC(c,33)
    c =  twistCorner(c,38)
    # Edges

    e = swap5(swap5(swap5(e,25,55),0,20),25,20)
    e = flipE(e,4,24,29,59)
    return c,e

def Bp(c,e):
    # Corners
    c =  swap5(swap5(swap5(c,35,30),0,5),35,0)
    c =  twistCornerC(c,8)
    c =  twistCorner(c,3)
    c =  twistCornerC(c,33)
    c =  twistCorner(c,38)
    # Edges

    e = swap5(swap5(swap5(e,25,55),0,20),55,0)
    e = flipE(e,4,24,29,59)
    return c,e

def B2(c,e):
    # Corners
    c =  swap5(swap5(c,30,5),35,0)
    # Edges

    e = swap5(swap5(e,25,20),55,0)
    # no edge flips
    return c,e

def printbin(c,e):
    ie = []
    ic = []
    cp = format(c,'b')
    ep = format(e,'b')
    while len(cp) < 40:
        cp = '0'+cp

    while len(ep) < 60:
        ep = '0'+ep
    
    # co = 7
    for j in range(0,40,5):
        # print("place",co,"has",int(cp[j+2:j+5],2))
        # co-=1
        # Corner orientation 1 = has been turned once clockwise. 2, has been turned two times (i.e. do it once more and you have co)
        ic.append((int(cp[j:j+2],2),int(cp[j+2:j+5],2)))
    print(ic)
    # eo = 11
    for j in range(0,60,5):
        # print("place",eo,"has",int(ep[j+1:j+5],2))
        # eo-=1
        ie.append((int(ep[j:j+1],2),int(ep[j+1:j+5],2)))
    print(ie)

def checkEO(e):
    # Prints False if there is EO solved, else the state of EO
    # poss = [4, 9, 14,19,24,29,34,39,44,49,54,59]
    # k = 0
    # for pos in poss:
    #     k |= 1 << pos
    eoState = e & 595056260442243600
    if not eoState:
        return False
    else:
        return eoState

def checkDRBad(c,e):
    drCornerCheck = 851234808600
    cornerState = c & drCornerCheck # If this is 0, the corners are solved
    if not cornerState:
        piece1 = ((e >> 20) & 15)
        if piece1 > 3 and piece1 < 8:
            piece2 = ((e >> 25) & 15)
            if piece2 > 3 and piece2 < 8:
                piece3 = ((e >> 30) & 15)
                if piece3 > 3 and piece3 < 8:
                    piece4 = ((e >> 35) & 15)
                    if piece4 > 3 and piece4 < 8:
                        return True
    return False

def checkDR(c,e):
    # poss = [3, 8, 13,18,23,28,33,38]
    # k = 0
    # for pos in poss:
    #     k |= 3 << pos
    cornerState = c & 851234808600 # If this is 0, the corners are solved
    if (not cornerState) and e == 532021248000:
        return True
    return False

def solveDR(c,e,oScramble,eoSol):
    e = 532021248000 
    c = 248276819175
    for move in oScramble: # Re do the corners and edges in a state where A) it can be checked faster
        c,e = mdic[move](c,e)
    for move in eoSol: # And B) where the equivalent state for this step is not checked multiple times
        c,e = mdic[move](c,e)

    if checkDR(c,e):
        return []
    else:
        moves = ["R","R'","R2","U","U'","U2","F2","B2","D","D2","D'","L","L2","L'"]
        q = deque([(c,e,[])])
        visited = set()
        while q:
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                if checkDR(_c,_e):
                    return l+[move]
                else:
                    if (_c,_e) not in visited:
                        q.append((_c,_e,l+[move]))
                        visited.add((_c,_e))

def checkHTRBad(c,e):
    if e & 15 in {0,3,8,11}:
        if (e >> 15) & 15 in {0,3,8,11}:
            if (e >> 40) & 15 in {0,3,8,11}:
                if (e >> 55) & 15 in {0,3,8,11}: # Done edges
                    if c & 7 in {0,3,4,7}:
                        if (c>>15) & 7 in {0,3,4,7}:
                            if (c>>20) & 7 in {0,3,4,7}:
                                if (c>>35) & 7 in {0,3,4,7}: # Done corner
                                    if notFakeHTR(c,e):
                                        return True
    return False

def notFakeHTR(c,e):
    moves = ["R2","L2","F2","D2","B2","U2"]
    q = deque([(c,e,[])])
    while q:
        c,e,l = q.popleft()
        for move in moves:
            _c,_e= mdic[move](c,e)
            if _c == solvedC:
                return True
            elif len(l) < 4:
                q.append((_c,_e,l+[move]))
    return False

def solveEO(c,e):
    if not checkEO(e):
        return []
    else:
        moves = ["R","R'","R2","U","U'","U2","F","F'","F2","D","D2","D'","L","L2","L'","B","B2","B'"]
        q = deque([(c,e,[])])
        visited = set()
        while q:
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                eoState = checkEO(_e)
                if not eoState:
                    return l+[move]
                else:
                    if eoState not in visited:
                        q.append((_c,_e,l+[move]))
                        visited.add(eoState)

def solveDRBad(c,e):
    if checkDRBad(c,e):
        return []
    else:
        moves = ["R","R'","R2","U","U'","U2","F2","B2","D","D2","D'","L","L2","L'"]
        q = deque([(c,e,[])])
        visited = set()
        while q:
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                if checkDR(_c,_e):
                    return l+[move]
                else:
                    if (_c,_e) not in visited:
                        q.append((_c,_e,l+[move]))
                        visited.add((_c,_e))

def solveHTRBad(c,e):
    if checkHTRBad(c,e):
        return []
    else:
        moves = ["R2","U","U'","U2","F2","B2","D","D2","D'","L2"]
        q = deque([(c,e,[])])
        visited = set()
        while q:
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                if checkHTRBad(_c,_e):
                    return l+[move]
                else:
                    if (_c,_e) not in visited:
                        q.append((_c,_e,l+[move]))
                        visited.add((_c,_e))

def checkHTR(c,e,l,oc,oe):
    # poss = [1, 16, 21,36]
    # k = 0
    # for pos in poss:
    #     k |= 1 << pos

    # poss = [1, 16, 41,56]
    # k = 0
    # for pos in poss:
    #     k |= 1 << pos

    if (c & 68721639426) == 68721639426 and (e & 72060325082497026) == 72060325082497026:
        
        for move in l:
            oc,oe = mdic[move](oc,oe)
        # printbin(oc,oe)
        if notFakeHTR(oc,oe):
            return True
    return False

def solveHTR(c,e,oScramble,eoSol,drSol,oc,oe):
    e = 109251305892020226 
    c = 108455333922
    for move in oScramble: # Re do the corners and edges in a state where A) it can be checked faster
        c,e = mdic[move](c,e)
    for move in eoSol: # And B) where the equivalent state for this step is not checked multiple times
        c,e = mdic[move](c,e)
    for move in drSol: 
        c,e = mdic[move](c,e)
    if checkHTR(c,e,[],oc,oe):
        return []
    else:
        moves = ["R2","U","U'","U2","F2","B2","D","D2","D'","L2"]
        q = deque([(c,e,[])])
        visited = set()
        cc = 0
        while q:
            # cc+=1
            # print(cc)
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                if checkHTR(_c,_e,l+[move],oc,oe):
                    return l+[move]
                else:
                    if (_c,_e) not in visited:
                        q.append((_c,_e,l+[move]))
                        visited.add((_c,_e))


def solveFromHTR(c,e):
    if c == solvedC and e == solvedE:
        return []
    else:
        moves = ["R2","U2","F2","B2","D2","L2"]
        q = deque([(c,e,[])])
        visited = set()
        while q:
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                if _c == solvedC and _e == solvedE:
                    return l+[move]
                else:
                    if (_c,_e) not in visited:
                        q.append((_c,_e,l+[move]))
                        visited.add((_c,_e))

def getFromDRPrune():
    c = 247132686368
    e = 407901468851537952
    moves = ["R2","U","U'","U2","F2","B2","D","D2","D'","L2"]
    q = deque([(c,e,[])])
    distt = {(c,e):[]}
    # i = 0
    continuee = 1
    while q and continuee:
        i+=1
        c,e,l = q.popleft()
        for move in moves:
            _c,_e= mdic[move](c,e)
            nyL = l+[move]
            if (_c,_e) not in distt:
                q.append((_c,_e,nyL))
                distt[(_c,_e)] = nyL
            if len(nyL) > 7:
                continuee = 0
        # if i%100000 == 0:
        #     print(i,len(nyL))
    return distt

def mk_inv(li): # Invert alg
    inverted = []
    for trigger in li[::-1]:
        if len(trigger)== 3:
            inverted.append(trigger[:2])
        elif trigger[-1] == "'":
            inverted.append(trigger[0])
        elif trigger[-1] == '2':
            inverted.append(trigger)
        else:
            inverted.append(f"{trigger}'")
    return inverted

def solveFromDRFast(c,e):
    if c==solvedC and e == solvedE:
        return []
    else:
        if os.path.exists('fromDRPrune.pickle'):
            with open('fromDRPrune.pickle','rb') as f:
                disst = pickle.load(f)
        else:
            print('first time, genning prune table to finish the cube. Should take like 5 sec with pypy')
            disst =getFromDRPrune()
            with open('fromDRPrune.pickle','wb') as f:
                pickle.dump(disst,f)
        moves = ["R2","U","U'","U2","F2","B2","D","D2","D'","L2"]
        q = deque([(c,e,[])])
        visited = set()
        cc = 0
        while q:
            # cc+=1
            # print(cc)
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                if (_c,_e) in disst:
                    return  l+[move]+ mk_inv(disst[(_c,_e)])
                else:
                    if (_c,_e) not in visited:
                        q.append((_c,_e,l+[move]))
                        visited.add((_c,_e))


# printbin(startc,starte)

# startc,starte = R(startc,starte)
# print(checkDR(startc,starte))

# scramble = "D B D' L2 F2 L2 F2 U' F2 U' L2 B2 U F2 L B' D' R2 D2 F' D".split(' ')
scramble = "B2 R2 U2 B D2 B D2 R2 D2 R2 F' U2 R F2 D B U B U2 F U2".split(' ')
mdic = {"R":R,"R'":Rp,"R2'":R2,"R2":R2,"U":U,"U'":Up,"U2":U2,"D":D,"D'":Dp,"D2":D2,"F":F,"F'":Fp,"F2":F2,"U2'":U2,"B":B,"B'":Bp,"B2":B2,"L":L,"L2":L2,"L'":Lp}

# for i in range(1000000):
for move in scramble:
    startc,starte = mdic[move](startc,starte)

# print(checkDR(startc,starte))
# print(checkEO(starte))

def solveScramble(scramble):
    starte = 407901468851537952
    startc = 247132686368
    print(scramble)
    scramble = scramble.split(' ')
    for move in scramble:
        startc,starte = mdic[move](startc,starte)

    eoSol = solveEO(startc,starte)
    print("EO:",end='\t')
    for move in eoSol:
        print(move,end=' ')
        startc,starte = mdic[move](startc,starte)
    print('')
    # drSol = solveDR(startc,starte)
    drSol = solveDR(startc,starte,scramble,eoSol)
    print("DR:",end='\t')
    for move in drSol:
        print(move,end=' ')
        startc,starte = mdic[move](startc,starte)
    print('')
    # htrSol = solveHTR(startc,starte)
    htrSol = solveHTR(startc,starte,scramble,eoSol,drSol,startc,starte)
    # htrSol = solveHTRBad(startc,starte)
    print("HTR:", end='\t')
    for move in htrSol:
        print(move,end=' ')
        startc,starte = mdic[move](startc,starte)
    print('')
    finalSol = solveFromHTR(startc,starte)
    print("Finish:", end='\t')
    for move in finalSol:
        print(move,end=' ')
    print('')
    print(f"Solution length:\t{len(eoSol)+len(drSol)+len(htrSol)+len(finalSol)}")

def solveScrambleFast(scramble):
    starte = 407901468851537952
    startc = 247132686368
    print(scramble)
    scramble = scramble.split(' ')
    for move in scramble:
        startc,starte = mdic[move](startc,starte)

    eoSol = solveEO(startc,starte)
    print("EO:",end='\t')
    for move in eoSol:
        print(move,end=' ')
        startc,starte = mdic[move](startc,starte)
    print('')
    # drSol = solveDR(startc,starte)
    drSol = solveDR(startc,starte,scramble,eoSol)
    print("DR:",end='\t')
    for move in drSol:
        print(move,end=' ')
        startc,starte = mdic[move](startc,starte)
    print('')
    # htrSol = solveHTR(startc,starte)
    finalSol = solveFromDRFast(startc,starte)
    # htrSol = solveHTRBad(startc,starte)
    print("Finish:", end='\t')
    for move in finalSol:
        print(move,end=' ')
    print('')
    print(f"Solution length:\t{len(eoSol)+len(drSol)+len(finalSol)}")
    

# sloww = "F2 L D2 L' F2 L' F2 D2 R2 B2 D2 R B' U' F2 L R2 B R2 F2 R2"

# solveScramble("B U2 B D2 L2 D2 F2 U2 F' D2 R2 U' R' U' L' D' B2 F R B D'")
solveScrambleFast("F2 L D2 L' F2 L' F2 D2 R2 B2 D2 R B' U' F2 L R2 B R2 F2 R2")


