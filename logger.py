#! /usr/bin/env python3
import logging

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename="log.log",format=FORMAT,level=logging.INFO)
logger = logging.getLogger('httpproxy')

if __name__ == "__main__":
    logger.error("An error")
    logger.info("An info")
    logger.warning("a warning")
    logger.debug("debugger")