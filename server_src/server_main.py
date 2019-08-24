from server.a2_ml_server import a2_ml_server
import sys
import traceback

device = sys.argv[1]
try:
    a2_ml_server(device=device)
except Exception as e:
    traces = traceback.format_exc()

    with open("/tmp/server.log","a") as f:
        f.writelines([str(traces),str(e)])
        f.close()
