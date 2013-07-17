import pickle
import threading
import zmq
from databasyfacade.rpc import api

__author__ = 'Marboni'

server = None
srv = lambda: server

def init(zmq_address):
    global server
    server = RpcServer(zmq_address)
    server.run()

class RpcServer(object):
    def __init__(self, address):
        super(RpcServer, self).__init__()
        self.address = address

    def listen(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.address)

        while True:
            body = self.socket.recv()
            request = pickle.loads(body)
            func = getattr(api, request['func'])

            try:
                result = func(*request['args'])
            except Exception, e:
                response = {
                    'status': 'ERROR',
                    'error': e
                }
            else:
                response = {
                    'status': 'OK',
                    'result': result
                }

            response = pickle.dumps(response)
            self.socket.send(response)

    def run(self):
        t = threading.Thread(target=self.listen)
        t.setDaemon(True)
        t.start()

    def unbind(self):
        self.socket.unbind(self.address)