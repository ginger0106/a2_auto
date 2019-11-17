# a2_auto
## auto_script
这是在 aws 上控制所有分布式节点的脚本
节点 ip 写在atuo_control_cpu.py的hosts 里
并且 执行参数也写在atuo_control_cpu.py里：
```
     act_client_dict = {
                'type': "activate",
                "config": {
                    "role": "client",
                    "region_id": i,
                    "client_number": 3, #每个 client machine 启动几个client 进程
                    "zipf_param": 3, # 每个 client 进程请求不同的 model 的流行度分布
                    "min_acc": 0.75, # 每个请求的最小 accuracy
                    "max_acc": 0.9, # 每个请求的最大 accuracy
                    "min_lat": 0.5, # 每个请求的最小latency
                    "max_lat": 5.0, # 每个请求的最大latency
                    "comm": 60, #second # 运行时间 跟 controller 要一直
                    "seed": i,
                    "mobile_trace":0, # mobile 模型的请求 trace， trace在/client/traces 文件夹下
                    "res18_trace":1 #res18 模型的请求 trace，trace在/client/traces 文件夹下
                } 
        }
   ```
   
代码内的所有 ip 和端口都需要注意
使用方法: 
- 每个节点（包括 controller client server） 都需要运行 auto_server.py
- 随机选择一个节点运行 atuo_control_cpu.py （运行 cpu 节点们）
- 然后输入 activate 启动，（此时要先启动 controller）
- 运行结束输入 terminate 来 kill掉所有进程
## client 
server.py中的 tf_serving_cls是发送图片的类，可以抽取出来在改写为本地运行版本
## server
a2_ml_server.py 是核心文件，可以抽取出来改写为本地运行版本
