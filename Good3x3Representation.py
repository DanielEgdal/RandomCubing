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

def twistCorner(k):
    u = k & 24
    o = (u+8+((u&16)>>1))&24
    return o + (k&7)

def twistCornerC(k):
    u = k & 24
    t = u + 24
    o = (t - ((t & 16)>>1)) & 24
    return o + (k&7)

# @profile
def R(c,e):

    block1 = twistCornerC((c >> 10) & 31)
    block2 = twistCorner((c >> 20) & 31)
    block3 = twistCornerC((c >> 30) & 31)
    block4 = twistCorner((c) & 31)
    c = c & 35151053554656
    c = c ^ ((block1 << 20) | (block2 << 30) |(block3) |(block4 << 10))

    block1 = (e >> 10) & 31
    block2 = (e >> 25) & 31
    block3 = (e >> 30) & 31
    block4 = (e >> 50) & 31
    e = e & 1118018573168509951
    e = e ^ ((block1 << 30) | (block2 << 10) |(block3 << 50) |(block4 << 25))

    return c,e

def Rp(c,e):
    # Corners
    block1 = twistCornerC((c >> 10) & 31)
    block2 = twistCorner((c >> 20) & 31)
    block3 = twistCornerC((c >> 30) & 31)
    block4 = twistCorner((c) & 31)
    c = c & 35151053554656
    c = c ^ ((block1) | (block2 << 10) |(block3 << 20) |(block4 << 30))

    block1 = (e >> 10) & 31
    block2 = (e >> 25) & 31
    block3 = (e >> 30) & 31
    block4 = (e >> 50) & 31
    e = e & 1118018573168509951
    e = e ^ ((block1 << 25) | (block2 << 50) |(block3 << 10) |(block4 << 30))
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

    block1 = (c >> 20) & 31
    block2 = (c >> 25) & 31
    block3 = (c >> 30) & 31
    block4 = (c >> 35) & 31

    c = c & 34084861509631
    c = c ^ ((block1 << 25) | (block2 << 35) |(block3 << 20 ) |(block4 << 30))

    block1 = (e >> 40) & 31
    block2 = (e >> 45) & 31
    block3 = (e >> 50) & 31
    block4 = (e >> 55) & 31
    e = e & 1099511627775
    e = e ^ ((block1 << 45) | (block2 << 55) |(block3 << 40) |(block4 << 50))
    return c,e

def Up(c,e):
    block1 = (c >> 20) & 31
    block2 = (c >> 25) & 31
    block3 = (c >> 30) & 31
    block4 = (c >> 35) & 31

    c = c & 34084861509631
    c = c ^ ((block1 << 30) | (block2 << 20) |(block3 << 35 ) |(block4 << 25))

    block1 = (e >> 40) & 31
    block2 = (e >> 45) & 31
    block3 = (e >> 50) & 31
    block4 = (e >> 55) & 31
    e = e & 1099511627775
    e = e ^ ((block1 << 50) | (block2 << 40) |(block3 << 55) |(block4 << 45))
    return c,e

def U2(c,e):
    c =  swap5(swap5(c,20,35),30,25)
    # Corner twisting not needed
    e =  swap5(swap5(e,40,55),45,50)
    # Edge flipping not needed
    return c,e

def D(c,e):

    block1 = (c) & 31
    block2 = (c >> 5) & 31
    block3 = (c >> 10) & 31
    block4 = (c >> 15) & 31

    c = c & 35184371040256
    c = c ^ ((block1 << 5) | (block2 << 15) |(block3) |(block4 << 10))

    block1 = (e) & 31
    block2 = (e >> 5) & 31
    block3 = (e >> 10) & 31
    block4 = (e >> 15) & 31
    e = e & 1152921504605798400
    e = e ^ ((block1 << 5) | (block2 << 15) |(block3) |(block4 << 10))
    return c,e

def Dp(c,e):
    block1 = (c) & 31
    block2 = (c >> 5) & 31
    block3 = (c >> 10) & 31
    block4 = (c >> 15) & 31

    c = c & 35184371040256
    c = c ^ ((block1 << 10) | (block2) |(block3 << 15) |(block4 << 5))

    block1 = (e) & 31
    block2 = (e >> 5) & 31
    block3 = (e >> 10) & 31
    block4 = (e >> 15) & 31
    e = e & 1152921504605798400
    e = e ^ ((block1 << 10) | (block2) |(block3 << 15) |(block4 << 5))
    return c,e

