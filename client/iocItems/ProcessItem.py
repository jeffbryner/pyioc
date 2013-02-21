#!/usr/bin/python2
import psutil
import os
import sys
import socket
from lib import log
from lib.log import debug,critical,error,info

def name(searchString):
    searchString=str(searchString).lower()
    for process in psutil.process_iter():
        try:
            if searchString in str(process.name).lower():
                return True
        except psutil.error.NoSuchProcess as e:
            continue
        except psutil.error.AccessDenied as e:
            error("Must run this as root/administrator to get process connection information\n")
    return False

def path(searchString):
    searchString=str(searchString).lower()
    for process in psutil.process_iter():
        try:
            if searchString in str(process.cmdline).lower():
                return True
        except psutil.error.NoSuchProcess as e:
            continue
        except psutil.error.AccessDenied as e:
            error("Must run this as root/administrator to get process connection information\n")
    return False

def pid(searchString):
    searchString=str(searchString).lower()
    for process in psutil.process_iter():
        try:
            if searchString in str(process.pid).lower():
                return True
        except psutil.error.NoSuchProcess as e:
            continue
        except psutil.error.AccessDenied as e:
            error("Must run this as root/administrator to get process connection information\n")
    return False

def username(searchString):
    searchString=str(searchString).lower()
    for process in psutil.process_iter():
        try:
            if searchString in str(process.username).lower():
                return True
        except psutil.error.NoSuchProcess as e:
            continue
        except psutil.error.AccessDenied as e:
            error("Must run this as root/administrator to get process connection information\n")
    return False

def portlistportitemlocalport(searchString):
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

def portlistportitemremoteip(searchString):
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
    
def portlistportitemremoteport(searchString):
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