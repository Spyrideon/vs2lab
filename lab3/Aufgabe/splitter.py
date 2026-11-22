import pickle
import sys
import time
import re

import zmq

import constPipe

context = zmq.Context()
push_socket = context.socket(zmq.PUSH)  # create a push socket

address = constPipe.SPLIT_ENDPOINT  # how and where to connect
push_socket.bind(address)  # bind socket to address

time.sleep(1) # wait to allow all clients to connect

file = open("example.txt", "r")

while True:
    line = file.readline()
    if not line:
        break
    for workload in re.split(r'(?<=[.!?])\s+', line):
        push_socket.send(pickle.dumps(workload.strip()))  # send workload to worker