def D2(c,e):
    c =  swap5(swap5(c,0,15),5,10)
    # Corner twisting not needed
    e =  swap5(swap5(e,0,15),5,10)
    # Edge flipping not needed
    return c,e

def F(c,e):
    # Corners

    block1 = twistCorner((c >> 10) & 31)
    block2 = twistCornerC((c >> 15) & 31)
    block3 = twistCornerC((c >> 20) & 31)
    block4 = twistCorner((c >> 25) & 31)
    c = c & 35183298348031
    c = c ^ ((block1 << 15) | (block2 << 25) |(block3 << 10) |(block4 << 20))

    block1 = ((e >> 15) & 31)^16
    block2 = ((e >> 30) & 31) ^16
    block3 = ((e >> 35) & 31) ^16
    block4 = ((e >> 40) & 31) ^16
    e = e & 1152886321307484159
    e = e ^ ((block1 << 35) | (block2 << 15) |(block3 << 40) |(block4 << 30))

    return c,e

def Fp(c,e):
    # Corners
    block1 = twistCorner((c >> 10) & 31)
    block2 = twistCornerC((c >> 15) & 31)
    block3 = twistCornerC((c >> 20) & 31)
    block4 = twistCorner((c >> 25) & 31)
    c = c & 35183298348031
    c = c ^ ((block1 << 20) | (block2 << 10) |(block3 << 25) |(block4 << 15))

    block1 = ((e >> 15) & 31)^16
    block2 = ((e >> 30) & 31) ^16
    block3 = ((e >> 35) & 31) ^16
    block4 = ((e >> 40) & 31) ^16
    e = e & 1152886321307484159
    e = e ^ ((block1 << 30) | (block2 << 40) |(block3 << 15) |(block4 << 35))
    return c,e

def F2(c,e):
    # Corners
    c =  swap5(swap5(c,20,15),25,10)

    # Edges
    e = swap5(swap5(e,15,40),30,35)
    return c,e

def L(c,e):
    block1 = twistCornerC((c >> 5) & 31)
    block2 = twistCorner((c >> 15) & 31)
    block3 = twistCornerC((c >> 25) & 31)
    block4 = twistCorner((c >>35) & 31)
    c = c & 34118178995231
    c = c ^ ((block1 << 35) | (block2 << 5) |(block3 << 15) |(block4 << 25))

    block1 = (e >> 5) & 31
    block2 = (e >> 20) & 31
    block3 = (e >> 35) & 31
    block4 = (e >> 45) & 31
    e = e & 1151829723887696927
    e = e ^ ((block1 << 20) | (block2 << 45) |(block3 << 5) |(block4 << 35))

    return c,e


def Lp(c,e):
    block1 = twistCornerC((c >> 5) & 31)
    block2 = twistCorner((c >> 15) & 31)
    block3 = twistCornerC((c >> 25) & 31)
    block4 = twistCorner((c >>35) & 31)
    c = c & 34118178995231
    c = c ^ ((block1 << 15) | (block2 << 25) |(block3 << 35) |(block4 << 5))

    block1 = (e >> 5) & 31
    block2 = (e >> 20) & 31
    block3 = (e >> 35) & 31
    block4 = (e >> 45) & 31
    e = e & 1151829723887696927
    e = e ^ ((block1 << 35) | (block2 << 5) |(block3 << 45) |(block4 << 20))

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
    block1 = twistCornerC((c) & 31)
    block2 = twistCorner((c >> 5) & 31)
    block3 = twistCorner((c >> 30) & 31)
    block4 = twistCornerC((c >> 35) & 31)
    c = c & 34085934201856
    c = c ^ ((block1 << 30) | (block2) |(block3 << 35) |(block4 << 5))

    block1 = ((e) & 31)^16
    block2 = ((e >> 20) & 31) ^16
    block3 = ((e >> 25) & 31) ^16
    block4 = ((e >> 55) & 31) ^16
    e = e & 36028795946270688
    e = e ^ ((block1 << 25) | (block2) |(block3 << 55) |(block4 << 20))
    return c,e

