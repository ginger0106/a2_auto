
import numpy as np
# from ..utilis.multi_version_index import multi_version_index
from .bkp import bkp_gurobi, bkp_gurobi_noversion
from .global_val import *
from .model import *




class Placement_engine(object):
    def __init__(self,multi_version):
        self.multi_version = multi_version
        # self.modelconfig = ModelConfig(multi_version)
        self.model_zoo= ModelConfig(self.multi_version).model_gen()
        self.port = [8501 + 2 * i for i in range (4)]+[8601 + 2 * i for i in range (4)]
        self.model_name = [ 'mobile_dcp_0','mobile_dcp_1', 'mobile_dcp_2', 'mobile_dcp_3', 'res18_dcp_0',
                      'res18_dcp_1', 'res18_dcp_2', 'res18_dcp_3']


    def engine(self):
        pass

    def set_resource_dict(self,cpu_allocation):
        self.desicion = {self.model_name[i]:{'port':self.port[i],'cpu':round(cpu_allocation[i],2)}
                         for i in range (len(self.model_zoo))}
        return self.desicion

    def init_resource_dict(self):
        self.init_desicion = {self.model_name[i]:{'port':self.port[i],'cpu':2}
                         for i in range (len(self.model_zoo))}
        return self.init_desicion



class BKP_placement(Placement_engine):
    pass
#     def engine(self,p):
#
#         servers_flops = 16*2000
#         servers_bandwidth = 20*1024 #KB
#         if self.multi_version == True:
#             solution = bkp_gurobi (MODEL_NUMBER, MODEL_VERSION, TOTAL_SERVER_NUM, p, np.array (self.model_zoo),
#                                    servers_flops,
#                                    servers_bandwidth, 1 ,b)
#         else:
#
#             solution = bkp_gurobi_noversion (MODEL_NUMBER, MODEL_VERSION, TOTAL_SERVER_NUM, p, np.array (self.model_zoo),
#                                              servers_flops,
#                                              servers_bandwidth, 1,self.config)
#             # self.sett_c_noversion (solution, np.array (self.model_zoo))
#
#         for index, server in enumerate (self.server_list):
#             server.set_resource_dict(self.gen_model_config(solution[index]))
#         print(solution)
#         print("placement done!")
#
#         self.print_place_solution(self.server_list)
#         return self.server_list
#



class Rand_placement(Placement_engine):

    def engine(self):
        rand_rng = np.random.RandomState(11)
        result = np.zeros ((len (self.model_zoo)))
        cpu_allocation = np.zeros ((len (self.model_zoo)))
        FLOPS = 1*3000
        BW = 200*1024
        while FLOPS > 0 and BW>0:
            pick_index = rand_rng.choice (len(self.model_zoo))
            if FLOPS - self.model_zoo[pick_index].fp < 0 and BW - self.model_zoo[pick_index].get_bw(11):
                break
            result[pick_index] += 1
            FLOPS = FLOPS - self.model_zoo[pick_index].fp
            BW = BW - self.model_zoo[pick_index].get_bw (rand_rng.choice(11))
        for index in range(len(self.model_zoo)) :
            cpu_allocation[index] = self.model_zoo[index].fp*result[index]/300
            # print( self.model_zoo[index].fp)
        desicion_dict = self.set_resource_dict(cpu_allocation)
        # print(result)
        print("placement done!")
        return desicion_dict

