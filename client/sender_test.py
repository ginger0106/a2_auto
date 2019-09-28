import logging
import base64
import requests
import timeit
import time
import random
import traceback
from PIL import Image
from io import  BytesIO
import threading
import aiohttp
import asyncio
import json


def unbuffered_print(p_str):
    print(p_str, flush=True)

class tf_serving_cls():
    def __init__(self):
        self.image_path = 'cat.jpg'


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

    async def tf_serving_request(self, session,url="http://127.0.0.1:8500/v1/models/res18_dcp_3:classify"):
        data_version = 11
        SERVER_URL = url
        image_bytes = self.data_preprocess (self.image_path, data_version)
        predict_request = '{"signature_name":"serving_default" ,"examples":[{"image/encoded":{"b64": "%s"}}]}' % image_bytes

        start_time = timeit.default_timer()
        # s = requests.session()
        # aiohttp.request()
        # print(timeit.default_timer)
        async with session.post (SERVER_URL, data=predict_request) as response:
            # response
            if response.status == 200:
                prediction = await response.text()
            prediction = (json.loads(prediction)['results'][0])
        # print(prediction)
        # print(response.status_code)
        #     response.raise_for_status ()
        #     response.status()

            # prediction = response.json ()['results'][0]

        end_time = timeit.default_timer ()
        latency = end_time-start_time

        print('Prediction class: %s, avg latency: %.2f ms'%(prediction[0][0],latency*1000))

        return

async def main():
    lst = []
    cls = tf_serving_cls()
    async with aiohttp.ClientSession() as session:
        for j in range(10):
            # for i in range(10):
            print(j)
            lst.append(cls.tf_serving_request(session))
        await asyncio.gather(*lst)

asyncio.run(main())
        # print(j,i)

        # cls.tf_serving_request()
        # t = threading.Thread(target=cls.tf_serving_request)
        # t.start()
        # t.join()
        # print(j,i)

    # print(f'id={i})
