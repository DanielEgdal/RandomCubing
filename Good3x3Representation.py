
starte = 407901468851537952
startc = 247132686368

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


# printbin(startc,starte)

# startc,starte = R(startc,starte)

scramble = "F R D2 U2 R D2 R2 F2 L' U2 R' D2 B' R2 F R2 F' D' U2".split(' ')
mdic = {"R":R,"R'":Rp,"R2'":R2,"R2":R2,"U":U,"U'":Up,"U2":U2,"D":D,"D'":Dp,"D2":D2,"F":F,"F'":Fp,"F2":F2,"U2'":U2,"B":B,"B'":Bp,"B2":B2,"L":L,"L2":L2,"L'":Lp}

for i in range(1000000):
    for move in scramble:
        startc,starte = mdic[move](startc,starte)

# print('after')
# printbin(startc,starte)
