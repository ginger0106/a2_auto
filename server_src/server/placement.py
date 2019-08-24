import numpy as np
from .place_engine import *



class Placement(object):
    def __init__(self, placement_policy):
        self.policy = placement_policy

    def placement_proc(self,
                 multi_version ):
        policy_options = {
            'random': Rand_placement,
            'BKP': BKP_placement
        }
        placement_ins = policy_options[self.policy](
                 multi_version )
        decision_dict = placement_ins.engine()

        return decision_dict

    def init_proc(self,mulit_version):
        return Placement_engine(mulit_version).init_resource_dict()