def Bp(c,e):
    block1 = twistCornerC((c) & 31)
    block2 = twistCorner((c >> 5) & 31)
    block3 = twistCorner((c >> 30) & 31)
    block4 = twistCornerC((c >> 35) & 31)
    c = c & 34085934201856
    c = c ^ ((block1 << 5) | (block2 << 35) |(block3 ) |(block4 << 30))

    block1 = ((e) & 31)^16
    block2 = ((e >> 20) & 31) ^16
    block3 = ((e >> 25) & 31) ^16
    block4 = ((e >> 55) & 31) ^16
    e = e & 36028795946270688
    e = e ^ ((block1 << 20) | (block2 << 55) |(block3) |(block4 << 25))
    return c,e

def B2(c,e):
    # Corners
    c =  swap5(swap5(c,30,5),35,0)
    # Edges

    e = swap5(swap5(e,25,20),55,0)
    # no edge flips
    return c,e

def printbin(c,e):
    print("printbin")
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

# @profile
def solveEO(c,e):
    if not checkEO(e):
        return []
    else:
        moves = ["R","R'","R2","U","U'","U2","F","F'","F2","D","D2","D'","L","L2","L'","B","B2","B'"]
        # moves = [R,Rp,R2,U,Up,U2,F,Fp,F2,D,Dp,D2,L,Lp,L2,B,Bp,B2]
        q = deque([(c,e,[])])
        visited = set()
        while q:
            c,e,l = q.popleft()
            for move in moves:
                _c,_e= mdic[move](c,e)
                # _c,_e = move(c,e)
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
        # i+=1
        c,e,l = q.popleft()
        for move in moves:
            _c,_e= mdic[move](c,e)
            nyL = l+[move]
            if (_c,_e) not in distt:
                q.append((_c,_e,nyL))
                distt[(_c,_e)] = nyL
            if len(nyL) > 7: # 7 is fastest when looking at both running and loading
                continuee = 0
        # if i%100000 == 0:
        #     print(i,len(nyL))
    return distt

def getFromEOToDRPrune():
    e = 532021248000 
    c = 248276819175
    moves = ["R","R'","R2","U","U'","U2","F2","B2","D","D2","D'","L","L2","L'"]
    q = deque([(c,e,[])])
    distt = {(c,e):[]}
    # i = 0
    continuee = 1
    while q and continuee:
        # i+=1
        c,e,l = q.popleft()
        for move in moves:
            _c,_e= mdic[move](c,e)
            nyL = l+[move]
            if (_c,_e) not in distt:
                q.append((_c,_e,nyL))
                distt[(_c,_e)] = nyL
            if len(nyL) > 7: # 7 is faster because of loading in later
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

def solveFromDRFast(c,e,given=False):
    if c==solvedC and e == solvedE:
        return []
    else:
        if not given:
            if os.path.exists('fromDRPrune.pickle'):
                with open('fromDRPrune.pickle','rb') as f:
                    disst = pickle.load(f)
            else:
                print('first time, genning prune table to finish the cube. Should take like 5 sec with pypy')
                disst =getFromDRPrune()
                with open('fromDRPrune.pickle','wb') as f:
                    pickle.dump(disst,f)
        else:
            disst = given
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

def EOToDR(c,e,oScramble,eoSol,*,partialStep=False,given=False):
    e = 532021248000 
    c = 248276819175
    for move in oScramble: # Re do the corners and edges in a state where A) it can be checked faster
        c,e = mdic[move](c,e)
    for move in eoSol: # And B) where the equivalent state for this step is not checked multiple times
        c,e = mdic[move](c,e)

    if partialStep:
        for move in partialStep: # Done if you want to make a step before to make it more human findable
            c,e = mdic[move](c,e)

    if not given:
        if os.path.exists('fromEOToDRPrune.pickle'):
            with open('fromEOToDRPrune.pickle','rb') as f:
                disst = pickle.load(f)
        else:
            print('first time, genning prune table to get EO -> DR. Should take like 5 sec with pypy')
            disst =getFromEOToDRPrune()
            with open('fromEOToDRPrune.pickle','wb') as f:
                pickle.dump(disst,f)
    else:
        disst = given
    
    if (c,e) in disst:
        return mk_inv(disst[(c,e)])
    moves = ["R","R'","R2","U","U'","U2","F2","B2","D","D2","D'","L","L2","L'"]
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

