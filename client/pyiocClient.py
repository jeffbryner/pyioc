#!/usr/bin/python2
import os
import sys
import platform
import SOAPpy
from M2Crypto import SSL
import tempfile
from base64 import b64decode
import psutil
import shutil
from hashlib import sha1
import lxml.objectify
import socket
import ConfigParser
from optparse import OptionParser
from datetime import datetime

#local package imports
import iocItems
from iocItems import ProcessItem
from iocItems import PortItem
from iocItems import FileItem
from iocItems import RegistryItem
from lib.settings import PLATFORM
from lib import log
from lib.log import debug,critical,error,info

def getmyip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((options.iocServer,int(options.serverPort)))
    myip= s.getsockname()[0]
    s.close()
    return myip

def cleanup():
    shutil.rmtree(iocDir)

def hashfile(filepath):
    '''get the sha1 hash of a file's contents'''
    sha1hash = sha1()
    f = open(filepath, 'rb')
    try:
        sha1hash.update(f.read())
    finally:
        f.close()
    return sha1hash.hexdigest()

def fillFileCache(root):
    """See if we have a file name or directory in our .ioc file we can use to narrow the files we search
       and fill our cache of file names for future ioc queries"""
    global fileCacheItems, cache
    for ii in root.findall("//*[local-name()='IndicatorItem']"):
        if 'fileitem/filename' in ii.Context.attrib.get("search").lower():
            cache=True
            FileItem.filename(ii.Content,fileCacheItems,True)
        if 'fileitem/fullpath' in ii.Context.attrib.get("search").lower():
            cache=True
            FileItem.fullpath(ii.Content,fileCacheItems,True)        
        if 'fileitem/filepath' in ii.Context.attrib.get("search").lower():
            cache=True
            FileItem.filepath(ii.Content,fileCacheItems,True)        
            
    
    
def processIOCFile(filename):
    ioco=lxml.objectify.parse(filename)
    root=ioco.getroot()
    fillFileCache(root)
    for Indicator in root.findall("//*[local-name()='Indicator']")[0]:
        walkIndicator(Indicator)    

def walksearches(ind):
    #build a list of everything we will be searching below the given indicator
    #used to preview future ioc checks to save lists of files, registry entries, etc.
    searches=[]
    for i in ind.findall(".//*[local-name()='Context']"):
        searches.append(i.attrib.get("search"))
    return searches

