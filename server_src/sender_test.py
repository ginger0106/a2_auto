import  asyncio
from server.dict_bytes import dict_bytes

async def sendmsg(host, port):  #
    reader, writer = await asyncio.open_connection (
        host, port)

    test_dict = {
            "mobile_dcp_2":{
                "port":[10102],
                "frac":0.08,
                "batch":2,
                "timeout":10,
                "threads":16,
                "device":"gpu"
            },
        "mobile_dcp_1":{
            "port":[10103],
            "frac":0.08,
            "batch":2,
            "timeout":10,
            "threads":16,
            "device":"gpu"
        },
    }
    test_dict['type'] = 'allocation'
    await dict_bytes().send_dict2bytes (test_dict, writer)
    print(f'send msg:{test_dict}')
    print(await dict_bytes().read_bytes2dict(reader,writer))
    writer.close()


if __name__ == "__main__":
    asyncio.run(sendmsg('127.0.0.1',9000))
