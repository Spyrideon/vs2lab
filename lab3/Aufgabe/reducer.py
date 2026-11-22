import pickle
import sys
import time
import string

import zmq

import constPipe

me = str(sys.argv[1])
address1 = constPipe.MAPPER_ENDPOINTS[0]  # 1st mapper
address2 = constPipe.MAPPER_ENDPOINTS[1]  # 2nd mapper
address3 = constPipe.MAPPER_ENDPOINTS[2]  # 3rd mapper

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket

pull_socket.connect(address1)  # connect to task source 1
pull_socket.connect(address2)  # connect to task source 2
pull_socket.connect(address3)  # connect to task source 3

time.sleep(1) 

print("{} started".format(me))

wordmap = {}

while True:
    work = pickle.loads(pull_socket.recv()) # receive work from a source
    form = work[1].translate(str.maketrans('', '', string.punctuation)).lower()
    grammar =""
    for word in wordmap:
        if word == form:
            wordmap[word] += 1
            grammar = "st" if wordmap[word] == 1 else "nd" if wordmap[word] == 2 else "rd" if wordmap[word] == 3 else "th"
            break
    else:
        wordmap.update({form: 1})
    print("{} : {}".format(form,wordmap[form]))
    #print(wordmap)
    time.sleep(1)  # pretend to work