def Human1DR(c,e,oScramble,eoSol):
    e = 532021248000 
    c = 248276819175
    for move in oScramble: # Re do the corners and edges in a state where A) it can be checked faster
        c,e = mdic[move](c,e)
    for move in eoSol: # And B) where the equivalent state for this step is not checked multiple times
        c,e = mdic[move](c,e)

    if checkHuman1DR(c,e):
        return []
    moves = ["R","R'","R2","U","U'","U2","F2","B2","D","D2","D'","L","L2","L'"]
    q = deque([(c,e,[])])
    visited = set()
    cc = 0
    while q:
        # cc+=1
        # print(cc)
        c,e,l = q.popleft()
        for move in moves:
            _c,_e= mdic[move](c,e)
            if checkHuman1DR(_c,_e):
                return  l+[move]
            else:
                if (_c,_e) not in visited:
                    q.append((_c,_e,l+[move]))
                    visited.add((_c,_e))

def checkHuman1DR(c,e):
    # poss = [3, 8, 13,18,23,28,33,38]
    # k = 0
    # for pos in poss:
    #     k |= 3 << pos
    co = cornersHuman1Dr(c)
    eo = edgesHuman1DR(e)
    if (co == 4 and eo in {2,4}) or (co == 3 and eo == 3):
        return True
    else:
        return False

def cornersHuman1Dr(c):
    o = 0
    for i in range(3,40,5):
        if (c >> i) & 3 > 0:
            continue
        o += 1
    return o

def edgesHuman1DR(e):
    o = 0
    for i in range(20,39,5):
        if (e >> i) & 15 == 15:
            continue
        o += 1
    return o

# printbin(startc,starte)

# startc,starte = R(startc,starte)
# print(checkDR(startc,starte))

scramble = "U R2 F B R B2 R U2 L B2 R U' D' R2 F R' L B2 U2 F2".split(' ')
# scramble = "F R D2 U2 R D2 R2 F2 L' U2 R' D2 B' R2 F R2 F' D' U2".split(' ')
mdic = {"R":R,"R'":Rp,"R2'":R2,"R2":R2,"U":U,"U'":Up,"U2":U2,"D":D,"D'":Dp,"D2":D2,"F":F,"F'":Fp,"F2":F2,"U2'":U2,"B":B,"B'":Bp,"B2":B2,"L":L,"L2":L2,"L'":Lp}

starte = 407901468851537952
startc = 247132686368

# printbin(startc,starte)

# startc,starte = mdic["B'"](startc,starte)

# for i in range(10_000_000):
for move in scramble:
    startc,starte = mdic[move](startc,starte)
    # print(move,startc,starte)

# from line_profiler import LineProfiler
# lp = LineProfiler()
# lp_wrapper = lp(solveEO)
# lp_wrapper([(startc,starte)])
for i in range(100):
    j = solveEO(startc,starte)
# print(j)
# lp_wrapper.print_stats()
#             # print(startc,starte,move)
# print(startc,starte)
# printbin(startc,starte)
# for i in range(1000):
#     oos = solveEO(startc,starte)
# print(oos)
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


def zScramble(scramble):
    # Z rotation, scramble pre split
    newScramble = []
    for move in scramble:
        # print(move)
        if move[0] == 'R':
            newScramble.append("U"+move[1:])
        elif move[0] == 'L':
            newScramble.append("D"+move[1:])
        elif move[0] == 'U':
            newScramble.append("L"+move[1:])
        elif move[0] == 'D':
            newScramble.append("R"+move[1:])
        else:
            newScramble.append(move)
    return newScramble

def yScramble(scramble):
    # y rotation, scramble pre split
    newScramble = []
    for move in scramble:
        # print(move)
        if move[0] == 'R':
            newScramble.append("B"+move[1:])
        elif move[0] == 'L':
            newScramble.append("F"+move[1:])
        elif move[0] == 'F':
            newScramble.append("R"+move[1:])
        elif move[0] == 'B':
            newScramble.append("L"+move[1:])
        else:
            newScramble.append(move)
    return newScramble

