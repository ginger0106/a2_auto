import asyncio
import logging
import subprocess
import json
from shlex import quote
from . import dict_bytes as db
from .dict_bytes import PATH
import os
# from .model import *
# from .measurement import *
# from .placement import Placement

logging.basicConfig(level= logging.DEBUG)

def unbuffered_print(p_str):
    print(p_str, flush=True)

server_profile1 = {
    "type":"allocation",
    "mobile_dcp_0":{
        "port":[10101,10102],
        "frac":0.08,
        "batch":2,
        "timeout":10,
        "threads":16
    }
}




#data send:
## --> client bw = {'type':'bw', 'content':'a'*800}
## --> client load = {'type': 'load','time':time, 'mobile_dcp_1':{'cpu': '2.05%','net':'20/30KB' },'mobile_dcp_2':{'cpu': '2.05%','net':'20/30KB' }...}
## --> controller allocate_done_stats = {'type':'step','step':step, 'addr':addr}

# data receive:
#<--client  bw = {'type':'bw', 'content':'a'*800}0000000000000
#<--controller allocation ={'type':'allocation', 'addr' = addr, 'step' = step ,{self.model_name[i]: {'port': self.port[i], 'cpu': round (cpu_allocation[i], 2), 'step': 0}
#                  for i in range (len (self.model_zoo))}}

# controller　send decision
class a2_ml_server ():
    def __init__(self,addr="0.0.0.0",port="9949",device="cpu"):
        # print(MODEL_VERSION,DATA_VERSION)
        self.dict_tool = db.dict_bytes()
        self.device = device
        self.port = port
        self.addr = addr
        self.server_load_send = {'type':'load'}
        self.server_allocat_get = {}
        self.model_root = PATH+"Infocom19/exp/real_exp/ml_server/models/"
        self.config_root = PATH+"model_root/" + "config_root/"
        self.scheduler_writer = None
        self.run = asyncio.run (self.main ())


    async def handle_socket(self, reader, writer):

        receive_data = await self.dict_tool.read_bytes2dict(reader,writer)
        if receive_data['type'] == 'allocation':

            self.server_allocat_get = receive_data

            self.scheduler_writer = writer
            unbuffered_print(receive_data)

            logging.info('Recive allocation from controller!')

            await self.allocat_que.put (self.server_allocat_get)


        else:
            pass
            # while not receive_data:
            #     writer.close()
            #     asyncio.run (self.main ())
            #     data = await reader.read (1024)
            #     message = data.decode ()


    def clear_docker(self):
        # os.system('docker stop `docker ps -a -q`')
        # os.system('docker rm `docker ps -a -q`')
        cmd1 = 'docker stop `docker ps -a -q`'
        cmd2 = 'docker rm `docker ps -a -q`'
        p = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        p = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()

        unbuffered_print("clear docker")
        unbuffered_print('done!')


    async def allocator(self):
        # """"""
        #
        # await self.docker_run(server_profile1)

        while True:
            unbuffered_print("Wait Profile")
            allocat_dict = await self.allocat_que.get()
            self.clear_docker()
            await self.docker_run(allocat_dict)


    # async def serverload(self):
    #     return
    #     while True:
    #         await asyncio.sleep(1)
    #         formatt = "{\"container\":\"{{ .Name }}\",\"net\":\"{{ .NetIO }}\",\"memory\":{\"raw\":\"{{ .MemUsage }}\",\"percent\":\"{{ .MemPerc }}\"}," \
    #                   "\"cpu\":\"{{ .CPUPerc }}\"}".strip (
    #             '\n')
    #         cmd = 'docker stats --no-stream --format {}'.format (quote (formatt))
    #         proc = await asyncio.create_subprocess_shell (
    #             cmd,
    #             stdout=asyncio.subprocess.PIPE,
    #             stderr=asyncio.subprocess.PIPE)
    #         stdout, stderr = await proc.communicate ()
    #         # self.server_load = stdout.decode().splitlines()
    #         # unbuffered_print(stdout.decode().splitlines())
    #         self.server_load = [json.loads (i) for i in stdout.decode().splitlines()]
    #         # self.server_load_send = {i['container']:{'cpu':i['cpu'],'net':i['net'] } for i in self.server_load}
    #         self.server_load_send = {i['container']:i['cpu'] for i in self.server_load}
    #         self.server_load_send['type']= 'load'
    #         unbuffered_print(self.server_load_send)
    #         logging.info('Update: load update')
    #         # unbuffered_print(stdout.decode().splitlines())


    def update_config_file(self, model_name,config):

        config_file = "%s%s.config"%(self.config_root,model_name)
        # return config_file
        if not os.path.exists(self.config_root):
            os.mkdir(self.config_root)
        with open(config_file,"w") as f:
            f.write("max_batch_size {value: %s} \n"% config["batch"])
            f.write("batch_timeout_micros {value: %s} \n"% config["timeout"])
            f.write("num_batch_threads {value: %s} \n"% config["threads"])
            f.close()
        return config_file





    async def docker_run(self,decision_dict):
        unbuffered_print('docker run')
        del decision_dict["type"]
        gpu_count = 0

        # decision_dict = self.init_allocate()
        for model_name, config in decision_dict.items ():
            ports = config["port"]
            config_file = self.update_config_file(model_name,config)
            frac = config["frac"]

            for p in ports:
                if self.device == "gpu":
                    gpu_count += 1
                    cmd_run = f'NV_GPU="{gpu_count}" nvidia-docker run --runtime=nvidia --name="{model_name + "_"+str(p)}"  -p {p}:8501  '\
                            f'--mount type=bind,source={self.model_root + model_name}/,target=/models/{model_name} ' \
                            f'--mount type=bind,source={config_file},target=/models/batching_parameters.config ' \
                            f'-e MODEL_NAME={model_name} -t tensorflow/serving:latest-gpu --per_process_gpu_memory_fraction={frac} '  \
                            f'--enable_batching=true --batching_parameters_file=/models/batching_parameters.config &' \
                            # f'--rest_api_timeout_in_ms=2000 &'
                else:
                    cmd_run = f'docker run --cpus={frac} --name="{model_name + "_"+str(p)}" -p {p}:8501'\
                            f' --mount type=bind,source={self.model_root + model_name}/,target=/models/{model_name}'\
                            f' --mount type=bind,source={config_file},target=/models/batching_parameters.config'\
                            f' -e MODEL_NAME={model_name} -t tensorflow/serving:latest ' \
                            f' --enable_batching=true --batching_parameters_file=/models/batching_parameters.config &' \
                            # f' --rest_api_timeout_in_ms=3000 &'

                    # f' --enable_batching=true --batching_parameters_file=/models/batching_parameters.config' \

                unbuffered_print(cmd_run)
                output = subprocess.Popen(cmd_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                # unbuffered_print ('err:'+str(output.stderr))
                # unbuffered_print ('out' + str (output.stdout.readlines()))



        result = {"result_code":1,"result_info":"Done"}
        await self.dict_tool.send_dict2bytes(result,self.scheduler_writer)
        self.scheduler_writer.close()







    async def socket(self):
        server = await asyncio.start_server (
            self.handle_socket, self.addr, self.port)

        addr = server.sockets[0].getsockname ()
        print (f'Serving on {addr}')

        async with server:
            await server.serve_forever ()

    async def main(self):
        self.allocate_done_que = asyncio.Queue ()
        self.allocat_que = asyncio.Queue()
        await asyncio.gather(self.socket(),self.allocator())


    # def delete_cpu0_docker(self):
