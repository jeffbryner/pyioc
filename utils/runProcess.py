import wmi
import os
import getpass
import sys
from optparse import OptionParser

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-p", dest='targetIP' , help="destination ip address")
    parser.add_option("-P", dest='targetIPFile' ,  help="file of destination ip addresses")
    parser.add_option("-c", dest='targetCMD' ,  help="command to run")     
    (options,args) = parser.parse_args()

    #give some help if obviously wrong command line
    if len(sys.argv)==1 or options.targetCMD is None:
        parser.print_help()
        sys.exit()

    if options.targetIPFile is None:
        #just one targetIP specified via commandline
        wmiUser=raw_input("User:")
        wmiPassword=getpass.getpass()
        c=wmi.WMI(computer=options.targetIP,user=wmiUser,password=wmiPassword)
        process_id, return_value = c.Win32_Process.Create (CommandLine=options.targetCMD)
        for process in c.Win32_Process (ProcessId=process_id):
            print("Created processID: %s ProcessName: %s "%(str(process.ProcessId), process.Name))
  
    else:
        #we've got a file that should contain a list of target IPs as destinations: 
        if not os.path.isfile(options.targetIPFile):
            sys.stderr.write("Target file not found: %s\n"%(options.targetIPFile))
            parser.print_help()
            sys.exit(1)
        wmiUser=raw_input("User:")
        wmiPassword=getpass.getpass()

        with open(options.targetIPFile) as f:
            for line in f.readlines():
                #get rid of any cr/lf
                targetIP=line.replace('\n','')
                targetIP=targetIP.replace('\r','')
                #skip blank lines
                if len(targetIP)>0:
                    sys.stdout.write("targeting %s\n"%(targetIP))
                    c=wmi.WMI(computer=targetIP,user=wmiUser,password=wmiPassword)
                    process_id, return_value = c.Win32_Process.Create (CommandLine=options.targetCMD)
                    for process in c.Win32_Process (ProcessId=process_id):
                        print("Created processID: %s ProcessName: %s "%(str(process.ProcessId), process.Name))
                   
            
            

    sys.exit()
