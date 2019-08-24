import  asyncio
from dict_bytes import dict_bytes

class Result_proxy:
    def __init__(self):
        self.result_dict = {}

async def sendmsg(host, port, act_dict):  #
    if host == "":
        return
    print(host,port)
    reader, writer = await asyncio.open_connection (
        host, port)

    # print(123123)
    test_dict = act_dict

    await dict_bytes().send_dict2bytes (test_dict, writer)
    # print(f'send msg:{test_dict}')
    text = await dict_bytes().read_bytes2dict(reader,writer)
    print(text)

    writer.close()


async def mysendmsg(host, port, act_dict,r = None):  #
    if host == "":
        return
    reader, writer = await asyncio.open_connection (
        host, port)

    # print(123123)
    test_dict = act_dict

    await dict_bytes().send_dict2bytes (test_dict, writer)
    # print(f'send msg:{test_dict}')
    text = await dict_bytes().read_bytes2dict(reader,writer)
    print(text)
    r.result_dict = text

    writer.close()


def activate_hosts(hosts):
    for i in range(len(hosts)):
        region_ip_dict = hosts["region_%s"%i]
        scheduler_ip = region_ip_dict["scheduler"]
        cpu_server_ip = region_ip_dict["cpu_server"]
        gpu_server_ip = region_ip_dict["gpu_server"]
        client_ip = region_ip_dict["client"]

        act_scheduler_dict = {
                'type': "activate",
                "config": {
                    "role": "scheduler",
                    "gpu_server":[gpu_server_ip],
                    "cpu_server":[cpu_server_ip],
                }
        }
        scheduler_ip = region_ip_dict["scheduler"]
        asyncio.run(sendmsg(scheduler_ip,20020,act_scheduler_dict))

        act_server_dict = {
                'type': "activate",
                "config": {
                    "role": "server",
                    "device": "cpu"
                }
        }
       #asyncio.run(sendmsg(gpu_server_ip,20020,act_server_dict))

        act_server_dict = {
                'type': "activate",
                "config": {
                    "role": "server",
                    "device": "cpu"
                }
        }
        asyncio.run(sendmsg(cpu_server_ip,20020,act_server_dict))

        act_client_dict = {
                'type': "activate",
                "config": {
                    "role": "client",
                    "region_id": i,
                    "client_number": 10,
                    "zipf_param": 2,
                    "min_acc": 0.6,
                    "max_acc": 0.9,
                    "min_lat": 1.0,
                    "max_lat": 4.0,
                    "comm": 60, #second
                    "seed": i,
                    "mobile_trace":0,
                    "res18_trace":1
                }
        }
        asyncio.run(sendmsg(client_ip,20020,act_client_dict))

def terminate_all(hosts):
    for i in range(len(hosts)):
        region_ip_dict = hosts["region_%s"%i]
        # scheduler_ip = region_ip_dict["scheduler"]
        # cpu_server_ip = region_ip_dict["cpu_server"]
        # gpu_server_ip = region_ip_dict["scheduler"]
        # client_ip = region_ip_dict["client"]
        for role,ip in region_ip_dict.items():
            end_dict = {
                'type': "terminate",
            }
            asyncio.run(sendmsg(ip,20020,end_dict))

def pull_all(hosts):
    for i in range(len(hosts)):
        region_ip_dict = hosts["region_%s"%i]
        # scheduler_ip = region_ip_dict["scheduler"]
        # cpu_server_ip = region_ip_dict["cpu_server"]
        # gpu_server_ip = region_ip_dict["scheduler"]
        # client_ip = region_ip_dict["client"]
        for role,ip in region_ip_dict.items():
            print("send pull to %s"%ip)
            pull_dict = {
                'type': "pull",
            }
            asyncio.run(sendmsg(ip,20020,pull_dict))

def status_all(hosts):
    status_result_dict = {}
    for i in range(len(hosts)):
        region_ip_dict = hosts["region_%s"%i]
        status_result_dict["region_%s"%i] = {}
        # scheduler_ip = region_ip_dict["scheduler"]
        # cpu_server_ip = region_ip_dict["cpu_server"]
        # gpu_server_ip = region_ip_dict["scheduler"]
        # client_ip = region_ip_dict["client"]
        for role,ip in region_ip_dict.items():
            status_dict = {
                'type': "status",
            }
            r = Result_proxy()
            ip = hosts["region_%s"%i][role]
            asyncio.run(mysendmsg(ip,20020,status_dict,r))
            try:
                if role == "cpu_server" or role == "gpu_server":
                    status_result_dict["region_%s"%i][role] = r.result_dict["server"]
                else:
                    status_result_dict["region_%s"%i][role] = r.result_dict[role]
            except:
                status_result_dict["region_%s"%i][role] = {"Not Activated"}

    for region, status_r in status_result_dict.items():
        print(region)
        for r,s in status_r.items():
            print("    %s : %s "%(r,s))
    # print(status_result_dict)







