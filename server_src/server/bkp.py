# from gurobipy import *
import numpy as np
from sklearn.preprocessing import MinMaxScaler,minmax_scale,scale
from sklearn.metrics.pairwise import cosine_similarity

def bkp_gurobi(K, I, S, p, model, FS, BW, T, config,b):
    """

    :param K:
    :param I:
    :param S:
    :param p:
    :param model:
    :param FS:
    :param BW:
    :param T:
    :param config:
    :param b: b is the data version
    :return:
    """
    globals ().update (config.config_dict)
    m = Model('PLACEMENT')
    x_ski = {}
    p_ski = {}
    f_ki = {}
    b_ski = {}
    N_ski = {}
    similarity = {}
    avg = np.mean(p)
    delta = (2)
    # min_max_scaler = minmax_scale()
    # p_scale = np.exp(p)/np.sum(np.exp(p))
    # print(p_scale,np.sum(p_scale))
    # resource_type = min_max_scaler.fit_transform(np.array(FS).reshape(-1, 1)/np.array(BW).reshape(-1, 1))
    resource_type_servers = np.vstack((FS,BW)).transpose() #[[fs1,bw1],[fs2,bw2]]
    for k in range(K):
        for i in range(I):
            # _, f_ki[k, i],_ = model[MODEL_VERSION * k].get_arg(i, 0)
            # print(f_ki[k, i])
            for s in range(S):
                _, f_ki[k, i],b_ski[s, k, i] = model[MODEL_VERSION * k].get_arg (i, np.int16(b[k][i][s]))
                # b_ski[s, k, i] = b[k][i][s]
                N_ski[s, k, i] = BW[s] / b_ski[s, k, i]
                p_ski[s, k, i] = (p[k][i][s] - avg) / delta + avg
                # p_ski[s, k, i] = p_scale[k][i][s]
                upper_bound = min((FS[s] / f_ki[k, i]), N_ski[s, k, i],model[MODEL_VERSION * k].lam)
                # print(upper_bound)
                demand_type = np.array([f_ki[k, i],b_ski[s, k, i]]).reshape(1,-1)
                resource_type = resource_type_servers[s].reshape(1,-1)
                similarity[s, k, i] = cosine_similarity(demand_type,resource_type)
                # print(s,similarity[s, k, i][0][0]*p_ski[s, k, i],similarity[s, k, i][0][0],p_ski[s, k, i])
                x_ski[s, k, i] = m.addVar(lb=0, ub = upper_bound , vtype=GRB.CONTINUOUS,
                                          name="x_%s_%s_%s" % (s, k, i))
    # print(p_ski) * similarity[s, k, i][0][0]*p_ski[s, k, i] *
    # print(p_ski)
    m.setObjective(quicksum(quicksum(quicksum(x_ski[s, k, i]*(p_ski[s, k, i])*similarity[s, k, i]
                                              for s in range(S))
                                     for k in range(K))
                            for i in range(I))
                   , GRB.MAXIMIZE)

    for s in range(S):
        m.addConstr(quicksum(quicksum(x_ski[s, k, i] * f_ki[k, i]
                                      for k in range(K))
                             for i in range(I)) <= FS[s] * T)
        print(BW[s] * T)
        m.addConstr(quicksum(quicksum(x_ski[s, k, i] * b_ski[s, k, i]
                                      for k in range(K))
                             for i in range(I)) <= BW[s] * T)

    # for k in range(K):
    #     for s in range(S):
    #         m.addConstr(quicksum(x_ski[s,k,i]
    #                                       for i in range(I))>=1)

    m.optimize()
    result = np.zeros((S, K, I))
    solution = m.getAttr('x', x_ski)
    for k in range(K):
        for i in range(I):
            for s in range(S):
                result[s][k][i] = solution[s, k, i]
    result = np.array(result).reshape(S, I * K)

    M = []
    model2 = model.reshape(K, I)
    for m in model2[:, 1]:
        for i in range(I):
            M.append(m.get_flops(i))

    M = np.array(M)
    for s in range(S):
        a = np.sum(result[s] * M)
        print(a, FS[s], a / (FS[s] * T))

    return np.floor(result)


def bkp_gurobi_noversion(K, I, S, p, model, FS, BW, T ,config):
    globals ().update (config.config_dict)
    m = Model('PLACEMENT')
    x_ski = {}
    p_ski = {}
    f_ki = {}
    b_ki = {}
    N_sk = {}
    avg = np.mean(p)
    similarity = {}
    delta = (2)
    # print(p)
    # min_max_scaler = MinMaxScaler ()
    # resource_type = min_max_scaler.fit_transform (np.array(p).reshape (-1, 1))
    resource_type_servers = np.vstack((FS,BW)).transpose() #[[fs1,bw1],[fs2,bw2]]

    for k in range(K):
        _, f_ki[k], b_ki[k]= model[k].get_arg(0, 0)
        # print(f_ki[k, i])
        for s in range(S):
            N_sk[s, k] = BW[s] / b_ki[k]
            p_ski[s, k] = (p[k][s] - avg) / delta + avg
            upper_bound = min(FS[s] / f_ki[k], N_sk[s, k],model[k].lam)
            # print(FS[s] / f_ki[k], N_sk[s, k],model[k].lam)
            demand_type = np.array([f_ki[k], b_ki[k]]).reshape(1, -1)
            resource_type = resource_type_servers[s].reshape(1, -1)
            similarity[s, k] = cosine_similarity(demand_type, resource_type)
            # print(upper_bound,1111111,)
            x_ski[s, k] = m.addVar(lb=0.0, ub=np.ceil(upper_bound), vtype=GRB.CONTINUOUS,
                                   name="x_%s_%s" % (s, k))

    print(p_ski)
    # *np.abs (f_ki[k] / f_ki[k] - resource_type[s])
    m.setObjective(quicksum(quicksum(p_ski[s, k] * x_ski[s, k]
                                     for s in range(S))
                            for k in range(K))
                   , GRB.MAXIMIZE)

    for s in range(S):
        # print(FS[s],BW[s])
        m.addConstr(quicksum(x_ski[s, k] * f_ki[k]
                             for k in range(K))
                    <= FS[s] * T)
        m.addConstr(quicksum(x_ski[s, k] * b_ki[k]
                                      for k in range(K))
                                 <= BW[s] * T)

    # for k in range(K):
    #     for s in range(S):
    #         m.addConstr(x_ski[s, k]>=1)
         # print(model[MODEL_VERSION * k].lam * T)
        # m.addConstr(quicksum(x_ski[s, k] for s in range(S)) >= 1.1)

    # (p_ski[s, k, i] * model[MODEL_VERSION * k].lam * T)

    # for k in range(K):
    #     for s in range(S):
    #         m.addConstr(x_ski[s, k] >= (p_ski[s, k] * model[k].lam * T))

    m.optimize()
    # solution = m.getAttr('x',m.getVars())
    result = np.zeros((S, K))
    solution = m.getAttr('x', x_ski)
    for k in range(K):
        for s in range(S):
            result[s][k] = solution[s, k]
    result = np.array(result).reshape(S, K)
    # result = np.floor(result)

    M = []
    model2 = model.reshape(K)
    for m in model2:
        M.append(m.get_flops(0))

    M = np.array(M)
    for s in range(S):
        a = np.sum(result[s] * M)
        print(a, FS[s], a / (FS[s] * T))
    return np.floor(result)
# knapsack_gurobi(10, 5, 5, 1, model, FS)
# return 0
