#!/usr/bin/env python3
import json
import requests

from lastwill.settings import PARINT_HOST, PARINT_PORT

class ParConnectExc(Exception):
    def __init__(self, *args):
        self.value = 'can not connect to parity'

    def __str__(self):
        return self.value

class ParErrorExc(Exception):
    pass

    
class ParInt:
    def __init__(self, addr=PARINT_HOST, port=PARINT_PORT):
        self.addr = addr
        self.port = port

    def __getattr__(self, method):
        def f(*args):
            arguments = { 
                    'method': method,
                    'params': args,
                    'id': 1,
                    'jsonrpc': '2.0',
            }
            try:
                temp = requests.post(
                        'http://{}:{}/'.format(self.addr, self.port),
                        json=arguments,
                        headers = {'Content-Type': 'application/json'}
                )
            except requests.exceptions.ConnectionError as e:
                raise ParConnectExc()
            result = json.loads(temp.content.decode())
            if result.get('error'):
                raise ParErrorExc(result['error']['message'])
            return result['result']
        return f
    
if __name__ == '__main__':
    par_int = ParInt(PARINT_HOST, PARINT_PORT)
    try:
        print(par_int.parity_nextNonce('0x' + '0'*40))
    except (ParConnectExc, ParErrorExc) as e :
        print(e)