if __name__ == "__main__":
    act_client_dict = {
            'type': "activate",
            "config": {
                "role": "client",
                "region_id": 0,
                "client_number": 2,
                "zipf_param": 2,
                "min_acc": 0.85,
                "max_acc": 0.9,
                "min_lat": 1.0,
                "max_lat": 2.0,
                "comm": 12,
                "seed": 0,
                "comm": 5,
                "seed": 0,
                "mobile_trace":0,
                "res18_trace":1
            }
    }

    act_scheduler_dict = {
            'type': "activate",
            "config": {
                "role": "scheduler",
                "gpu_server":["127.0.0.1", "127.0.0.2"],
                "cpu_server":["127.0.0.3", "127.0.0.4"],
            }
    }

    act_server_dict = {
            'type': "activate",
            "config": {
                "role": "server",
                "device": "gpu"
            }
    }

    act_test_dict = {
            'type': "activate",
            "config": {
                "role": "test"
            }
    }


    status_dict = {
        'type': "status",
    }

    pull_dict = {
        'type': "pull",
    }

    output_dict = {
        'type': "output",
        "config": {
            "role": "client"
        }
    }

    end_dict = {
        'type': "terminate",
    }

    hosts = {
        "region_0":{
            "scheduler":"18.136.13.110",
           # "gpu_server":"18.139.235.198",
            "gpu_server":"",
            "cpu_server":"18.136.13.110",
            "client":"18.139.237.235"
           # "client":""
        },
        "region_1":{
            "scheduler":"13.235.174.165",
          #  "gpu_server":"13.235.118.34",
            "gpu_server":"",
            "cpu_server":"13.235.174.165",
            "client":"13.233.6.157"
            #"client":""
        },
    #     # "region_9":{
    #     #     "test":"127.0.0.1",
    #     # },
    # }
    # hosts = {
    #     "region_0":{
    #         "scheduler":"127.0.0.1",
    #        # "gpu_server":"18.139.235.198",
    #         "gpu_server":"",
    #         "cpu_server":"127.0.0.1",
    #         "client":"127.0.0.1"
    #        # "client":""
    #     },
        # "region_1":{
        #     "scheduler":"0.0.0.0",
        #   #  "gpu_server":"13.235.118.34",
        #     "gpu_server":"",
        #     "cpu_server":"0.0.0.0",
        #     "client":"0.0.0.0"
        #     #"client":""
        # },

        # "region_9":{
        #     "test":"127.0.0.1",
        # },
    }

    # cmd_dict = {
    #     "type":"cmd",
    #     "cmd":"hostname"
    #
    # }
    # asyncio.run(sendmsg("3.1.239.165",20020,cmd_dict))

    while True:
        print("Enter Command:")
        command = input()
        if command == "status":
            print("Enter region id and role:")
            [region_id, role] = input().split(" ")
            status_dict = {
                'type': "status",
            }
            ip = hosts["region_%s"%region_id][role]
            asyncio.run(sendmsg(ip,20020,status_dict))
        elif command == "output":
            print("Enter region id and role:")
            [region_id, role] = input().split(" ")
            if role == "cpu_server" or role == "gpu_server":

                output_dict = {
                    'type': "output",
                    "config": {
                        "role": "server"
                    }
                }
            else:
                output_dict = {
                    'type': "output",
                    "config": {
                        "role": role
                    }
                }
            ip = hosts["region_%s"%region_id][role]
            asyncio.run(sendmsg(ip,20020,output_dict))

        elif command == "terminate":
            terminate_all(hosts)
        elif command == "pull":
            pull_all(hosts)
        elif command == "status_all":
            status_all(hosts)
        elif command == "activate":
            activate_hosts(hosts)
        elif command=="cmd":
            print("Enter region id and role:")
            [region_id, role] = input().split(" ")
            ip = hosts["region_%s"%region_id][role]

            print("CMD Mode (exit):")
            sh_cmd = input()
            print("cmd is: %s"%sh_cmd)
            while sh_cmd != "exit":
                cmd_dict = {
                    "type":"cmd",
                    "cmd":sh_cmd
                }
                asyncio.run(sendmsg(ip,20020,cmd_dict))
                sh_cmd = input()


    #
    #
    # if 1:
    #     print("start server, scheduler and client")
    #     asyncio.run(sendmsg('3.1.239.165',20020,act_scheduler_dict))
    #     asyncio.run(sendmsg('3.1.239.165',20020,act_server_dict))
    #     asyncio.run(sendmsg('3.1.239.165',20020,act_client_dict))
    #     input()
    #     print("\n\n")
    #     print("status")
    #     asyncio.run(sendmsg('3.1.239.165',20020,status_dict))
    #     input()
    #     print("output of client")
    #     asyncio.run(sendmsg('3.1.239.165',20020,output_dict))
    #     input()
    #     print("terminatesta")
    #     asyncio.run(sendmsg('3.1.239.165',20020,end_dict))
    #     asyncio.run(sendmsg('3.1.239.165',20020,status_dict))
    # else:

    #
    # # asyncio.run(sendmsg('3.1.239.165',20020,act_server_dict))
    # # asyncio.run(sendmsg('127.0.0.1',20020,end_dict))
