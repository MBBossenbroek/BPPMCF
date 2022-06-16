

def Algo(name):
    from readdata import data
    data = data(name)
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


    Q = []
    for i in Colors:
        q = 0
        I = []
        for j in range(len(c)):
            if c[j] == i:
                q += w[j]
                I.append(j)
        Q.append([q,I])

    Qs = []
    Ql = []

    for i in range(len(Q)):
        if Q[i][0] <= C:
            Qs.append([i,Q[i][0]])
        else:
            Ql.append([i,Q[i][0]])

    Qs = sorted(Qs,key=lambda l:l[1], reverse=True)
    Ql = sorted(Ql,key=lambda l:l[1], reverse=True)

    for i in Qs:
        for j in Bins:
            if i[1] <= j[0]:
                j[0] -= i[1]

                for k in Q[i[0]][1]:
                    j[1].append(k)
                break

    
    assign = 0
    for i in Ql:
        items = []
        for j in Q[i[0]][1]:
                items.append([j,w[j]])
        items = sorted(items,key=lambda l:l[1], reverse=True)
        for i in items:
            Assigned = False
            for j in Bins:
                if i[1] <= j[0]:
                    j[1].append(i[0])
                    j[0] -= i[1]
                    Assigned = True
                    assign +=1
                    break
            if Assigned is False:
                for j in Bins:
                    for m in Bins:
                        for k in j[1]:
                                if data[1][k] + m[0] < 0 and i[1] + j[0] < 0:
                                    j[1].remove(k)
                                    m[1].append(k)
                                    j[1].append(i[0])
 

            

    mcf = 0
    bins = 0
    for i in Bins:
        if len(i[1])>0:
            bins += 1
        for j in Q: #kleurgroepen
            present = False
            for k in i[1]:#alle items in elke bin
                if k in j[1]:
                    present = True
            if present == True:    
                mcf += 1       
    
    filename = r"C:\Users\Matth\OneDrive\Documenten\University\Thesis\Data\compare.txt"
    with open(filename,"w+", encoding="utf-8-sig") as fh:
        for j in range(len(Bins)):
                for k in Bins[j][1]:
                    fh.write(str(j)+"/"+str(k))
                    fh.write("\n")
    fh.close
            


    return[mcf, bins]

Algo(r"C:\Users\Matth\OneDrive\Documenten\University\Thesis\Data\120-2-1.txt")