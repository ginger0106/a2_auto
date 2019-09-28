import os
import numpy as np

PATH = '/home/ginger/a2_auto/client/traces'
trace = {}

def region():
    trace_lst = []

    for region in os.listdir(PATH):
        if region.startswith('re'):
            path = os.path.join(PATH,region)
            for num in range(8):

                content_path = os.path.join(path,f'content_{num}.npy')
                print(content_path)
                trace_lst.append(np.load(content_path))
            trace[region] = np.sum(trace_lst)
            trace_lst = []
    print(trace)

def content():
    trace_lst = []

    for num in range(8):
        for region in os.listdir(PATH):
            if region.startswith('re'):
                path = os.path.join(PATH,region)

                content_path = os.path.join(path,f'content_{num}.npy')
                # print(content_path)
                trace_lst.append(np.load(content_path)[:60])
        trace[num] = (trace_lst)
        trace_lst = []
    print(trace)
    return trace
# content()

def gen_trace():
    trace_lst = [20]*720
    print(trace_lst)
    np.save('/home/ginger/a2_auto/client/traces_ori/region_0/content_9.npy',trace_lst)
#
# t = content()
# print(t[0])
# def change_trace():
#     for file in os.listdir(PATH):
#



# gen_trace()
content()