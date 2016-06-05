#!/usr/bin/env python3
# coding=utf-8
# Created Time: 2016-06-05
# Using fd watcher to watch if there is anything to read.

__author__ = 'Matthew Gao'

import _thread
from logger import logger
from proxy_socket import ProxySocket
from util import find_host
import asyncio


FD_MAP = dict()

def async_reader(conn, loop):
    data = conn.recv()
    logger.debug("RECV DATA: %s", data)
    if data is None:
        return

    if data == b'':
        if conn in FD_MAP:
            forward_server = FD_MAP[conn]
            loop.remove_reader(forward_server.fd)
            forward_server.shutdown()
            del FD_MAP[forward_server]
            del FD_MAP[conn]
        
        loop.remove_reader(conn.fd)
        conn.shutdown()
        return

    if conn not in FD_MAP:
        target_host = find_host(data)
        if target_host is None:
            return

        forward_server = ProxySocket.get_client(host=target_host, port=80)
        forward_server.connect()
        if forward_server and forward_server.fd != -1: 
            FD_MAP[conn] = forward_server
            FD_MAP[forward_server] = conn
            loop.add_reader(forward_server.fd, async_reader, forward_server, loop)
            logger.info("Create a connection to %s", target_host)
        else:
            logger.error("FAIL to connect to target host {0}".format(target_host))
    
    FD_MAP[conn].sendall(data)


def start_async_main(loop):
    with ProxySocket.get_server("0.0.0.0", 50007) as server:
        server.listen()
        while True:
            conn = server.start_accept()
            if not conn: break
            loop.add_reader(conn.fd, async_reader, conn, loop)

def async_processor():
    loop = asyncio.get_event_loop()
    _thread.start_new_thread( start_async_main, (loop, ) )
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    async_processor()