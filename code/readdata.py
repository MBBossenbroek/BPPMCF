def  data(filename) :   
    fh1 = open(filename,"r",encoding = 'utf-8-sig')

    L = fh1.readline()
    L = L.strip("\n")
    UB = int(L)

    L = fh1.readline()
    L = L.strip("\n")
    Bincap = int(L)
    

    Weights = []
    Colors = []

    d1 = {}
    while len(L)>0:
        L = fh1.readline()
        L = L.strip("\t\n")
        K = L.split("\t")
        if len(K)>1:
            Weights.append(int(K[1]))
            Colors.append(K[0])
        else:
            continue
    fh1.close()
    return Bincap, Weights, Colors,UB