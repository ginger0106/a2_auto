import logging
import base64
import requests
import timeit
import time
import random
import traceback
from PIL import Image
from io import  BytesIO
import aiohttp
import json
import asyncio
from dict_bytes import PATH

def get_time():
    t = time.localtime(time.time())
    return "%s:%s:%s"%(t.tm_hour,t.tm_min,t.tm_sec)

def unbuffered_print(p_str):
    print(p_str, flush=True)

class tf_serving_cls():
    def __init__(self):
        self.image_path = PATH+'a2_auto/client/cat.jpg'

    def data_preprocess(self,data_path, data_version):
        # compress data
        size = int (224 - data_version * 12)
        data_size = (size, size)
        im = Image.open (data_path)
        im = im.resize (data_size, Image.ANTIALIAS)
        image_io = BytesIO ()
        im.save (image_io, 'JPEG')
        byte_data = image_io.getvalue ()
        image_bytes = base64.b64encode (byte_data).decode ('utf-8')
        return image_bytes

    async def tf_serving_request(self, decision_dict,req_recorder,session):
        # print(decision_dict)
        config = decision_dict["config"]
        # unbuffered_print(config)
        model_version = config['model_ver']
        data_version = config['data_ver']
        url = random.sample(config["urls"],1)[0]
        # r_time = config['time']
        # r
        # r_time = get_time()
        r_time = time.time()
        batch = config["batch"]
        count = 0
        unbuffered_print("Sending request: %s"%decision_dict["id"])
        unbuffered_print(f'!!!!!!!!!! count is {count}')
        # start_time = timeit.default_timer ()


        # await asyncio.sleep(0.5)
        # end_time = timeit.default_timer()
        # latency = end_time - start_time
        #
        # temp = {}
        # temp["real_latency"] = latency
        # temp["url"] = url
        # temp["model_ver"] = model_version
        # temp["data_ver"] = data_version
        # temp["time"] = r_time
        # temp["batch"] = batch
        # # temp[""]
        # req_recorder[decision_dict["id"]] = temp
        # unbuffered_print(
        #     'Request: %s Prediction class: %s, avg latency: %.2f ms' % (decision_dict["id"], 'cat', latency * 1000))
        # return "ok"

        while count <= 9:
            try:
                unbuffered_print("!!!!! Sending request: %s" % decision_dict["id"])

                # unbuffered_print("Sending Requests for %s times"%count)
                SERVER_URL = url
                image_bytes = self.data_preprocess (self.image_path, data_version)
                predict_request = '{"signature_name":"serving_default" ,"examples":[{"image/encoded":{"b64": "%s"}}]}' % image_bytes

                start_time = timeit.default_timer ()

                # await asyncio.sleep(0.5)

                response = requests.post(SERVER_URL, data=predict_request)
                response.raise_for_status ()
                prediction = response.json ()['results'][0]
                try:
                    start_time = timeit.default_timer ()
                    async with session.post (SERVER_URL, data=predict_request) as response:
                        # response
                        if response.status ==200:
                            await response.text ()
                            unbuffered_print('OK! 200')
                        else:
                            unbuffered_print(response.status)


                # try:
                #     unbuffered_print (1111)
                #     unbuffered_print (prediction)
                #     # prediction = (json.loads (prediction)['results'][0])
                # except KeyError:
                #     unbuffered_print (2222)
                #     unbuffered_print (prediction)
                #     await asyncio.sleep(0.5)

                        end_time = timeit.default_timer ()
                        latency = end_time-start_time

                        temp = {}
                        temp["real_latency"] = latency
                        temp["url"] = SERVER_URL
                        temp["model_ver"] = model_version
                        temp["data_ver"] = data_version
                        temp["time"] = r_time
                        temp["batch"] = batch
                        # temp[""]
                        req_recorder[decision_dict["id"]] = temp
                        unbuffered_print('Request: %s Prediction class: %s, avg latency: %.2f ms'%(decision_dict["id"], 'cat',latency*1000))
                        return "ok"
                except Exception:
                    unbuffered_print(Exception)

            except Exception as e:
                traces = traceback.format_exc()
                time.sleep(1)
                count += 1

                with open("/tmp/client_error.log","a") as f:
                    f.writelines([str(traces),str(e)])
                    f.close()


        # latency = 0.1*10
        # unbuffered_print("    sleep %s" % latency)
        # time.sleep(latency)
