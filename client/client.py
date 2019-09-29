import asyncio
import _thread
import logging
import subprocess
import json
from shlex import quote
import dict_bytes as db
from dict_bytes import PATH

import os
import random
from sender import tf_serving_cls
import time, sys
import numpy as np
import itertools
import traceback
import aiohttp
import timeit

# from .model import *
# from .measurement import *
# from .placement import Placement


def unbuffered_print(p_str):
    print(p_str, flush=True)


logging.basicConfig(level= logging.DEBUG)


controller_message = {"client_id":0,
    "location_id":0,
    "model_name":"res18",
    "acc_limit":0.5,
    "latency_limit":1000,
    "real_latency":30,
    "bw":{"127.0.0.1":330,"127.0.0.2":330},
    "requests":{
          0:{
              "model_ver":0,
              "data_ver":1,
              "url":"***********"},
          1:{
              "model_ver":0,
              "data_ver":1,
              "url":"***********"}
              }
}




def get_time():
    t = time.localtime(time.time())
    return "%s:%s:%s"%(t.tm_hour,t.tm_min,t.tm_sec)



class a2_client():
    def __init__(self, ctrl_addr, ctrl_port, region_id, client_id, model_name, acc_lim, lat_lim, trace_file, comm_interval):
        # unbuffered_print(MODEL_VERSION,DATA_VERSION)
        self.dict_tool = db.dict_bytes()
        self.region_id = int(region_id)
        self.client_id = int(client_id)
        self.model_name = model_name
        self.acc_lim = float(acc_lim)
        self.lat_lim = float(lat_lim)
        self.comm_interval = int(comm_interval)
        self.complete_time = 0

        trace_data = None
        try:
            trace_data = list(np.load(trace_file))#ginger
        except:
            unbuffered_print("Reading trace file Error, using default settings")
            trace_data = [2] * 3600
        trace_data[0] += 1
        self.trace_data = trace_data[:self.comm_interval]
        self.total_requests_number = np.sum(self.trace_data)



        self.ctrl_addr = ctrl_addr
        self.ctrl_port = ctrl_port
        decision_dict = {
            "mobile_dcp_0":{
                "url":["http://18.136.13.110:10102/v1/models/mobile_dcp_0:classify"],
                "model_ver":0,
                "data_ver":2,
                "prob": 1.0
            }

        }
        self.config_prob_list = [[decision_dict],[1.0]]
        self.req_history = {}
        self.total_req_number = 0
        self.tf_proxy = tf_serving_cls()

        self.run = asyncio.run (self.main ())

    async def phase_one(self):
        bandwidths = self.get_bandwidths()
        # message = {}
        # message["bandwidth"] = bandwidths
        # message["history"] = self.req_history
        message = {}
        message["bw"] = bandwidths
        message["client_id"] = self.client_id
        message["location_id"] = self.region_id
        message["acc_limit"] = self.acc_lim
        message["latency_limit"] = self.lat_lim
        message["model_name"] = self.model_name
        message["requests"] = {}
        for i in range(self.total_requests_number):
            message["requests"][i] = {
                "model_ver":0,
                "data_ver":0,
                "url":"",
                "real_latency":0,
                "batch":0,
                "time":1
            }

        reader, writer = await asyncio.open_connection(
          self.ctrl_addr, self.ctrl_port,limit=2**128)
        # unbuffered_print("111111111111111")
        await self.dict_tool.send_dict2bytes (message, writer)
        # unbuffered_print(444444)
        unbuffered_print("Sent Phase one to controller")

        controller_msg = await self.dict_tool.read_bytes2dict(reader,writer)
        self.process_controller_msg(controller_msg)
        writer.close()

        # unbuffered_print(self.trace_data)
        # unbuffered_print(message)
        # self.process_controller_msg(1)


    async def client_core(self):
        await self.phase_one()
        print("Phase one Ended")
        trace_iter = itertools.cycle(self.trace_data)
        count = 0
        # start_time = timeit.default_timer()
        # async with aiohttp.ClientSession() as session:
        session = 0

        while True:
            count += 1
            num_request = next(trace_iter)
            unbuffered_print("%s Requests generated at %s, total: %s"%(num_request,get_time(),self.total_req_number))
            reqs = self.request_generator(count,num_request)

            await self.dispatch_requests(reqs,session) #ginger


            if count == len(self.trace_data):
                while len(self.req_history.keys()) != self.total_req_number:
                    # unbuffered_print(len(self.req_history.keys()),self.total_req_number)
                    pass

                # Communication
                end_time = timeit.default_timer()
                # self.complete_time = end_time - start_time
                unbuffered_print("Send to Controller & Wait settings")

                await self.send_to_controller()

                unbuffered_print("Restart Client")
                time.sleep(3)

                count = 0
                self.total_req_number = 0
                self.req_history = {}
            else:
                # unbuffered_print("Server sleep %s Secs"%1)
                time.sleep(1)



    def config_generator(self):
        if self.config_prob_list == None:
            unbuffered_print("Prob None Error")
            exit(0)

        config_list = self.config_prob_list[0]
        prob_list = self.config_prob_list[1]
        if not (0.9 < sum(prob_list) < 1.00001):
            raise ValueError("The probabilities are not normalized!")
        if len(config_list) != len(prob_list):
            raise ValueError("The length of two input lists are not match!")

        random_normalized_num = random.random()
        acc_prob = 0.0
        for item in zip(config_list, prob_list):
            acc_prob += item[1]
            if random_normalized_num < acc_prob:
                return item[0]


    def request_generator(self,count,num_request=2):
        request_list = []
        for i in range(num_request):
            self.total_req_number += 1
            config = self.config_generator()
            config["time"] = count
            req_dict = {
                "id" : self.total_req_number,
                "config":config
            }

            # self.req_history[self.total_req_number] = req_dict
            request_list.append(req_dict)

        return request_list


    async def dispatch_requests(self,reqs,session): #ginger
        lst = []
        # cls = tf_serving_cls ()
        # unbuffered_print(234352435243)
        # async with aiohttp.ClientSession () as session:
        unbuffered_print([item["id"] for item in reqs])
        # for item in reqs:
        #     # unbuffered_print(item["id"])
        #     lst.append (self.tf_proxy.tf_serving_request(item, self.req_history,session))
        lst = [self.tf_proxy.tf_serving_request(item, self.req_history,session) for item in reqs]
        # unbuffered_print(f'333333333,{len(lst)}')
        result = await asyncio.gather(*lst)
        unbuffered_print(result)
        # for item in reqs:
            # self.tf_proxy.tf_serving_request(item, self.req_history)
            # _thread.start_new_thread(self.tf_proxy.tf_serving_request,(item,self.req_history))


    def get_bandwidths(self):
        bw_dict = {}
        with open(PATH+'a2/bw_client/bw.txt', "r") as f:
            for item in f.readlines():
                item = item.split(',')
                print(item)
                bw_dict[item[0]]=float(item[2])
        return bw_dict


    def process_controller_msg(self,ctrl_msg):
        del ctrl_msg["type"]
        # ctrl_msg = {
        #     "mobile_dcp_0":{
        #         "url":["http://18.136.13.110:10102/v1/models/mobile_dcp_2:classify"],
        #         "model_ver":0,
        #         "data_ver":2,
        #         "prob": 1.0
        #     }
        #
        # }
        # unbuffered_print(ctrl_msg)
        config_list = []
        prob_list = []
        for model_version, values in ctrl_msg.items():
            unbuffered_print("%s ,%s"%(model_version, type(values)))
            config = {}
            config["model_name_version"] = f'{model_version[:6]}_dcp_{model_version[6]}'
            config["model_ver"] = values["model_ver"]
            config["data_ver"] = values["data_ver"]
            config["urls"] = values["url"]
            config["batch"] = values["batch"]
            prob_list.append(values["prob"])
            config_list.append(config)

        self.config_prob_list = [config_list,prob_list]


    async def send_to_controller(self):
        bandwidths = self.get_bandwidths()
        # message = {}
        # message["bandwidth"] = bandwidths
        # message["history"] = self.req_history
        message = {}
        message["bw"] = bandwidths
        message["client_id"] = self.client_id
        message["location_id"] = self.region_id
        message["acc_limit"] = self.acc_lim
        message["latency_limit"] = self.lat_lim
        message["requests"] = self.req_history
        message["model_name"] = self.model_name
       # message["complete_time"] = self.complete_time
       #  message["throughput"] = len(self.trace_data)/self.complete_time

        # unbuffered_print(message)
        reader, writer = await asyncio.open_connection(
          self.ctrl_addr, self.ctrl_port,limit=2**128)

        await self.dict_tool.send_dict2bytes (message, writer)
        unbuffered_print("Sent to controller")

        controller_msg = await self.dict_tool.read_bytes2dict(reader,writer)
        self.process_controller_msg(controller_msg)
        writer.close()


    async def main(self):
        self.allocate_done_que = asyncio.Queue ()
        self.allocat_que = asyncio.Queue()
        await asyncio.gather(self.client_core())


    # def delete_cpu0_docker(self):

if __name__ == "__main__":
    try:
        args = sys.argv
        region_id = args[1]
        client_id = args[2]
        model_name = args[3]
        acc_limit = args[4]
        latency_limit = args[5]
        trace_file = args[6]
        comm_interval = args[7]
        unbuffered_print(args)
        a2_client("18.139.237.235",8888,region_id, client_id, model_name, acc_limit, latency_limit, trace_file, comm_interval)
        # a2_client("192.168.1.104",8888,region_id, client_id, model_name, acc_limit, latency_limit, trace_file, comm_interval) #ginger

    except Exception as e:
        traces = traceback.format_exc()

        with open("/tmp/client_error.log","a") as f:
            f.writelines([str(traces),str(e)])
            f.close()
