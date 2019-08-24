# from ..utilis import model_identify
from .measurement import *
from .global_val import *


class Model():
    # data_variants : 0 is the best, 16 is the worst.
    def __init__(self, name, model_variants=0):
        self.name = name
        self.acc_list = self.get_acc_list()
        self.flops_list = self.get_flops_list()
        self.model_variants = model_variants
        self.acc = self.acc_list[self.model_variants][0]
        self.fp = self.flops_list[self.model_variants]
        self.bw = IMG_SIZE[0]

    def get_arg(self, model_variants, data_variants):
        acc = self.acc_list[model_variants][data_variants]
        fp = self.flops_list[model_variants]
        bw = IMG_SIZE[data_variants]
        return acc, fp, bw

    def get_bw(self, data_variants):
        return IMG_SIZE[data_variants]

    def get_flops(self, model_variants):
        return self.flops_list[model_variants]

    def set_arg(self, model_variants, data_variants):
        self.model_variants = model_variants
        self.acc = self.acc_list[self.model_variants][data_variants]
        self.fp = self.flops_list[self.model_variants]
        self.bw = IMG_SIZE[data_variants]

    def get_runtime_list(self):
        if self.name == 'mobile':
            runtime_list = MBV1TIME
        else:
            runtime_list = RES18TIME
        return runtime_list

    def get_acc_list(self):
        if self.name == 'mobile':
            acc_list = MBV1ACC
        else:
            acc_list = RES18ACC
        return acc_list

    def get_flops_list(self):
        if self.name == 'mobile':
            flops_list = MBV1FLP
        else:
            flops_list = RES18FLP
        return flops_list


class ModelConfig():
    def __init__(self, version_flag):
        self.version_flag = version_flag


    def model_gen(self):
        model_zoo = []
        for model_name in ['mobile','res18']:
            if self.version_flag == 1:
                for model_variants in range(MODEL_VERSION):
                    model_zoo.append(Model(model_name, model_variants))
            else:
                model_zoo.append(Model(model_name, 0))
        return model_zoo

    def model_zoo_reshape(self):
        model_zoo = np.array(self.model_gen())
        if self.version_flag == 1:
            return model_zoo.reshape(MODEL_NUMBER, MODEL_VERSION)
        else:
            return model_zoo.reshape(MODEL_NUMBER, 1)

    def model_index(self, request):
        if self.version_flag == 1:
            model_index = request.Model.name * MODEL_VERSION + request.model_variants
        else:
            model_index = request.Model.name
        return model_index