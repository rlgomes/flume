"""
flume logger
"""

import logging

from logging import DEBUG, INFO, ERROR, WARN, CRITICAL


def init():
    """
    internal method that initialize the flume logger
    """
    logger = logging.getLogger('flume')
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.WARN)


def setLogLevel(lvl):
    """
    set logging level (ie logger.INFO, DEBUG, etc.)
    """
    logging.getLogger('flume').setLevel(lvl)


def debug(*args, **kwargs):
    """
    log a debug message
    """
    logging.getLogger('flume').debug(*args, **kwargs)


def info(*args, **kwargs):
    """
    log an info message
    """
    logging.getLogger('flume').info(*args, **kwargs)


def warn(*args, **kwargs):
    """
    log a warning message
    """
    logging.getLogger('flume').warn(*args, **kwargs)


def error(*args, **kwargs):
    """
    log an error message
    """
    logging.getLogger('flume').error(*args, **kwargs)


def critical(*args, **kwargs):
    """
    log a critical message
    """
    logging.getLogger('flume').critical(*args, **kwargs)


init()