def walkIndicatorItems(ind):
    global level,iocEvalString, fileCacheItems,regCacheItems
    cache=False

    lastii=ind.findall("./*[local-name()='IndicatorItem']")[-1]

    #if we are to look for a filename/registry, then attributes of the hit, save the hit.
    searches=walksearches(ind)
    if ('FileItem/' in str(searches)) or ('RegistryItem/' in str(searches)):
        cache=True
        
    for i in ind.findall("./*[local-name()='IndicatorItem']"):        
        #do we know how to handle this IOC?
        #split it into category/attribute
        itemTarget=i.Context.attrib.get("search")        
        iocMajorCategory=itemTarget.split('/')[0]
        #iocAttribute=itemTarget.split('/')[-1]
        #Under the major category, concat all the attributes into one function name
        #to see if we know how to handle it.
        #i.e. FileItem/PEInfo/ImportedModules/Module/ImportedFunctions/string
        #becomes PEInfoImportedModulesModuleImportedFunctionsstring
        iocAttribute=''.join(itemTarget.split('/')[1:])
        #some ioc attributes are all lower, 1 upper, then lower, camel case, etc..normalize to lower case.
        iocAttribute=iocAttribute.lower()
        #optimistic result default. change if you are pessimistic ;-]
        iocResult= False        
        #let python tell us what functions we support by eval'ing our include iocItems modules.
        if iocMajorCategory in dir(iocItems):
            if iocAttribute in dir(eval(iocMajorCategory)):
                #tell the function about items we've cached? 
                if 'cacheItems' in eval(iocMajorCategory + '.' + iocAttribute + '.func_code.co_varnames'):
                    #iocResult=eval(iocMajorCategory + '.' + iocAttribute + '("' + str(i.Content) + '")')
                    #python hates trailing backslashes, strip it off
                    sContent=i.Content.text
                    if sContent[-1]=='\\':
                        sContent=sContent[:len(sContent)-1]
                        
                    if cache and iocMajorCategory=="FileItem":
                        iocResult=eval("%s.%s('%s',fileCacheItems,True)" %(iocMajorCategory,iocAttribute,sContent))
                        debug('cache items: %s' %(str(fileCacheItems)))
                    elif cache and iocMajorCategory=="RegistryItem":
                        iocResult=eval("%s.%s('%s',regCacheItems,True)" %(iocMajorCategory,iocAttribute,sContent))
                        debug('cache items: %s' %(str(regCacheItems)))
                        
                    else:
                        iocResult=eval("%s.%s(r'%s',[],False)" %(iocMajorCategory,iocAttribute,sContent))

                else:
                    #iocResult=eval(iocMajorCategory + '.' + iocAttribute + '("' + str(i.Content) + '")')
                    iocResult=eval("%s.%s(r'%s')" %(iocMajorCategory,iocAttribute,i.Content.text))
                
                #was this a condition testing false? i.e. isnot
                if 'not' in i.attrib.get("condition").lower() and iocResult==True:
                    iocResult= not iocResult
            else:
                debug('cannot evaluate %s'%( (iocMajorCategory + '.' + iocAttribute + '("' + str(i.Content) + '")')))
        else:
            debug('cannot evaluate %s'%( (iocMajorCategory + '.' + iocAttribute + '("' + str(i.Content) + '")')))

        logicOperator=str(i.getparent().attrib.get("operator")).lower()        
        if i == lastii:
            debug('\t'*level + str(iocResult))
            info('\t'*level + i.Context.attrib.get("search") + ' ' + i.attrib.get("condition") + ' ' + str(i.Content))            
            iocEvalString+=' ' + str(iocResult)
        else:
            debug('\t'*level + str(iocResult) +' ' + str(logicOperator))
            info('\t'*level + i.Context.attrib.get("search") + ' ' + i.attrib.get("condition") + ' ' + str(i.Content) + ' ' + str(logicOperator))            
            iocEvalString+=' ' + str(iocResult) + ' ' + str(logicOperator)



def walkIndicator(ind):
    global level,iocEvalString,fileCacheItems,regCacheItems
    #walk any indicator items first: 
    if len(ind.findall("./*[local-name()='IndicatorItem']"))>0:
        walkIndicatorItems(ind)     

    #walk any indicators (and their indicator items recursively)
    for i in ind.findall("./*[local-name()='Indicator']"):          
        level+=1
        logicOperator=str(i.attrib.get("operator")).lower()
        debug('\t'*level + logicOperator + ' (')

        #don't add a logic operator as the starting point..python won't eval 'or (True)'
        if len(iocEvalString)==0:
            iocEvalString += ' ('
        elif iocEvalString.strip().endswith("("):
            iocEvalString+=' ('
        else:
            iocEvalString += ' ' + logicOperator + ' ('            
        walkIndicator(i)
        level-=1
        #cacheItems=[]
        debug('\t'*level + ' )')
        iocEvalString += ' )'



    


def defaultConfig():  
    log.logfile='pyiocClient.log'    
    log.loglevel = log.loglevels['debug']


def processConfigFile(configfile):
    if os.path.isfile(configfile):
        debug("reading config file: %s"%(configfile))
        config = ConfigParser.ConfigParser()
        config.readfp(open(configfile))
        if config.has_option('core','iocServer'):
            #info("iocServer: %s"%(config.get('core','iocServer')))
            options.iocServer=config.get('core','iocServer')
            debug('set options.iocServer: %s'% (options.iocServer))
        if config.has_option('core','logfile'):
            log.logfile = config.get( 'core', 'logfile' )
            debug('set logfile: %s' % (log.logfile))
        if config.has_option('core','loglevel'):
            log.loglevel    = log.loglevels[config.get( 'core', 'loglevel' )]
            debug('set loglevel: %s' % (log.loglevel))            
    else: 
        error('bad config file %s'%(configfile))



