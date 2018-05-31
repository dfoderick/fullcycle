'''calls miner api'''
#based on https://github.com/tsileo/pycgminer
import socket
import json

class MinerApi(object):
    """cgminer api client"""
    def __init__(self, host='localhost', port=4028, timeout=2, retry_count=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retry_count = retry_count
        self.encoding = 'utf-8'

    def command(self, command, arg=None):
        socket.setdefaulttimeout(self.timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        retries_remaining = self.retry_count
        while (retries_remaining > 0):
            try:
                sock.connect((self.host, self.port))
                payload = {"command": command}
                if arg is not None:
                    payload['parameter'] = arg
                sock.send(bytes(json.dumps(payload), self.encoding))
                #for some reason on linux, cannot shutdown write yet
                #s.shutdown(socket.SHUT_WR)
                received = self._receive(sock)
                sock.shutdown(socket.SHUT_RDWR)
            except Exception as ex:
                retries_remaining -= 1
                if retries_remaining <= 0:
                    return dict({'STATUS': [{'STATUS': 'error', 'description': ex}]})
            else:
                # remove null byte in first character and add missing comma in stats command
                # fix lcd command
                return json.loads(received[:-1].replace('}{', '},{').replace('[,', '['))
            finally:
                sock.close()

    def _receive(self, sock, max_bytes=4096):
        fullresponse = ''
        while True:
            more = sock.recv(max_bytes)
            if not more: break
            fullresponse += more.decode(self.encoding)
        return fullresponse

    def __getattr__(self, attr):
        '''a pattern that converts an attribute into a miner command.
        Examples: stats, pools
        '''
        def out(arg=None):
            return self.command(attr, arg)
        return out
