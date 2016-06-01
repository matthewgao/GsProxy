#! /usr/bin/env python3
import socket
# import re
# import _thread
import time
from logger import logger

class ProxySocket:
    '''use to create a server/client socket, support using "with""'''
    
    def __init__(self, host=None, port=None, block=False, is_server=False, existed_socket=None):
        '''existed_socket allow you to wrap a socket using this class'''
        self._host = host
        self._port = port
        self._is_block = block
        self._is_server = is_server
        
        if existed_socket: 
            logger.debug("Inherit from a existed socket: {0}".format(host))
            self._socket = existed_socket
            self._socket.setblocking(block)
            return
        
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            logger.error("FAIL to create a socket for {0}, msg {1}"
                                .format(self._host, repr(e)))
            self.shutdown()

    def connect(self):
        '''return a ProxySocket object'''
        if self._is_server : return None
        
        try:
            self._socket.connect((self._host, self._port))
            self._socket.setblocking(self._is_block)
            return self
        except Exception as e:
            logger.error("FAIL to connect to {0}, msg {1}".format(self._host,repr(e)))
            self.shutdown()
            return None
    
    def listen(self, backlog=100):
        if not self._is_server: return None
        
        try:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._host, self._port))
            self._socket.listen(backlog)
            logger.debug("start to listen at {0}:{1}".format(self._host, self._port))
        except Exception as e:
            logger.error("Fail to listen, msg: {0}".format(repr(e)))
            self.shutdown()
            return False
        return True
        
    def start_accept(self):
        if not self._is_server: return None
        
        try:
            conn, addr = self._socket.accept()
            logger.info("Connected by {0}".format(addr))
            # conn.setblocking(self._is_block)
            return ProxySocket.__wrapper_existed_socket(host = addr, conn_socket=conn)
        except Exception as e:
            logger.error("Fail to accept, msg: {0}".format(repr(e)))
            # self.shutdown()
            return None
        
    def shutdown(self):
        if self._socket:
            # self._socket.shutdown(2)
            logger.info("Close %s", self._host)
            self._socket.close()
            
    def sendall(self, data):
        '''return true means normal action, False mean connection broken'''
        try:
            self._socket.sendall(data)
            return True
        except BlockingIOError as e:
            logger.debug("not ready to read from {0}, msg: {1}".format(self._host,repr(e)))
            return True
        except TimeoutError as e:
            logger.error("{1} while sending to {0}, msg: ".format(self._host,repr(e)))
            return True
        except ConnectionResetError as e: 
            logger.error("Connection reseted while sending to {0}, msg: {1}".format(self._host,repr(e)))
            return False
        except BrokenPipeError as e:
            logger.error("BrokenPipeError while sending to {0}, msg: {1}".format(self._host,repr(e)))
            return False
        except OSError as e:
            logger.error("OSError while sending to {0}, msg: {1}".format(self._host,repr(e)))
            return False
    
    def recv(self):
        resp = None
        try:
            # resp = b''
            # while True:
            #     logger.debug("LOOP IN RECV")
            #     tmp = self._socket.recv(1024*2)
            #     if not tmp: break
            #     resp += tmp
            # if return a b'', that mean connection closed by peer
            resp = self._socket.recv(4096)
        except BlockingIOError as e:
            logger.debug("not ready to read from {0}, msg: {1}".format(self._host,repr(e)))
            return None
        except ConnectionResetError as e: 
            logger.debug("Connection reseted while read from {0}, msg: {1}".format(self._host,repr(e)))
        except BrokenPipeError as e:
            logger.error("BrokenPipeError while read from {0}, msg: {1}".format(self._host,repr(e)))
        except TimeoutError as e:
            logger.error("{1} while read from {0}, msg: ".format(self._host,repr(e)))
        except OSError as e:
            logger.error("OSError while read from {0}, msg: {1}".format(self._host,repr(e)))
        finally:
            return resp
    @property
    def fd(self):
        return self._socket.fileno()
    
    def __enter__(self):
        logger.debug("enter host: {0}".format(self._host))
        return self
    
    def __exit__(self, type, value, traceback):
        logger.debug("close host: {0}".format(self._host))
        self.shutdown()
        
    @classmethod
    def get_server(cls, host, port, block=False):
        server = cls(host=host, port=port, block=block, is_server=True)
        return server
        
    @classmethod
    def get_client(cls, host, port, block=False):
        client = cls(host=host, port=port, block=block, is_server=False)
        return client
        
    @classmethod
    def __wrapper_existed_socket(cls, host, conn_socket):
        return cls(host=host, existed_socket=conn_socket)
        
        
if __name__ == "__main__":
    with ProxySocket.get_server("0.0.0.0", 50007) as server:
        server.listen()
        with server.start_accept() as conn:
            print("FD",conn.fd)
            # with ProxySocket.get_client("127.0.0.1", 50007) as client:
            #     client.connect()