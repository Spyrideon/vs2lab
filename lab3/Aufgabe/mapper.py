import pickle
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])
splitter = constPipe.SPLIT_ENDPOINT 

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket

pull_socket.connect(splitter)  # connect to splitter
push_socket = context.socket(zmq.PUSH)  # create a push socket

address = constPipe.MAPPER_ENDPOINTS[int(me)]  # how and where to connect
push_socket.bind(address)  # bind socket to address


time.sleep(1) 

print("{} started".format(me))

while True:
    work = pickle.loads(pull_socket.recv())  # receive work from a source
    print("{} received workload {}".format(me, work))
    for workload in work.split(" "):
        push_socket.send(pickle.dumps((me, workload.strip())))  # send workload to worker
    time.sleep(1)  # pretend to work
