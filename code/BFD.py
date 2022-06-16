
from readdata import data
def BFD(filename):
    from readdata import data

    data = data(filename)
    w = data[1]
    c = data[2]
    C = data[0]
    N = len(w)
    UB = data[3]

    Colors = []
    for i in c:
        if i not in Colors:
            Colors.append(i)

    Bins = []
    MCF = []
    for i in range(UB):
        Bins.append([C,[]])
        MCF.append([])

    Items = []
    for i in range(len(w)):
        Items.append([i,w[i]])

    Items = sorted(Items,key=lambda l:l[1], reverse=True)

    Q = []
    for i in Colors:
        q = 0
        I = []
        for j in range(len(c)):
            if c[j] == i:
                q += w[j]
                I.append(j)
        Q.append([q,I])



    for i in Items:
        Bestfit = C
        for j in range(len(Bins)):
            
            if i[1] <= Bins[j][0] and Bins[j][0] <= Bestfit:
                Canidate = j
                Bestfit = Bins[j][0]
                

                
        Bins[Canidate][1].append(i[0])
        Bins[Canidate][0] -= i[1]


    mcf = 0
    bins = 0
    for i in Bins:
        for j in Q: #kleurgroepen
            present = False
            for k in i[1]:#alle items in elke bin
                if k in j[1]:
                    present = True
            if present == True:    
                mcf += 1  

        if len(i[1])>0:
            bins += 1

    return[mcf,bins]

print(BFD(r"C:\Users\Matth\OneDrive\Documenten\University\Thesis\Data\toy.txt"))