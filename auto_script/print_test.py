import time
import sys
i = 0


def unbuffered_print(p_str):
    print(p_str, flush=True)


while True:
    unbuffered_print("Now %s"%i)
    # sys.stdout.flush()
    time.sleep(2)
    i += 1
