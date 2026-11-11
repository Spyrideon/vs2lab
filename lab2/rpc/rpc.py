from curses.ascii import ACK

import constRPC
import time
import threading

from context import lab_channel

ACK = 'ACK'
RESULT = getattr(constRPC, 'RESULT', 'RESULT')

class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None
        self.waiter = None
         

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')
        
     

    def stop(self):
        
        self.chan.leave('client')

    def _wait_for_result(self, callback):
        #print("[DEBUG] Wartethread laeuft")
        msgrcv = self.chan.receive_from(self.server)
        #
        # print("[DEBUG] Wartethread hat empfangen:", msgrcv)
        msg = msgrcv[1]
        if msg[0] == RESULT:
            callback(msg[1])



    def append(self, data, db_list, callback):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server
        msgrecv = self.chan.receive_from(self.server)  # wait for response
        if msgrecv[1][0] != ACK:
            raise RuntimeError("Kein ACK vom Server: {}".format(msgrcv[1]))
        
        self.waiter = threading.Thread(target=self._wait_for_result, args=(callback,)) 
        self.waiter.start()  # start the thread to wait for the result




class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3  # seconds

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def _process(self, client, db_list, data):
        #print("[DEBUG] Server: starte Pause")
        time.sleep(10)  # simulate some processing time
        result = self.append(data, db_list)
        #print("[DEBUG] Server: sende Ergebnis")
        self.chan.send_to({client}, (RESULT, result))  # send result back to client

    

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    self.chan.send_to({client}, (ACK,))  # send ACK to client
                    self._process(client, msgrpc[2], msgrpc[1])  # process the request      
                else:
                    pass  # unsupported request, simply ignore   