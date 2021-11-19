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

if PLATFORM=='win':
    import regobj
    from regobj import * 

validHIVES=['HKCC', 'HKCR', 'HKCU', 'HKDD', 'HKEY_CLASSES_ROOT', 'HKEY_CURRENT_CONFIG', 'HKEY_CURRENT_USER', 'HKEY_DYN_DATA', 'HKEY_LOCAL_MACHINE', 'HKEY_PERFORMANCE_DATA', 'HKEY_USERS', 'HKLM', 'HKPD', 'HKU']

def parseRegString(searchString):
    if '\\' in searchString and searchString.split('\\')[0] in validHIVES:
        try: 
            rootKey=searchString.split('\\')[0]
            subKey=searchString.split(rootKey)[1]
            rootKey=eval(rootKey)
            if type(rootKey)!= regobj.Key:
                debug("rootKey eval didn't result in a regobj.Key. Terminating check.")
                return None,None
            else:
                return rootKey,subKey
        except Exception as e:
            debug("RegistryItem/parseRegString exception %r"%(e))
            return None,None            

        
    
def path(searchString,cacheItems=[],cache=False):
    """
    a full file path to test for exists 
    """
    hits=False   
    if PLATFORM!='win':
        #no registry 
        hits=False
    
    else:
        if '\\' in searchString and searchString.split('\\')[0] in validHIVES:
            try:            
                rootKey=searchString.split('\\')[0]
                subKey=searchString.split(rootKey)[1]
                rootKey=eval(rootKey)            
                if type(rootKey)!= regobj.Key:
                    debug("rootKey eval didn't result in a regobj.Key. Terminating check.")
                    return hits
                
                if type(rootKey(subKey)) is regobj.Key:
                    hits=True
                    if cache:
                        cacheItems.append(searchString)
            except Exception as e:
                debug("RegistryItem/Path exception %r"%(e))
                pass
                       
        else: 
            debug("invalid registry key. Terminating check")
    return hits

   
def valuename(searchString,cacheItems=[],cache=False):
    hits=False
    debug("valuename values %s %s"%(searchString,str(cacheItems)))
    for akey in cacheItems:
        try:
            rootKey,subKey=parseRegString(akey)
            subKeyValueNames=[k.name for k in rootKey(subKey)]
            debug('SubKeys are %s'%(str(subKeyValueNames)))
            if searchString in subKeyValueNames:
                hits=True
        except Exception as e:
            debug("RegistryItem/valuename exception %r"%(e))
            continue
                
    return hits

def value(searchString,cacheItems=[],cache=False):
    """unclear what the difference is between registryitem/value and registryitem/text..so they are the same here"""    
    hits=False
    debug("value values %s %s"%(searchString,str(cacheItems)))
    for akey in cacheItems:
        try:
            rootKey,subKey=parseRegString(akey)
            subKeyValues=[str(k.data) for k in rootKey(subKey).values()]
            debug('SubKeyValues are %s'%(str(subKeyValues)))
            if searchString in subKeyValues:
                hits=True
        except Exception as e:
            debug("RegistryItem/value exception %r"%(e))
            continue

    return hits

def text(searchString,cacheItems=[],cache=False):
    """unclear what the difference is between registryitem/value and registryitem/text..so they are the same here"""
    hits=False
    debug("text values %s %s"%(searchString,str(cacheItems)))
    for akey in cacheItems:
        try: 
            rootKey,subKey=parseRegString(akey)
            subKeyValues=[str(k.data) for k in rootKey(subKey).values()]
            debug('SubKeyValues are %s'%(str(subKeyValues)))
            if searchString in subKeyValues:
                hits=True
        except Exception as e:
            debug("RegistryItem/text exception %r"%(e))
            continue
                
    return hits