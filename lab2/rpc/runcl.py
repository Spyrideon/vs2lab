import time
import logging
import threading

import rpc
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

result_ready = threading.Event()


def on_result_ready(result_list):
    print("Result received: {}".format(result_list.value))
    result_ready.set()

cl = rpc.Client()
cl.run()

try:
    base_list = rpc.DBList({'foo'})
    cl.append('bar', base_list, callback=on_result_ready)
    print("ACK erhalten! Waiting for result...")

    sekunden = 0
    while not result_ready.is_set():
        sekunden += 1
        print("Client is active! Waiting for result... ({} seconds)".format(sekunden))
        time.sleep(1)
finally:
    cl.stop()
