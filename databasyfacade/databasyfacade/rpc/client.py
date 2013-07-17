import pickle
import zmq

__author__ = 'Marboni'


class RpcClient(object):
    def __init__(self, address):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(address)

    def __call__(self, func, *args):
        request = {
            'func': func,
            'args': args
        }
        request = pickle.dumps(request)

        self.socket.send(request)
        response = self.socket.recv()

        response = pickle.loads(response)
        if response['status'] == 'ERROR':
            e = response['error']
            raise e
        else:
            return response['result']
