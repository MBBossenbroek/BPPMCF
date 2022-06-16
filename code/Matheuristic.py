
from gurobipy import *


def Meta(filename):
    import math
    import numpy as np
    from readdata import data

    data = data(filename)

    w = data[1]
    c = data[2]
    C = data[0]
    N = len(w)
    UB = data[3]


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
    

        




 
    M = len(Colors)


    LP_Relaxation = Model("BPP")




    x = LP_Relaxation.addVars(UB,N, vtype= GRB.CONTINUOUS, name = "x" )
    y = LP_Relaxation.addVars(UB,M, vtype= GRB.CONTINUOUS, name = "y")
    z = LP_Relaxation.addVars(UB, vtype= GRB.BINARY, name = "z")






    for j in range(N):
        LP_Relaxation.addConstr(quicksum(x[i,j] for i in range(UB)) == 1)

    LP_Relaxation.addConstrs(quicksum(x[i,j]*w[j] for j in range(N)) <= C*z[i] for i in range(UB))

    for j in range(len(Colors)):
        for k in range(UB):
            for i in range(N):
                if data[i][1] == Colors[j]:
                    LP_Relaxation.addConstr(x[k,i] <= y[k,j])

    for k in range(len(Colors)):
        for j in range(UB):
                LP_Relaxation.addConstr((quicksum(x[j,i] for i in colj[k] ) <= y[j,k]*C ))

    for j in range(len(Colors)):
        LP_Relaxation.addConstr(quicksum(y[i,j] for i in range(UB)) >= Lc[j])



    Obj = quicksum(y[i,j]*UB for j in range(M) for i in range(UB)) + quicksum(z[i] for i in range(UB))

    LP_Relaxation.setObjective(Obj,GRB.MINIMIZE) 

    LP_Relaxation.optimize()


  
    a = 0
    Fixed_items = []
    for v in LP_Relaxation.getVars():
        #print("%s : %g" %(v.varName,v.x))
        if "x" in v.VarName:
            if v.xn > 0.99:
                index = v.Varname.split("[")
                index = index[1].split(",")
                index[1] = index[1].strip("]")
                index[0] = int(index[0])
                index[1] = int(index[1])
                Fixed_items.append(index)
                a +=1

       

    X = []
    for var in LP_Relaxation.getVars():
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

    for var in LP_Relaxation.getVars():
        if "y" in var.VarName:
            Y += var.xn


    MCF = Y            
    runtime = LP_Relaxation.Runtime
    BPP = len(used_bins)
  
    fixed = []
    not_fixed = []
    for i in range(N):
        for j in range(UB):
            if [j,i] in Fixed_items:    
                    fixed.append((j,i))
            else:
                not_fixed.append((j,i))     
    


    f = tuplelist(fixed)
    nf = tuplelist(not_fixed)




    BPP_model = Model("BPP")



 
                
     
    
    






    x = BPP_model.addVars(UB,N, vtype= GRB.BINARY, name = "x" )
    y = BPP_model.addVars(UB,M, vtype= GRB.BINARY, name = "y")
    z = BPP_model.addVars(UB, vtype= GRB.BINARY, name = "z")





    for j in range(N):
        BPP_model.addConstr(quicksum(x[i,j] for i in range(UB)) == 1)

    for k in fixed:
        BPP_model.addConstr(x[k[0],k[1]] == 1)


    BPP_model.addConstrs(quicksum(x[i,j]*w[j] for j in range(N)) <= C*z[i] for i in range(UB))

    for j in range(len(Colors)):
        for k in range(UB):
            for i in range(N):
                if data[i][1] == Colors[j]:
                    BPP_model.addConstr(x[k,i] <= y[k,j])

    for k in range(len(Colors)):
        for j in range(UB):
                BPP_model.addConstr((quicksum(x[j,i] for i in colj[k] ) <= y[j,k]*C ))

    for j in range(len(Colors)):
        BPP_model.addConstr(quicksum(y[i,j] for i in range(UB)) >= Lc[j])



    Obj = quicksum(y[i,j]*UB for j in range(M) for i in range(UB)) + quicksum(z[i] for i in range(UB))

    BPP_model.setObjective(Obj,GRB.MINIMIZE) 

    BPP_model.setParam('TimeLimit', 300)
    BPP_model.optimize()

    if BPP_model.Status == GRB.INFEASIBLE:
        runtime = "INF"
        MCF = "INF"
        BPP = "INF"

    else:
        print("Objective function value: %f" %BPP_model.objVal)


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

        Y = 0

        for var in BPP_model.getVars():
            if "y" in var.VarName:
                Y += var.xn


        MCF = Y            
        runtime = BPP_model.Runtime
        BPP = len(used_bins)
        print("Bins used: %f" %BPP)
        print("Objective function value: %f" %BPP_model.objVal)
        print("Minimum Color Fragmentation: %f" %MCF)
        print("Runtime is: %f" %runtime)
        print(a)














    return [a,runtime,MCF,BPP]

