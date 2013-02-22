pyioc is a set of tools to handle IOC files (openioc.org).

Some simple utilities for parsing IOC files:
iocdump.py: spit out the indicator items being referenced
iocwalk.py: parse the boolean logic behind the IOC and the items referenced.

pyiocClient: 
	A client for linux/windows that handles basic searches for Files, 
	processes, registry items and ports. It compiles to native linux/windows
	32 or 64bit code via pyinstaller and can therefore be run with no python
	interpreter on the client system. 
	
pyiocServer: 
	The server-side compliment to the client. It dishes out .ioc files to
	clients that call in via SOAP over SSL and logs the results of the
	client checks. 
	IOCs can be tailored by a simple directory structure corresponding to
	the net CIDR mask of the client system. 
	i.e. 
	iocs/172.21-16/firefox.ioc
	will issue the firefox.ioc to any system inthe 172.21.0.0/16 ip range
	when the client is run.
	
	
Python library prereqs

python 2.7
Client: 
        SOAPpy
        M2Crypto
        psutil          
        lxml v2.3.2 ( pip install lxml==2.3.2 )
	regobj
	pefile
	python-magic
	python-dateutil

Server: 
        SOAPpy
        M2Crypto
        netaddr

If you're on linux you can get the libs through your favorite package manager
or via pip. 

On windows x64, pip or through the following sources: 
win64
        python2.7                       http://python.org/download/
        psutil: exe                     http://www.lfd.uci.edu/~gohlke/pythonlibs/
        lxml : .exe                     http://www.lfd.uci.edu/~gohlke/pythonlibs/
        m2crypto: exe                   http://chandlerproject.org/Projects/MeTooCrypto#Contributed%20Builds
        soappy: pip install soappy
        pywin32: exe                    http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/
        pyinstaller:                    http://www.pyinstaller.org/

Native builds for various platforms can be found in the builds directory.

Notes on Setup for the server:
It expects several subdirectories to exist: 
./certs
./confs
./iocs

./certs should contain at least: 
	ca.crt
	pyiocserver.pem
	pyiocserver.key
which you can create using the simpleca.sh script, use the default from github (note the risk that you're using a publically 
available 'private' key) or ideally; use your internal CA.

The confs directory is your chance to issue configuration files to pyiocClients in real time. 
The iocs directory is where you create netblocks (./iocs/172.21-16 for example) and publish .ioc files you want the clients to 
process.

