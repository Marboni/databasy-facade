from Queue import Queue
import threading
import time
import zmq
from databasyfacade.mq import api

__author__ = 'Marboni'

_rpc_server = None
_pub_server = None

rpc_server = lambda: _rpc_server
pub_server = lambda: _pub_server

def init(rpc_port, pub_port):
    global _rpc_server
    _rpc_server = RpcServer(rpc_port)
    _rpc_server.run()

    global _pub_server
    _pub_server = Publisher(pub_port)
    _pub_server.run()


class RpcServer(object):
    def __init__(self, port):
        super(RpcServer, self).__init__()
        self.address = 'tcp://*:%s' % port
        self.context = zmq.Context()

    def _listen(self):
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.address)

        while True:
            request = self.socket.recv_pyobj()
            try:
                func = getattr(api, request['func'])
            except AttributeError:
                response = {
                    'status': 'ERROR',
                    'error': ValueError('Function "%s" not exists.' % request['func'])
                }
            else:
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

            self.socket.send_pyobj(response)

    def run(self):
        t = threading.Thread(target=self._listen, name='rpc_server')
        t.daemon = True
        t.start()

    def unbind(self):
        self.socket.unbind(self.address)


class Publisher(object):
    def __init__(self, port):
        super(Publisher, self).__init__()
        self.address = 'tcp://*:%s' % port
        self.context = zmq.Context()
        self.messages = Queue()

    def publish(self, command, *args):
        message = {
            'command': command,
            'args': args
        }
        self.messages.put_nowait(message)

    def _deliver(self):
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(self.address)
        time.sleep(0.5)
        while True:
            while not self.messages.empty():
                self.socket.send_pyobj(self.messages.get_nowait())
            time.sleep(0.05)

    def run(self):
        t = threading.Thread(target=self._deliver, name='pub_server')
        t.daemon = True
        t.start()

    def unbind(self):
        self.socket.unbind(self.address)