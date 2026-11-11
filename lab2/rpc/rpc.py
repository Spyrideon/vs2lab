import threading
import time

import constRPC
from context import lab_channel


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

    def _receive_result(self):
        _, message = self.chan.receive_from(self.server)
        if not isinstance(message, tuple) or len(message) != 2 or message[0] != constRPC.RESULT:
            raise RuntimeError('Expected RPC result, received: {}'.format(message))
        return message[1]

    def _wait_for_result(self, callback):
        callback(self._receive_result())

    def append(self, data, db_list, callback=None):
        assert isinstance(db_list, DBList)
        message = (constRPC.APPEND, data, db_list)
        self.chan.send_to(self.server, message)

        _, acknowledgement = self.chan.receive_from(self.server)
        if acknowledgement != (constRPC.OK,):
            raise RuntimeError('Expected ACK from server, received: {}'.format(acknowledgement))

        if callback is None:
            return self._receive_result()

        self.waiter = threading.Thread(target=self._wait_for_result, args=(callback,))
        self.waiter.start()


class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)
        return db_list.append(data)

    def _process(self, client, db_list, data):
        time.sleep(10)
        result = self.append(data, db_list)
        self.chan.send_to({client}, (constRPC.RESULT, result))

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)
            if msgreq is None:
                continue

            client, request = msgreq
            if request[0] == constRPC.APPEND:
                self.chan.send_to({client}, (constRPC.OK,))
                self._process(client, request[2], request[1])