def zpScramble(scramble):
    newScramble = []
    for move in scramble:
        # print(move)
        if move[0] == 'R':
            newScramble.append("D"+move[1:])
        elif move[0] == 'L':
            newScramble.append("U"+move[1:])
        elif move[0] == 'U':
            newScramble.append("R"+move[1:])
        elif move[0] == 'D':
            newScramble.append("L"+move[1:])
        else:
            newScramble.append(move)
    return newScramble

def ypScramble(scramble):
    newScramble = []
    for move in scramble:
        # print(move)
        if move[0] == 'R':
            newScramble.append("F"+move[1:])
        elif move[0] == 'L':
            newScramble.append("B"+move[1:])
        elif move[0] == 'F':
            newScramble.append("L"+move[1:])
        elif move[0] == 'B':
            newScramble.append("R"+move[1:])
        else:
            newScramble.append(move)
    return newScramble

def rotatedScrambles(scramble):
    from copy import copy
    scrambles = [scramble]
    rots = {'z':zScramble,'y':yScramble}
    reverse = [[]]
    for posDr in [['z'],['y'],['y','z'],['z','y'],['z','y','z']]:
        tempScramble = copy(scramble)
        tempReverse = []
        for rot in posDr:
            tempScramble = rots[rot](tempScramble)
            tempReverse.append(rot)
        scrambles.append(tempScramble)
        reverse.append(tempReverse)
    return scrambles,reverse

def doReverseRotate(sol,rotations):
    rots = {'z':zpScramble,'y':ypScramble}
    if rotations:
        for rot in rotations[::-1]:
            sol = rots[rot](sol)
    
    return sol

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
    # drSol = solveDR(startc,starte,scramble,eoSol)
    drSol = EOToDR(startc,starte,scramble,eoSol)
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
    

def solveScrambleAllDRAxis(scramble):
    print("Scramble:",scramble)
    scramble = scramble.split(' ')
    scrambleList,reversing = rotatedScrambles(scramble)
    # Prune to finish cube
    if os.path.exists('fromDRPrune.pickle'):
        with open('fromDRPrune.pickle','rb') as f:
            fromDRPrune = pickle.load(f)
    else:
        print('first time, genning prune table to finish the cube. Should take like 5 sec with pypy')
        fromDRPrune =getFromDRPrune()
        with open('fromDRPrune.pickle','wb') as f:
            pickle.dump(fromDRPrune,f)

    # Prune to fast DR
    if os.path.exists('fromEOToDRPrune.pickle'):
        with open('fromEOToDRPrune.pickle','rb') as f:
            fromEOToDRPrune = pickle.load(f)
    else:
        print('first time, genning prune table to get EO -> DR. Should take like 5 sec with pypy')
        fromEOToDRPrune =getFromEOToDRPrune()
        with open('fromEOToDRPrune.pickle','wb') as f:
            pickle.dump(fromEOToDRPrune,f)
    
    for scramble,rev in zip(scrambleList,reversing):
        print(f"Solving for axis {rev}")
        starte = 407901468851537952
        startc = 247132686368
        for move in scramble:
            startc,starte = mdic[move](startc,starte)
        # print(startc,starte)
        # printbin(startc,starte)
        eoSol = solveEO(startc,starte)
        print("EO:",end='\t')
        eoSolPrint = doReverseRotate(eoSol,rev)
        for move in eoSolPrint:
            print(move,end=' ')
        for move in eoSol:
            startc,starte = mdic[move](startc,starte)
        print(f'\t{len(eoSol)}')
        drSol = EOToDR(startc,starte,scramble,eoSol,given=fromEOToDRPrune)
        drSolPrint = doReverseRotate(drSol,rev)

        print("DR:",end='\t')
        for move in drSolPrint:
            print(move,end=' ')
        for move in drSol:
            startc,starte = mdic[move](startc,starte)
        print(f'\t{len(drSolPrint)}')
        
        finalSol = solveFromDRFast(startc,starte,given=fromDRPrune)
        finalSolPrint = doReverseRotate(finalSol,rev)
        print("Finish:", end='\t')
        for move in finalSolPrint:
            print(move,end=' ')
        print(f'\t{len(finalSolPrint)}')
        print(f"Solution length:\t{len(eoSol)+len(drSol)+len(finalSol)}\n")


