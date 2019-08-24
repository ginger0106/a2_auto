import asyncio
import logging
import subprocess
import json
from shlex import quote
import server.dict_bytes as db
import os
import time
import sys
import traceback
# from .model import *
# from .measurement import *
# from .placement import Placement



def unbuffered_print(p_str):
    print(p_str, flush=True)

logging.basicConfig(level=logging.DEBUG)

server_profile = {
    "mobile_dcp_0" : {
        "port" : [10101,10102],
        "frac":0.08,
        "batch":2,
        "timeout":10,
        "threads":16,
        "device":"cpu"
    },
}




# controller　send decision
class cluster_scheduler ():
    def __init__(self,addr="0.0.0.0",port="9000",cpu_server_list = [], gpu_server_list = []):
        # unbuffered_print(MODEL_VERSION,DATA_VERSION)
        self.dict_tool = db.dict_bytes()
        # self.p_ij = np.zeros(MODEL_VERSION,DATA_VERSION))
        # self.placement_ins = Placement(place_policy)
        self.port = port
        self.addr = addr
        self.server_load_send = {'type':'load'}
        self.server_allocat_get = {}
        self.cpu_server_list = cpu_server_list
        self.gpu_server_list = gpu_server_list
        if len(cpu_server_list) + len(gpu_server_list) == 0:
            unbuffered_print("No avaliable server")

        self.server_port = 9949

        self.controller_writer = None


        self.run = asyncio.run (self.main ())

    async def handle_socket(self, reader, writer):
        # writer.write ('start connection'.encode ())
        if True:
            receive_data = await self.dict_tool.read_bytes2dict(reader,writer)
            if receive_data['type'] == 'allocation':
                # {'type':'allocation', 'allocation': {},'step':1}
                self.server_allocat_get = receive_data
                # unbuffered_print(receive_data,1111)
                logging.info('Recive allocation from controller at %s '%time.time())
                await self.allocat_que.put (self.server_allocat_get)

                self.controller_writer = writer

            else:
                pass
                # while not receive_data:
                #     writer.close()
                #     asyncio.run (self.main ())
                #     data = await reader.read (1024)
                #     message = data.decode ()


    def init_allocate(self):
        return server_profile

    async def receiver(self):

        # await self.server_run(self.init_allocate())

        while True:
            allocat_dict = await self.allocat_que.get()
            unbuffered_print("Msg from Controller: %s" % allocat_dict)
            schedule_result = await self.server_run(allocat_dict)
            unbuffered_print("Send back To ctrl: %s"%schedule_result)
            await self.dict_tool.send_dict2bytes(schedule_result,self.controller_writer)
            unbuffered_print("Send back Done ")
            self.controller_writer.close()


    async def send_decision(self,decision_dict,target_ip):
        decision_dict["type"] = "allocation"
        unbuffered_print("%s , %s "%(target_ip, self.server_port))
        reader, writer = await asyncio.open_connection (
            target_ip, self.server_port)
        await self.dict_tool.send_dict2bytes (decision_dict, writer)
        unbuffered_print("Send %s to %s"%(decision_dict,target_ip))

        return reader,writer

    async def server_run(self,controller_msg):
        if "type" in controller_msg.keys():
            del controller_msg["type"]

        cpu_message = {}
        gpu_message = {}



        for model_name, config in controller_msg.items():
            model_name = model_name[1:]
            if config["device"] == "cpu":
                cpu_message[model_name] = config
            else:
                gpu_message[model_name] = config

        connection_pool = []
        for cpu_server in self.cpu_server_list:
             connection_pool.append(await self.send_decision(cpu_message,cpu_server))

        for gpu_server in self.gpu_server_list:
            connection_pool.append(await self.send_decision(gpu_message,gpu_server))

        for reader,writer in connection_pool:
            server_result = await self.dict_tool.read_bytes2dict(reader,writer)
            unbuffered_print(server_result)
            if server_result["result_code"] != 1:
                unbuffered_print("Server Error")
            writer.close()

        unbuffered_print("Server scheduled.")

        return {"result_code":1,"result_info":"Done"}





    async def socket(self):
        server = await asyncio.start_server (
            self.handle_socket, self.addr, self.port)

        addr = server.sockets[0].getsockname ()
        unbuffered_print(f'Serving on {addr}')

        async with server:
            await server.serve_forever ()

    async def main(self):
        self.allocate_done_que = asyncio.Queue ()
        self.allocat_que = asyncio.Queue()
        await asyncio.gather(self.socket(),self.receiver())


    # def delete_cpu0_docker(self):


if __name__=="__main__":
    try:
        args = sys.argv[1:]
        gpu_server = []
        cpu_server = []

        flag = False
        for item in args:
            if item == "s":
                flag = True
                continue
            if flag:
                cpu_server.append(item)
            else:
                gpu_server.append(item)

        a2 = cluster_scheduler(cpu_server_list = cpu_server, gpu_server_list=gpu_server)
    except Exception as e:
        traces = traceback.format_exc()

        with open("/tmp/scheduler.log","a") as f:
            f.writelines([str(traces),str(e)])
            f.close()
