#!/usr/bin/python2
from SOAPpy import ThreadingSOAPServer
import logging
from M2Crypto import SSL
from glob import glob
import os,sys
from netaddr import * 
from hashlib import sha1
from base64 import b64encode
import ConfigParser
from optparse import OptionParser

#create logger
logging.getLogger("ioclogger")
logging.basicConfig(filename='iocServer.txt', level=logging.DEBUG, format="%(asctime)s \t%(levelname)s \t%(message)s",datefmt='%m/%d/%Y %I:%M:%S %p')

#settings
iocDirectory="./iocs"
confDirectory="./confs"


def logEntry(value):
    '''simply log something to a text file'''
    print(value)
    logging.info(value)
    return 

def hashfile(filepath):
    '''get the sha1 hash of a file's contents'''
    sha1hash = sha1()
    f = open(filepath, 'rb')
    try:
        sha1hash.update(f.read())
    finally:
        f.close()
    return sha1hash.hexdigest()

def b64file(filepath):
    '''get the base64 version of a file's contents'''
    f = open(filepath, 'rb')
    try:
        sout=b64encode((f.read()))
    finally:
        f.close()
    return sout


def confList(ipaddress):
    '''returns a list of config files meant for the calling ip'''
    #looks lin conf Directory for subdirectories corresponding to netblock cidr masks
    #i.e. ./conf/172.21.1.0-24 will contain conf files meant for clients in the 172.21.1.0/24 cidr range.
    logEntry('checking conf files for ip: %s'%(ipaddress))
    netdirs=[]
    confsList=[]
    if os.path.exists(confDirectory):
        netdirs=os.listdir(confDirectory)        
    try: 
        for net in netdirs:
            if IPAddress(ipaddress) in IPNetwork(net.replace('-','/')):
                confFiles=os.listdir(confDirectory + os.sep + net)
                for confFile in confFiles:
                    conf={}
                    if '.conf' in confFile:
                        conf['filename']=confFile
                        conf['sha1hash']=hashfile(confDirectory + os.sep + net + os.sep + confFile)
                        confsList.append(conf)
    except ValueError as e: 
        #catches bad dir names that don't resolve to IP networks.
        logEntry(e)
        pass
    except AddrFormatError as e:
        #catches bad dir names that don't resolve to IP networks.
        logEntry(e)
        pass
    return confsList
    
    
def getConfFile(filename,ipaddress):
    '''returns a base64 encode of the conffile contents'''
    logEntry('request for file %s from ip: %s'%(filename,ipaddress))
    netdirs=os.listdir(confDirectory)
    try: 
        confb64=""
        for net in netdirs:
            if IPAddress(ipaddress) in IPNetwork(net.replace('-','/')):
                confFiles=os.listdir(confDirectory + os.sep + net)
                for confFile in confFiles:
                    if confFile==filename:
                        confb64=b64file(confDirectory + os.sep + net + os.sep + confFile)
        return confb64
    except ValueError as e: 
        #catches bad dir names that don't resolve to IP networks.
        pass

def iocList(ipaddress):
    '''returns a list of dictionaries containing ioc files meant for the calling IP'''
    #looks lin iocDirectory for subdirectories corresponding to netblock cidr masks
    #i.e. ./iocs/172.21.1.0-24 will contain ioc files meant for clients in the 172.21.1.0/24 cidr range.
    logEntry('checking iocs for ip: %s'%(ipaddress))
    netdirs=[]
    iocsList=[]
    if os.path.exists(iocDirectory):
        netdirs=os.listdir(iocDirectory)     
    try: 
        for net in netdirs:
            if IPAddress(ipaddress) in IPNetwork(net.replace('-','/')):
                iocFiles=os.listdir(iocDirectory + os.sep + net)
                for iocFile in iocFiles:
                    ioc={}
                    if '.ioc' in iocFile:
                        ioc['filename']=iocFile
                        ioc['sha1hash']=hashfile(iocDirectory + os.sep + net + os.sep + iocFile)
                        iocsList.append(ioc)
    except ValueError as e: 
        #catches bad dir names that don't resolve to IP networks.
        logEntry(e)
        pass
    except AddrFormatError as e:
        #catches bad dir names that don't resolve to IP networks.
        logEntry(e)
        pass
    return iocsList



def getIOCFile(filename,ipaddress):
    '''returns a base64 encode of the IOC file contents'''
    logEntry('request for file %s from ip: %s'%(filename,ipaddress))
    netdirs=os.listdir(iocDirectory)
    try: 
        iocb64=""
        for net in netdirs:
            if IPAddress(ipaddress) in IPNetwork(net.replace('-','/')):
                iocFiles=os.listdir(iocDirectory + os.sep + net)
                for iocFile in iocFiles:
                    if iocFile==filename:
                        iocb64=b64file(iocDirectory + os.sep + net + os.sep + iocFile)
        return iocb64
    except ValueError as e: 
        #catches bad dir names that don't resolve to IP networks.
        pass

def iocResult(ipaddress,iocResult):
    logEntry('%s returned %s'%(ipaddress,iocResult))

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--port", dest='port'  , default=8443, type="int", help="TCP Port to listen on")
    parser.add_option("-i", "--ip", dest='ipaddress' , default="0.0.0.0", help="IP Address to listen on (all IPs by default)")
    parser.add_option("-d", "--debug",action="store_true", dest="debug", default=False, help="turn on debugging output")    

    (options,args) = parser.parse_args()    
    
    
    logging.info("starting SOAP server on %s" %(options.port))
    ctx = SSL.Context('sslv23')
    
    try:
        ctx.load_verify_locations('certs/ca.crt')
        ctx.load_cert(certfile='certs/pyiocserver.pem',keyfile='certs/pyiocserver.key')#pem cert file
    except SSL.SSLError as e:
        sys.stderr.write("Error loading SSL Certs: %s\n"%(e))
        sys.stderr.write("Server expects a ./certs directory with pyiocserver.pem,pyiocserver.key and ca.crt files\n")
        sys.stderr.write("You can create simple certs using the 'simpleca.sh' script included with the pyioc distribution\n")
        sys.stderr.write("example: ./simpleca.sh pyiocserver\n")
        sys.exit(1)
    
    server = ThreadingSOAPServer((options.ipaddress, options.port),ssl_context=ctx)
    server.registerFunction(logEntry)
    server.registerFunction(iocList)
    server.registerFunction(getIOCFile)
    server.registerFunction(confList)
    server.registerFunction(getConfFile)
    server.registerFunction(iocResult)
    server.serve_forever()