def solveScrambleAllDRAxisExtraDRStep(scramble):
    print("Scramble:",scramble)
    scramble = scramble.split(' ')
    scrambleList,reversing = rotatedScrambles(scramble)
    # Prune to finish cube
    if os.path.exists('fromDRPrune.pickle'):
        with open('fromDRPrune.pickle','rb') as f:
            fromDRPrune = pickle.load(f)
    else:
        print('first time, genning prune table to finish the cube. Should take like 5 sec with pypy')
        fromDRPrune =getFromDRPrune()
        with open('fromDRPrune.pickle','wb') as f:
            pickle.dump(fromDRPrune,f)

    # Prune to fast DR
    if os.path.exists('fromEOToDRPrune.pickle'):
        with open('fromEOToDRPrune.pickle','rb') as f:
            fromEOToDRPrune = pickle.load(f)
    else:
        print('first time, genning prune table to get EO -> DR. Should take like 5 sec with pypy')
        fromEOToDRPrune =getFromEOToDRPrune()
        with open('fromEOToDRPrune.pickle','wb') as f:
            pickle.dump(fromEOToDRPrune,f)
    
    for scramble,rev in zip(scrambleList,reversing):
        print(f"Solving for axis {rev}")
        starte = 407901468851537952
        startc = 247132686368
        for move in scramble:
            startc,starte = mdic[move](startc,starte)
        
        eoSol = solveEO(startc,starte)
        print("EO:",end='\t')
        eoSolPrint = doReverseRotate(eoSol,rev)
        for move in eoSolPrint:
            print(move,end=' ')
        for move in eoSol:
            startc,starte = mdic[move](startc,starte)
        print(f'\t{len(eoSol)}')

        human1drSol = Human1DR(startc,starte,scramble,eoSol)
        human1drSolPrint = doReverseRotate(human1drSol,rev)

        print("DR substep:",end='\t')
        for move in human1drSolPrint:
            print(move,end=' ')
        for move in human1drSol:
            startc,starte = mdic[move](startc,starte)
        print(f'\t{len(human1drSolPrint)}')

        drSol = EOToDR(startc,starte,scramble,eoSol,human1drSol,given=fromEOToDRPrune)
        drSolPrint = doReverseRotate(drSol,rev)

        print("DR:",end='\t')
        for move in drSolPrint:
            print(move,end=' ')
        for move in drSol:
            startc,starte = mdic[move](startc,starte)
        print(f'\t{len(drSolPrint)}')
        
        finalSol = solveFromDRFast(startc,starte,given=fromDRPrune)
        finalSolPrint = doReverseRotate(finalSol,rev)
        print("Finish:", end='\t')
        for move in finalSolPrint:
            print(move,end=' ')
        print(f'\t{len(finalSolPrint)}')
        print(f"Solution length:\t{len(eoSol)+len(drSol)+len(finalSol)}\n")

sloww = "F2 L D2 L' F2 L' F2 D2 R2 B2 D2 R B' U' F2 L R2 B R2 F2 R2"

# for i in range(1_000_000_000):
#     startc,starte = U(startc,starte)

# for i in range(1_000_000_000):
#     startc = twistCorner(startc,9)

# solveScramble("B U2 B D2 L2 D2 F2 U2 F' D2 R2 U' R' U' L' D' B2 F R B D'")
# solveScrambleFast("R2 F U2 L2 B' F' R2 F' L2 F2 D2 U' R' D2 L' D' R' B2 F U2")
# solveScrambleFast("R2 U L2 U2 L2 U' L2 R2 D F2 U L2 R' B2 D' R' U L' F' L B'")
# getFromEOToDRPrune()

# solveScrambleAllDRAxis("B' R2 U' F' R L2 F2 L2 U2 F' U2 B L2 D2 L2 F D R B D2 R' D B2 D' L")



# for i in range(1000000000):
#     startc = twistCorner(startc,18)
# print(startc)
# solveScrambleAllDRAxisExtraDRStep("D' B2 F2 D2 R2 D' F2 U' L2 D F2 U R' B' U2 R B' D' R' B D")
# solveScrambleAllDRAxisExtraDRStep("B' R2 U' F' R L2 F2 L2 U2 F' U2 B L2 D2 L2 F D R B D2 R' D B2 D' L")