def setPriority(): 
    #set priority
    p = psutil.Process(os.getpid())
    if PLATFORM=='linux':
        #-20 to 20, higher is lower priority.
        p.nice = 0  
        p.set_ionice(psutil.IOPRIO_CLASS_IDLE)

    if PLATFORM=='win':
        #Levels highest to lowest: 
        #http://msdn.microsoft.com/en-us/library/ms686219%28v=vs.85%29.aspx
        #http://msdn.microsoft.com/en-us/library/windows/desktop/ms685100%28v=vs.85%29.aspx
        #REALTIME_PRIORITY_CLASS      : preempt os
        #HIGH_PRIORITY_CLASS          : preempt the threads of normal or idle priority class processes
        #ABOVE_NORMAL_PRIORITY_CLASS  : priority above NORMAL_PRIORITY_CLASS but below HIGH_PRIORITY_CLASS
        #NORMAL_PRIORITY_CLASS        : no special scheduling needs
        #BELOW_NORMAL_PRIORITY_CLASS  : priority above IDLE_PRIORITY_CLASS but below NORMAL_PRIORITY_CLASS
        #IDLE_PRIORITY_CLASS          : threads run only when the system is idle

        p.nice = psutil.BELOW_NORMAL_PRIORITY_CLASS    


if __name__ == "__main__":

    level=1
    fileCacheItems=[]
    regCacheItems=[]
    iocEvalString=""
    parser = OptionParser()
    parser.add_option("-s", dest='iocServer'   , default='127.0.0.1', help="name or IP address of IOC Server")
    parser.add_option("-p", dest='serverPort' , default='8443', help="port of IOC service on IOC Server")
    parser.add_option("-c", dest='configfile' , default='pyiocClient.conf', help="configuration file to use")     
    
    #config is default, overridden by command line, overridden by config file, overridden by server
    defaultConfig()
    (options,args) = parser.parse_args()
    if os.path.isfile(options.configfile):
        processConfigFile(options.configfile)

    log.setLogging()

    ctx=SSL.Context('sslv23')
    serverURL="https://%s:%s"%(options.iocServer,options.serverPort)
    debug('connecting to server: %s'%(serverURL))
    server=SOAPpy.SOAPProxy(serverURL)
    iocDir = tempfile.mkdtemp(prefix = 'iocTmp')
    debug("using temp dir %s"%(iocDir))
    myip = getmyip()

    #check for config file from server which will override our local config file.
    for conf in server.confList(myip):
        info('conf file assigned to me: %s'%(conf))
        confContent=server.getConfFile(conf['filename'],myip)
        confFileHandle, confFileName =tempfile.mkstemp(suffix="conf",dir=iocDir,text=True)
        confFile=os.fdopen(confFileHandle,'w+')
        confFile.write(b64decode(confContent))
        confFile.close()
        #got file, now process 
        info('conf file successfully retrieved: %s'%(conf['filename']))
        processConfigFile(confFileName)
    
    #reset logging in case we've changed.
    log.setLogging()
    #set priority
    setPriority()
    
    for ioc in server.iocList(myip):
        debug('got ioc: %s'%(ioc))
        #clear any files,registry entries we may have cached from the last ioc
        fileCacheItems=[]
        regCacheItems=[]
        iocContent=server.getIOCFile(ioc['filename'],myip)
        iocFileHandle, iocFileName =tempfile.mkstemp(suffix="ioc",dir=iocDir,text=True)
        iocFile=os.fdopen(iocFileHandle,'w+')
        iocFile.write(b64decode(iocContent))
        iocFile.close()
        #got file, now process ioc items
        info('ioc file successfully retrieved: %s'%(ioc['filename']))
        processIOCFile(iocFileName)
        debug(iocEvalString)
        resultString=('iocResult: %s %s' %(ioc['filename'],str(eval(iocEvalString))))
        info(resultString)
        server.iocResult(myip,resultString)
        iocEvalString=""

    cleanup()
