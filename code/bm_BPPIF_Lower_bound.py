
from gurobipy import *



def IF_LB(filename):
    import numpy as np
    from readdata import data
    import math


    data = data(filename)

    w = data[1]
    c = data[2]
    C = data[0]
    N = len(w)


    data = []
    for j in range(len(w)):
        data.append([j,c[j],w[j]])


    Colors = []
    for i in c:
        if i not in Colors:
            Colors.append(i)

    u = 0
    for i in Colors:
        v = 0
        for j in data:
            if j[1] == i:
                v += j[2]
        u += math.ceil(v/C)

    LB = u
    UB = N
    M = len(Colors)


    data = []
    for j in range(len(w)):
        data.append([j,c[j],w[j]])


    Colors = []
    for i in c:
        if i not in Colors:
            Colors.append(i)

    colj = []
    for i in Colors:
        colr = []
        for j in data:
            if i == j[1]:
                colr.append(j[0])
        colj.append(colr)


    Lc1 = []
    for i in Colors:
        v = 0
        for j in data:
            if j[1] == i:
                v += j[2]
        Lc1.append(math.ceil(v/C))

    Ic1 = []
    for i in Colors:
        c1 = []
        for j in data:
            if j[1] == i:
                for k in range(C//2):
                    if j[2] > C-k:
                        c1.append(j[0])
                        break 
        Ic1.append(c1)

    Ic2 = []
    for i in Colors:
        c2 = []
        for j in data:
            if j[1] == i:
                for k in range(C//2):
                    if C-k >= j[2] and j[2] > C/2  :
                        c2.append(j[0])
                        if j[0] in Ic1:
                            print("stoooppp")
                        break
                        
        Ic2.append(c2)

    Ic3 = []
    for i in Colors:
        c3 = []
        for j in data:
            if j[1] == i:
                for k in range(C//2):
                    if C/2 >= j[2] and j[2] >= k  :
                        c3.append(j[0])
                        if j[0] in Ic1 or j[0] in Ic2:
                            print("stoooppp")
                        break 
        Ic3.append(c3)

    Lc2 = []
    for i in range(len(Colors)):
        lc2 = 0
        a = 0
        for j in Ic3[i]:

            a += data[j][2]/C
        b = 0    
        for k in Ic2[i]:
            b += data[j][2]/C
        if math.ceil(a-len(Ic2[i])+b)>0:
            lc2 += math.ceil(a-len(Ic2[i])+b)
        lc2 += len(Ic1[i])+len(Ic2[i])
        Lc2.append(lc2)

    Lc = []
    for i in range(len(Colors)):
        Lc.append(max(Lc1[i],Lc2[i]))
    

        




    UB = N
    M = len(Colors)

    max_weight = max(w)

    Icw = []
    for i in range(len(colj)):
        p = []
        for j in range(1,max_weight+1):
            p.append([])
        Icw.append(p)

    for i in range(len(colj)):
        for k in colj[i]:        
            Icw[i][w[k]-1].append(k)





    BPP_model = Model("BPP")




    x = BPP_model.addVars(UB,N,max_weight, vtype= GRB.INTEGER, name = "x" )
    y = BPP_model.addVars(UB,M, vtype= GRB.BINARY, name = "y")






    for j in range(M):
        for k in range(max_weight):
            BPP_model.addConstr(quicksum(x[i,j,k] for i in range(UB)) == len(Icw[j][k]))


    BPP_model.addConstrs(quicksum(x[i,j,k]* (k+1) for j in range(M) for k in range(max_weight)) <= C for i in range(UB))


    for i in range(UB): #voor elke bin
        for j in range(len(Icw)): #voor elke kleur
            for k in range(len(Icw[j])):#voor elk item met kleur j en weight k
                for l in range(len(Icw[j][k])):
                    BPP_model.addConstr(x[i,j,k] <= y[i,j]*len(Icw[j][k]))

    for k in range(len(Icw)):#voor elke kleur
        for j in range(UB):# voor elke bin
                BPP_model.addConstr((quicksum(x[j,k,l-1]*l for l in range(1,max_weight+1) ) <= y[j,k]*C ))

    for j in range(len(Colors)):
        BPP_model.addConstr(quicksum(y[i,j] for i in range(UB)) >= Lc[j])



    Obj = quicksum(y[i,j] for j in range(M) for i in range(UB))


    BPP_model.setObjective(Obj,GRB.MINIMIZE) 



    BPP_model.optimize()

    F = BPP_model.objVal




    BPP_model = Model("BPP")


    Q = []

    for i in Colors:
        q = 0
        for j in range(len(c)):
            if c[j] == i:
                q += w[j]
        Q.append(q)


    duplicates = []
    W = []
    for i in Q:
        if i not in duplicates:
            W.append([i,1])
            duplicates.append(i)
        else:
            for j in range(len(W)):
                if W[j][0] == i:
                    W[j][1] += 1

    if 1 not in duplicates:
        duplicates.append(1)






    u = BPP_model.addVars(UB, vtype= GRB.BINARY, name = "u" )
    x = BPP_model.addVars(M,UB, vtype= GRB.CONTINUOUS, name = "x", lb=0,ub=1 )
    z = BPP_model.addVars(M,UB, vtype= GRB.BINARY, name = "z")








    for i in range(M):
        BPP_model.addConstr(quicksum(x[i,j] for j in range(UB)) == 1)

    BPP_model.addConstrs(quicksum(x[i,j]*Q[i] for i in range(M)) <= C*u[j] for j in range(UB))

    BPP_model.addConstr(quicksum(z[i,j]  for i in range(M) for j in range(UB))-M <= F )

    for k in range(UB):
        for i in range(M):
            BPP_model.addConstr(x[i,k] <= z[i,k])
            


    Obj = quicksum(u[i] for  i in range(UB))

    BPP_model.setObjective(Obj,GRB.MINIMIZE) 


    BPP_model.optimize()

    print("Objective function value: %f" %BPP_model.objVal)
    for v in BPP_model.getVars():
        print("%s : %g" %(v.varName,v.x))

    X = []
    for var in BPP_model.getVars():
            if "x" in var.VarName:
                if var.xn > 0:
                    X.append(['%s %g' %(var.varName, var.xn)])


    used_bins = []
    for i in X:
        for j in i:
            j = j.split("[")
            j = j[1].split(",")
            if j[0] not in used_bins:
                used_bins.append(j[0])
    runtime = BPP_model.Runtime
    BPP = len(used_bins)
    return [runtime,BPP_model.objVal]
    print("Objective function value: %f" %BPP_model.objVal)
