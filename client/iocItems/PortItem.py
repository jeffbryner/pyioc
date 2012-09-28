#!/usr/bin/python2
import psutil
import os
import sys
import socket
from lib import log
from lib.log import debug,critical,error,info

def localport(searchString):
    searchString=str(searchString).lower()
    for process in psutil.process_iter():
        try:
            for conn in process.get_connections():
                if int(searchString) in conn.local_address:
                    return True
        except psutil.error.NoSuchProcess as e:
            continue
        except psutil.error.AccessDenied as e:
            error("Must run this as root/administrator to get process connection information\n")
    return False

def remoteport(searchString):
    searchString=str(searchString).lower()
    for process in psutil.process_iter():
        try:
            for conn in process.get_connections():
                if int(searchString) in conn.remote_address:
                    return True
        except psutil.error.NoSuchProcess as e:
            continue
        except psutil.error.AccessDenied as e:
            error("Must run this as root/administrator to get process connection information\n")
    return False

def remoteip(searchString):
    searchString=str(searchString).lower()
    for process in psutil.process_iter():
        try:
            for conn in process.get_connections():
                if searchString in conn.remote_address:
                    return True
        except psutil.error.NoSuchProcess as e:
            continue
        except psutil.error.AccessDenied as e:
            error("Must run this as root/administrator to get process connection information\n")
    return False
    
    