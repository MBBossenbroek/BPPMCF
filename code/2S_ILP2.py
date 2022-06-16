
from gurobipy import *



def two_step_plain_ILP2(filename):
    from readdata import data
    data = data(filename)
    import numpy as np
    import math


    w = data[1]
    c = data[2]
    C = data[0]
    UB = data[3]
    N = len(w)
    max_weight = max(w)


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
            for k in range(max_weight):
                    t.append((j,i,k))     





    M = len(Colors)


    Icw = []
    for i in range(len(colj)):
        p = []
        for j in range(1,max_weight+1):
            p.append([])
        Icw.append(p)

    for i in range(len(colj)):
        for k in colj[i]:        
            Icw[i][w[k]-1].append(k)

    stepone_model = Model("BPP")

    x = stepone_model.addVars(UB,N,max_weight, vtype= GRB.INTEGER, name = "x" )
    y = stepone_model.addVars(UB,M, vtype= GRB.BINARY, name = "y")






    for j in range(M):
        for k in range(max_weight):
            stepone_model.addConstr(quicksum(x[i,j,k] for i in range(UB)) == len(Icw[j][k]))


    stepone_model.addConstrs(quicksum(x[i,j,k]* (k+1) for j in range(M) for k in range(max_weight)) <= C for i in range(UB))


    for i in range(UB): #voor elke bin
        for j in range(len(Icw)): #voor elke kleur
            for k in range(len(Icw[j])):#voor elk item met kleur j en weight k
                for l in range(len(Icw[j][k])):
                    stepone_model.addConstr(x[i,j,k] <= y[i,j]*len(Icw[j][k]))

    for k in range(len(Icw)):#voor elke kleur
        for j in range(UB):# voor elke bin
                stepone_model.addConstr((quicksum(x[j,k,l-1]*l for l in range(1,max_weight+1) ) <= y[j,k]*C ))

    for j in range(len(Colors)):
        stepone_model.addConstr(quicksum(y[i,j] for i in range(UB)) >= Lc[j])



    Obj = quicksum(y[i,j] for j in range(M) for i in range(UB))


    stepone_model.setObjective(Obj,GRB.MINIMIZE) 



    stepone_model.optimize()
    mcf = int(stepone_model.objVal)

    startsol = []
    for i in t:
        startsol.append([i,x[i[0],i[1],i[2]].x])


    steptwo_model = Model("BPP")

    x = steptwo_model.addVars(UB,N,max_weight, vtype= GRB.INTEGER, name = "x" )
    for i in range(len(t)):
        x[t[i][0],t[i][1],t[i][2]].start = startsol[i][1]

    
    y = steptwo_model.addVars(UB,M, vtype= GRB.BINARY, name = "y")
    z = steptwo_model.addVars(UB, vtype= GRB.BINARY, name = "z")




    steptwo_model.addConstr(quicksum(y[i,j] for j in range(M) for i in range(UB)) <= mcf)

    for j in range(M):
        for k in range(max_weight):
            steptwo_model.addConstr(quicksum(x[i,j,k] for i in range(UB)) == len(Icw[j][k]))


    steptwo_model.addConstrs(quicksum(x[i,j,k]* (k+1) for j in range(M) for k in range(max_weight)) <= C*z[i] for i in range(UB))


    for i in range(UB): #voor elke bin
        for j in range(len(Icw)): #voor elke kleur
            for k in range(len(Icw[j])):#voor elk item met kleur j en weight k
                for l in range(len(Icw[j][k])):
                    steptwo_model.addConstr(x[i,j,k] <= y[i,j]*len(Icw[j][k]))

    for k in range(len(Icw)):#voor elke kleur
        for j in range(UB):# voor elke bin
                steptwo_model.addConstr((quicksum(x[j,k,l-1]*l for l in range(1,max_weight+1) ) <= y[j,k]*C ))

    for j in range(len(Colors)):
        steptwo_model.addConstr(quicksum(y[i,j] for i in range(UB)) >= Lc[j])




    Obj = quicksum(z[i] for i in range(UB))

    steptwo_model.setObjective(Obj,GRB.MINIMIZE) 

    steptwo_model.setParam('TimeLimit', 300)
    steptwo_model.optimize()

    print("Objective function value: %f" %steptwo_model.objVal)
    #for v in steptwo_model.getVars():
        #print("%s : %g" %(v.varName,v.x))

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





