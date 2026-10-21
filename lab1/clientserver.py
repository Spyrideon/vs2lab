"""
Client and server using classes
"""

import logging
import socket
import json

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

def send(sock, message):
    sock.sendall((json.dumps(message) + "\n").encode('utf-8'))
 
 
def receive(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1024)
        if not chunk:
            return None
        data += chunk
    return json.loads(data.decode('utf-8'))


class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    def __init__(self, phone_book = None):
        self.phone_book = phone_book if phone_book is not None else const_cs.PHONE_BOOK

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        self._logger.info("Server is listening")
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                self._logger.info("Server accepted connection from " + str(address))
                while True:  # forever
                    request = receive(connection)
                    if request is None:
                        break  # stop if client stopped
                    self._logger.info("Server received request " + str(request))
                    send(connection, self.handle(request))
                    self._logger.info("Server sent response")
                connection.close()  # close the connection
                self._logger.info("Server closed connection")
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")

    def handle(self, request):
        if request["command"] == "GET":
            return self.phone_book.get(request["name"])
        if request["command"] == "GETALL":
            return self.phone_book
        return None


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def get(self, name):
        send(self.sock, {"command": "GET", "name": name})
        self.logger.info("Client sent GET " + name)
        number = receive(self.sock)
        self.logger.info("Client received " + str(number))
        return number
 
    def get_all(self):
        send(self.sock, {"command": "GETALL"})
        self.logger.info("Client sent GETALL")
        entries = receive(self.sock)
        self.logger.info("Client received " + str(len(entries)) + " entries")
        return entries

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def close(self):
        """ Close socket """
        self.sock.close()
        self.logger.info("Client down.")