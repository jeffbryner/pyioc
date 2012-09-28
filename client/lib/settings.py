#!/usr/bin/python2
import platform 

VERSION= 0.1
DESCRIPTION = "IOC client to search a system for indicators of compromise"

#client context
PLATFORM='linux'
if 'win' in platform.system().lower():
    PLATFORM='win'
if 'linux' in platform.system().lower():
    PLATFORM='linux'    
if 'darwin' in platform.system().lower():
    PLATFORM='mac'

#how deep in terms of directory levels to search for a file name or extension
#used in place of walking every directory to all levels to increase performance
#by using glob-style matching i.e. /*/*/*
DIRECTORYRECURSELIMIT=4    