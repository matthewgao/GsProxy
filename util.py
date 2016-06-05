#!/usr/bin/env python3
# coding=utf-8
# Created Time: 2016-06-05

__author__ = 'Matthew Gao'

from logger import logger
import re

def find_host(data):
    logger.debug("searching host from %s", data)
    try:
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