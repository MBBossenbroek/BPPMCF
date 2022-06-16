
from gurobipy import *



def two_step_plain(filename):
    from readdata import data
    data = data(filename)
    import numpy as np
    import math


    w = data[1]
    c = data[2]
    C = data[0]
    UB = data[3]
    N = len(w)


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
    

    t = []
    for i in range(N):
        for j in range(UB):
                t.append((j,i))     





    M = len(Colors)


    stepone_model = Model("BPP")

   


    x = stepone_model.addVars(UB,N, vtype= GRB.BINARY, name = "x" )



    y = stepone_model.addVars(UB,M, vtype= GRB.BINARY, name = "y")






    for j in range(N):
        stepone_model.addConstr(quicksum(x[i,j] for i in range(UB)) == 1)

    stepone_model.addConstrs(quicksum(x[i,j]*w[j] for j in range(N)) <= C for i in range(UB))

    for j in range(len(Colors)):
        for k in range(UB):
            for i in range(N):
                if data[i][1] == Colors[j]:
                    stepone_model.addConstr(x[k,i] <= y[k,j])

    for k in range(len(Colors)):
        for j in range(UB):
                stepone_model.addConstr((quicksum(x[j,i] for i in colj[k] ) <= y[j,k]*C ))

    for j in range(len(Colors)):
        stepone_model.addConstr(quicksum(y[i,j] for i in range(UB)) >= Lc[j])



    Obj = quicksum(y[i,j] for j in range(M) for i in range(UB))


    stepone_model.setObjective(Obj,GRB.MINIMIZE) 



    stepone_model.optimize()

    mcf = int(stepone_model.objVal)

    startsol = []
    for i in t:
        startsol.append([i,x[i[0],i[1]].x])


    steptwo_model = Model("BPP")

    x = steptwo_model.addVars(UB,N, vtype= GRB.BINARY, name = "x" )
    for i in range(len(t)):
        x[t[i][0],t[i][1]].start = startsol[i][1]

    
    y = steptwo_model.addVars(UB,M, vtype= GRB.BINARY, name = "y")
    z = steptwo_model.addVars(UB, vtype= GRB.BINARY, name = "z")




    steptwo_model.addConstr(quicksum(y[i,j] for j in range(M) for i in range(UB)) <= mcf)

    for j in range(N):
        steptwo_model.addConstr(quicksum(x[i,j] for i in range(UB)) == 1)

    steptwo_model.addConstrs(quicksum(x[i,j]*w[j] for j in range(N)) <= C*z[i] for i in range(UB))

    for j in range(len(Colors)):
        for k in range(UB):
            for i in range(N):
                if data[i][1] == Colors[j]:
                    steptwo_model.addConstr(x[k,i] <= y[k,j])


    for k in range(len(Colors)):
        for j in range(UB):
                steptwo_model.addConstr((quicksum(x[j,i] for i in colj[k] ) <= y[j,k]*C ))

    for j in range(len(Colors)):
        steptwo_model.addConstr(quicksum(y[i,j] for i in range(UB)) >= Lc[j])




    Obj = quicksum(z[i] for i in range(UB))

    steptwo_model.setObjective(Obj,GRB.MINIMIZE) 

    steptwo_model.setParam('TimeLimit', 300)
    steptwo_model.optimize()

    print("Objective function value: %f" %steptwo_model.objVal)
    for v in steptwo_model.getVars():
        print("%s : %g" %(v.varName,v.x))

    X = []
    for var in steptwo_model.getVars():
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

    Y = 0

    for var in steptwo_model.getVars():
        if "y" in var.VarName:
            Y += var.xn




    MCF = Y            
    runtime =  steptwo_model.Runtime
    BPP = len(used_bins)
    print("Bins used: %f" %BPP)
    print("Objective function value: %f" % steptwo_model.objVal)
    print("Minimum Color Fragmentation: %f" %MCF)
    print("Runtime is: %f" %runtime)
    return [runtime,MCF,BPP]






