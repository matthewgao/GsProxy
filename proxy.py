#! /usr/bin/env python3
import socket
import re
import _thread
import time
from logger import logger
from proxy_socket import ProxySocket
from select import poll,POLLIN
# 1. pan.baidu.com will perodically timeout.
# 2. poll timeout
# 3. use memoryview to buffer recv_info
# 4. thread pool 

# 4. FIN_WAIT and CLOSE_WAIT

g_count = 0    

def find_host(data):
    logger.debug("searching host from %s", data)
    try:
        #FIXME need to prevent this xxxx:443
        regx_host = re.compile(b'(?<=\r\nHost:).*\r\n')
        target_host = regx_host.search(data).group(0).decode()
    except Exception:
        return None
    logger.debug("Found a host %s", target_host)
    
    return target_host.strip()
    
def find_connection(data):
    regx_connection = re.compile(b'(?<=\r\nConnection:).*\r\n')
    re_result = regx_connection.search(data)
    ret = None
    
    if re_result:
        try:
            ret = re_result.group(0).decode().strip()
            # print("CLOSE", ret)
        except Exception as e:
            print("FAIL to find connection from HEADER {0}, msg {1}".format(ret, repr(e)))
    return ret
    
def process(conn):
    with conn as conn:
        fd_map = dict()
        fd_map[conn.fd] = conn
        a_poll = poll()
        a_poll.register(conn.fd, POLLIN)
        forward_server = None
        
        forward_server_created = False
        while True:
            logger.debug("LOOP IN PROCESS")
            ready = a_poll.poll()
            ok = True
            for ready_fd, event in ready:
                logger.debug("LOOP IN READY")
                
                if not (event & POLLIN): continue
                
                recv = fd_map[ready_fd].recv()
                
                if recv == None:
                    continue
                
                global g_count
                g_count += len(recv)
                # logger.info("PROCESS %sMB data", (g_count/1024/1024))
                # IF return None means not ready, then continue
                # IF return b'', means connection close by peer. set ok = False
                
                if recv == b'':
                    logger.debug("Recv null message, break")
                    ok = False
                    continue
                
                if not forward_server_created:
                    target_host = find_host(recv)
                    forward_server = ProxySocket.get_client(host=target_host, port=80)
                    forward_server.connect()
                    if forward_server and forward_server.fd != -1: 
                        forward_server_created = True
                        fd_map[forward_server.fd] = forward_server
                        a_poll.register(forward_server.fd, POLLIN)
                        logger.info("Create a connection to %s", target_host)
                    else:
                        logger.error("FAIL to connect to target host {0}".format(target_host))
                        ok = False
                        break
                
                for itr in fd_map.keys():
                    logger.debug("LOOP IN FIND KEY")
                    if itr != ready_fd:
                        ok = fd_map[itr].sendall(recv)
                
                if not ok: break
            if not ok: break
        
        if forward_server: forward_server.shutdown()        
    
if __name__ == "__main__":
    with ProxySocket.get_server("0.0.0.0", 50007) as server:
        server.listen()
        while True:
            conn = server.start_accept()
            if not conn: break
            _thread.start_new_thread( process, (conn, ) )