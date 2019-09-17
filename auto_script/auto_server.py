import asyncio
import logging
import subprocess
import json
import sys
import dict_bytes as db
from dict_bytes import PATH
import time
import os,signal
import argparse


import time
# from .model import *
# from .measurement import *
# from .placement import Placement

logging.basicConfig(level=logging.DEBUG)


server_profile = {
    "mobile_dcp_0": {
        "port": [10101, 10102],
        "frac": 0.08,
        "batch": 2,
        "timeout": 10,
        "threads": 16,
        "device": "cpu"
    },
}

# controller　send decision


class auto_server():
    def __init__(self, addr="0.0.0.0", port="20020"):
        self.addr = addr
        self.port = port

        self.dict_tool = db.dict_bytes()
        self.process_pool = {}
        self.active_role = []
        self.output_dict = {}
        self.source_root = PATH+"a2_auto/"

        self.init_source()
        self.run = asyncio.run(self.main())

    def init_source(self):
        cmd = "git clone https://github.com/ginger0106/a2_auto_ginger %s" % self.source_root
        pass


    async def handle_socket(self, reader, writer):


        receive_data = await self.dict_tool.read_bytes2dict(reader, writer)
        print("receied: ", receive_data)
        return_data = None
        if receive_data['type'] == 'pull':
            return_data = self.pull_latest_source()

        elif receive_data['type'] == 'activate':
            act_config = receive_data["config"]
            return_data = self.activate_role(act_config)

        elif receive_data['type'] == 'terminate':
            return_data = self.terminate_process()

        elif receive_data['type'] == 'status':
            return_data = self.get_status()

        elif receive_data['type'] == 'output':
            ouput_config = receive_data["config"]
            return_data = self.get_output(ouput_config)
        elif receive_data['type'] == 'clean':
            return_data = self.clean_zombie()
        elif receive_data['type'] == 'cmd':
            cmd = receive_data["cmd"]
            p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
            p.wait()
            p_str = ""
            for item in p.stdout.readlines():
                p_str += item.decode()
            return_data = {"Result":p_str}
        elif receive_data['type'] == 'bandwidth':
            act_config = receive_data["config"]
            return_data = await self.activate_role_bw(act_config)

        await self.dict_tool.send_dict2bytes(return_data, writer)
        writer.close()
    async def activate_role_bw(self,config):
        role = config["role"]

        if role in self.process_pool.keys():
            return {"result_code": 0,"result_info":"Role already activated"}


        if role == "server":
            server_script_path = PATH+"a2_auto/server_src/server_main.py"
            device = config["device"]
            cmd = "python3.7 %s %s %s" % (server_script_path, device,self.addr) #ginger
            print(cmd)
            # return


        elif role == "client":
            region_id = config["region_id"]
            client_number = config["client_number"]
            zipf_param = config["zipf_param"]
            min_acc = config["min_acc"]
            max_acc = config["max_acc"]
            min_lat = config["min_lat"]
            max_lat = config["max_lat"]
            comm_interval = config["comm"]
            random_seed = config["seed"]
            mobile_trace = config["mobile_trace"]
            res18_trace = config["res18_trace"]

            param_list = "%s %s %s %s %s %s %s %s %s %s %s"
            param_list = param_list % (region_id, client_number, zipf_param,
                                        min_acc, max_acc, min_lat, max_lat,
                                        comm_interval, random_seed, mobile_trace,res18_trace)

            client_script_path = PATH+"a2_auto/client/client_init.py"

            cmd = "python3.7 %s %s"%(client_script_path, param_list)
            print(cmd)
            # return

        elif role == "controller":
            cmd = "python3.7 controller.py"

        elif role == "scheduler":
            gpu_server_list = config["gpu_server"]
            cpu_server_list = config["cpu_server"]

            scheduler_path = PATH+"a2_auto/server_src/cluster_scheduler.py"

            cmd = f"python3.7 %s" % scheduler_path

            for item in gpu_server_list:
                cmd = cmd + item + " "

            cmd = cmd + "s "

            for item in cpu_server_list:
                cmd = cmd + item + " "
            print(cmd)
            # return
        elif role == "test":
            cmd = "python3.7 print_test.py"
        else:
            return {"result_code": 0,"result_info":"Undefined Type"}

        logfile = "/tmp/%s.log"%role
        cmd = cmd + " > %s"%logfile
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,preexec_fn=os.setsid)

        # if role in self.process_pool.keys():
        #     self.process_pool[role].append(p)
        #     self.output_dict[role].append("")
        # else:
        self.process_pool[role] = p
        self.output_dict[role] = logfile

        bw_path = PATH+"a2/bw_client/control_bw.py"
        cmd = f"sudo setcap cap_net_raw,cap_net_admin+ep /bin/ip; python3.7 {bw_path} -p {PATH}a2/bw_client/cpu_srver.txt -b 750"
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,preexec_fn=os.setsid)

        await asyncio.sleep(60)

        return {"result_code": 1,"result_info":p.stdout.readlines()}

    def change_bw(self):
        cmd = "sudo setcao cap_net_raw,cap_net_admin+ep /bin/ip"
        cmd = "cd %s; git pull" % self.source_root
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        p.wait()
        p_str = ""
        for item in p.stdout.readlines():
            p_str += item.decode()
        return {"result_code": 1,"result_info":p_str}


    def clean_zombie(self):
        to_remove = []
        for role, p in self.process_pool.items():
            if p.poll() is not None:
                to_remove.append(role)
        for item in to_remove:
            del self.process_pool[item]
            del self.output_dict[item]


    def pull_latest_source(self):
        cmd = "cd %s; git pull" % self.source_root
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        p.wait()
        p_str = ""
        for item in p.stdout.readlines():
            p_str += item.decode()
        return {"result_code": 1,"result_info":p_str}

    def activate_role(self,config):
        role = config["role"]

        if role in self.process_pool.keys():
            return {"result_code": 0,"result_info":"Role already activated"}


        if role == "server":
            server_script_path = PATH+"a2_auto/server_src/server_main.py"
            device = config["device"]
            cmd = "python3.7 %s %s %s" % (server_script_path, device,self.addr) #ginger
            print(cmd)
            # return


        elif role == "client":
            region_id = config["region_id"]
            client_number = config["client_number"]
            zipf_param = config["zipf_param"]
            min_acc = config["min_acc"]
            max_acc = config["max_acc"]
            min_lat = config["min_lat"]
            max_lat = config["max_lat"]
            comm_interval = config["comm"]
            random_seed = config["seed"]
            mobile_trace = config["mobile_trace"]
            res18_trace = config["res18_trace"]

            param_list = "%s %s %s %s %s %s %s %s %s %s %s"
            param_list = param_list % (region_id, client_number, zipf_param,
                                        min_acc, max_acc, min_lat, max_lat,
                                        comm_interval, random_seed, mobile_trace,res18_trace)

            client_script_path = PATH+"a2_auto/client/client_init.py"

            cmd = "python3.7 %s %s"%(client_script_path, param_list)
            print(cmd)
            # return

        elif role == "controller":
            cmd = "python3.7 controller.py"

        elif role == "scheduler":
            gpu_server_list = config["gpu_server"]
            cpu_server_list = config["cpu_server"]

            scheduler_path = PATH+"a2_auto/server_src/cluster_scheduler.py"

            cmd = f"python3.7 %s" % scheduler_path

            for item in gpu_server_list:
                cmd = cmd + item + " "

            cmd = cmd + "s "

            for item in cpu_server_list:
                cmd = cmd + item + " "
            print(cmd)
            # return
        elif role == "test":
            cmd = "python3.7 print_test.py"
        else:
            return {"result_code": 0,"result_info":"Undefined Type"}

        logfile = "/tmp/%s.log"%role
        cmd = cmd + " > %s"%logfile
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,preexec_fn=os.setsid)

        # if role in self.process_pool.keys():
        #     self.process_pool[role].append(p)
        #     self.output_dict[role].append("")
        # else:
        self.process_pool[role] = p
        self.output_dict[role] = logfile

        return {"result_code": 1,"result_info":"Activate Done"}


    def terminate_process(self):
        for role, p in self.process_pool.items():
            if p.poll() is None:
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                except:
                    print("Error killing %s"%role)

        try:
            f = open("/tmp/client_pid.txt","r")
            for item in f.readlines():
                try:
                    pid = int(item)
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                except:
                    pass
        except:
            pass


        self.process_pool = {}
        self.output_dict = {}
        return {"result_code": 1,"result_info":"Terminate Done"}

    def get_status(self):
        status_dict = {}
        for role, p in self.process_pool.items():
            returncode = p.poll()
            if returncode is None:
                status_dict[role] = "running"
            else:
                status_dict[role] = f"exit{returncode}"

        return status_dict

    def get_output(self,config):
        target = config["role"]
        with open(self.output_dict[target],"r") as f:

            return {"output":f.readlines()}


    # async def gather_process_output(self):
    #     while True:
    #         await asyncio.sleep(3)
    #         for role, p in self.process_pool.items():
    #             returncode = p.poll()
    #             if returncode is None:
    #                 outline = p.stdout.readline().decode()
    #                 print(outline)
    #                 self.output_dict[role] += outline
    #                 # print(p.stdout.readable())


    async def socket(self):
        server = await asyncio.start_server(
            self.handle_socket, self.addr, self.port)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    async def main(self):
        await asyncio.gather(self.socket())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser ()
    parser.add_argument ("-a", default='0.0.0.0', type=str, help='controller_ip')  # server ip addr
    # version_stg,device_type,time_slot,con_addr,con_port,client_num
    args = parser.parse_args ()
    a2 = auto_server(args.a)
