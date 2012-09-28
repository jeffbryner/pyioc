#!/usr/bin/python2
import logging
from logging.handlers import WatchedFileHandler
from logging.handlers import SysLogHandler
from logging.handlers import NTEventLogHandler
from datetime import datetime
import sys

loglevels = {   'debug'   : logging.DEBUG,
                'info'    : logging.INFO,
                'warning' : logging.WARNING,
                'error'   : logging.ERROR,
                'critical': logging.CRITICAL }
logformat      = "%s %8s %s"
logfile=''
loglevel=''
logger=None

def setLogging():
    #Setup logging.
    global logger
    if logger==None: 
        logger = logging.getLogger('pyiocClient')
    if logger.level!=loglevel:
        logger.setLevel(loglevel)
    for lh in logger.handlers:
        logger.removeHandler(lh)
    
    loghandler = WatchedFileHandler( logfile )
    logger.addHandler(loghandler)



def debug( msg ):
    if logger: 
        logger.debug( logformat % (datetime.now(),'DEBUG',msg))

def info( msg ):
    if logger:
        logger.info( logformat % (datetime.now(),'INFO',msg))

def warning( msg ):
    if logger:
        logger.warning( logformat % (datetime.now(),'WARNING',msg))

def error( msg ):
    if logger:
        logger.info( logformat % (datetime.now(),'ERROR',msg))
    else:
        sys.stderr.write(logformat % (datetime.now(),'ERROR',msg))

def critical( msg ):
    if logger:
        logger.critical( logformat % (datetime.now(),'CRITICAL',msg))
    else:
        sys.stderr.write(logformat % (datetime.now(),'ERROR',msg))