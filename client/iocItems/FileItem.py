#!/usr/bin/python2
import os
import sys
import platform
import glob
from lib.settings import PLATFORM
from lib.settings import DIRECTORYRECURSELIMIT
from lib import log
from lib.log import debug,critical,error,info
from time import sleep
from hashlib import md5, sha1


def fullpath(searchString,cacheItems=[],cache=False):
    """
    either a full file path for condition="is" or 
    last bits of a file/directory path for condition="contains": 
    \system32\perfdi.ini"""
    #glob is unix-style file searching..add a * if needed.
    #searching uses glob
    #instead of os.walk since glob performs better when you don't know 
    #where you may find the file; i.e. 
    #glob /*file
    #glob /*/*file
    #glob /*/*/*file    
    hits=False
    if searchString[0]!='*':
        searchString='*' + searchString
    if PLATFORM=='linux':
        driveroot='/'
        for level in range(0,DIRECTORYRECURSELIMIT):
            dirlevel=level*('*'+os.path.sep)
            for name in glob.glob(driveroot +dirlevel + searchString):
                if cache:
                    cacheItems.append(name)
                    debug(cacheItems)
                    hits=True
                else:
                    #no need to look further, found one hit..early escape
                    return True
            #reduce our impact on the system
            sleep(1)
    
    if PLATFORM=='win':
        for driveletter in ['c','d','e']:            
            driveroot=driveletter + ':\\'
            if os.path.isdir(driveroot):
                for level in range(0,DIRECTORYRECURSELIMIT):
                    dirlevel=level*('*'+os.path.sep)
                    for name in glob.glob(driveroot +dirlevel + searchString):
                        if cache:
                            cacheItems.append(name)
                            hits=True
                        else:
                            #no need to look further, found one hit..early escape
                            return True                        
                    sleep(1)
    return hits

def filename(searchString):
    """exact match search for a file name"""
    if PLATFORM=='linux':
        driveroot='/'
        for level in range(0,DIRECTORYRECURSELIMIT):
            dirlevel=level*('*'+os.path.sep)
            for name in glob.glob(driveroot +dirlevel + searchString):
                if os.path.isfile(name):
                    return True
        return False
    
    if PLATFORM=='win':
        for driveletter in ['c','d','e']:            
            driveroot=driveletter + ':\\'
            if os.path.isdir(driveroot):
                for level in range(0,DIRECTORYRECURSELIMIT):
                    dirlevel=level*('*'+os.path.sep)
                    for name in glob.glob(driveroot +dirlevel + searchString):
                        if os.path.isfile(name):
                            return True
                    sleep(1)
        return False
    

def fileextension(searchString):
    """search filename for ending extension"""
    if searchString[0]!='*':
        searchString='*' + searchString
    if PLATFORM=='linux':
        driveroot='/'
        for level in range(0,DIRECTORYRECURSELIMIT):
            dirlevel=level*('*'+os.path.sep)
            for name in glob.glob(driveroot +dirlevel + searchString):
                if os.path.isfile(name):
                    return True
        return False
    
    if PLATFORM=='win':
        for driveletter in ['c','d','e']:            
            driveroot=driveletter + ':\\'
            if os.path.isdir(driveroot):
                for level in range(0,DIRECTORYRECURSELIMIT):
                    dirlevel=level*('*'+os.path.sep)
                    for name in glob.glob(driveroot +dirlevel + searchString):
                        if os.path.isfile(name):
                            return True
                    sleep(1)
        return False

def md5sum(searchString,cacheItems=[],cache=False):
    for afile in cacheItems:
        hash = md5()    
        f = open(afile, 'rb')
        try:
            hash.update(f.read())
        finally:
            f.close()
        if hash.hexdigest()==searchString:
            return True
    return False