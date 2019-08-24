import numpy as np


RES18ACC = np.load('server/res18_acc_new.npy')
RES18FLP = np.array([3.65, 3.65 - 3.65 * 0.4, 3.65 - 3.65 * 0.6, 3.65 - 3.65 * 0.8])
RES18TIME = [1] * 4

MBV1ACC = np.load('server/mobile_v1_acc_new.npy')
MBV1FLP = np.array([1.1375, 1.1375 - 1.1375 * 0.4, 1.1375 - 1.1375 * 0.6, 1.1375 - 1.1375 * 0.8])
MBV1TIME = [1] * 4


IMG_SIZE = np.load('server/IMG_SIZE.npy')