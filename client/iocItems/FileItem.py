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
from hashlib import md5, sha1, sha256
from lib import util
import pefile
import time
import datetime
from dateutil import parser
try:
    import magic
except ImportError:
    pass
    
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
                if cache and not name in cacheItems:
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
                        if cache and not name in cacheItems:
                            cacheItems.append(name)
                            hits=True
                        else:
                            #no need to look further, found one hit..early escape
                            return True                        
                    sleep(1)
    return hits

def filepath(searchString,cacheItems=[],cache=False):
    """ Seems to be the same as fullpath?
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
                if cache and not name in cacheItems:
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
                        if cache and not name in cacheItems:
                            cacheItems.append(name)
                            hits=True
                        else:
                            #no need to look further, found one hit..early escape
                            return True                        
                    sleep(1)
    return hits

def filename(searchString,cacheItems=[],cache=False):
    """exact match search for a file name"""
    if PLATFORM=='linux':
        driveroot='/'
        for level in range(0,DIRECTORYRECURSELIMIT):
            dirlevel=level*('*'+os.path.sep)
            for name in glob.glob(driveroot +dirlevel + searchString):
                if os.path.isfile(name):
                    if cache and not name in cacheItems:
                        cacheItems.append(name)
                        
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
                            if cache and not name in cacheItems:
                                cacheItems.append(name)                            
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


def sha1sum(searchString,cacheItems=[],cache=False):
    for afile in cacheItems:
        hash = sha1()    
        f = open(afile, 'rb')
        try:
            hash.update(f.read())
        finally:
            f.close()
        if hash.hexdigest()==searchString:
            return True
    return False

def sha256sum(searchString,cacheItems=[],cache=False):
    for afile in cacheItems:
        hash = sha256()    
        f = open(afile, 'rb')
        try:
            hash.update(f.read())
        finally:
            f.close()
        if hash.hexdigest()==searchString:
            return True
    return False

def sizeinbytes(searchString,cacheItems=[],cache=False):
    if not util.is_number(searchString):
        return False
    for afile in cacheItems:
        if long(os.path.getsize(afile))==long(searchString):
            return True
    return False

def peinfopetimestamp(searchString,cacheItems=[],cache=False):
    if not util.is_date(searchString):
        return False
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=True)            
            epochtime=pe.FILE_HEADER.TimeDateStamp
            petime=time.gmtime(epochtime)
            if parser.parse(searchString).isoformat()==parser.parse(time.asctime(petime)).isoformat():
                return True
        except:
            continue          
    return False

def peinfodetectedanomaliesstring(searchString,cacheItems=[],cache=False):
    """Undocumented IOC that seems to contain common suspicious PE indicators"""
    #Valid values seen in mandiant IOCs include: 
    #contains_eof_data, checksum_is_zero, checksum_mismatch,incorrect_image_size,oversized_section,corrupted_imports
    #Search PE file for suspicious PE indicators
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=True) 
            if searchString=="checksum_is_zero" and pe.OPTIONAL_HEADER.CheckSum==0:
                return True
            if searchString=="checksum_mismatch" and (pe.OPTIONAL_HEADER.CheckSum !=pe.generate_checksum()):
                return True
        except:
            continue
    return False
            
def peinfosectionssectionname(searchString,cacheItems=[],cache=False):
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=True) 
            for section in pe.sections:
                if searchString.lower() in section.Name.lower():
                    return True
        except:
            continue
    return False
    
def peinfoexportsdllname(searchString,cacheItems=[],cache=False):
    """Check for PE export item. Currently just a strings match."""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            if searchString in data:
                return True
        except:
            continue
    return False    

def peinfoexportsexportedfunctionsstring(searchString,cacheItems=[],cache=False):
    """Check for PE exported function. Currently just a strings match."""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            if searchString in data:
                return True
        except:
            continue
    return False    

def peinfotype(searchString,cacheItems=[],cache=False):
    if sys.modules.has_key('magic'):    
        for afile in cacheItems:
            try:
                FILE = open(afile, "rb")
                data = FILE.read()
                FILE.close()
                if searchString in magic.from_buffer(data):
                    return True
            except:
                continue
    return False    
    
    
def stringliststring(searchString,cacheItems=[],cache=False):
    """check for a string in a file"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            if searchString in data:
                return True
        except:
            continue
    return False

def peinfoversioninfolistversioninfoitemfiledescription(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'filedescription' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False

def peinfoversioninfolistversioninfoitemoriginalfilename(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'originalfilename' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False

def peinfoversioninfolistversioninfoitemproductname(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'productname' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False

def peinfoversioninfolistversioninfoiteminternalname(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'internalname' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False

def peinfoversioninfolistversioninfoitemcompanyname(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'companyname' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False

def peinfoversioninfolistversioninfoitemlegalcopyright(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'legalcopyright' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False

def peinfoversioninfolistversioninfoitemfileversion(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'fileversion' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False

def peinfoversioninfolistversioninfoitemlanguage(searchString,cacheItems=[],cache=False):
    """check for a string in a pefile version info table"""
    for afile in cacheItems:
        try:
            FILE = open(afile, "rb")
            data = FILE.read()
            FILE.close()
            pe = pefile.PE(data=data, fast_load=False) 
            for fileinfo in pe.FileInfo:
                if fileinfo.Key == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if 'language' in entry[0].encode('ascii',errors='ignore').lower() and searchString in entry[1].encode('ascii',errors='ignore').lower():
                                return True            
        except:
            continue
    return False