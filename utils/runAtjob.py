import wmi
import os
import datetime
import sys
import getpass
from optparse import OptionParser

#if len(sys.argv)!=3:
    #print("""
    #runAtJob.py: setups up an AT job on the target host to run the command given a minute from now
    #Usage:
    #runAtjob.py targetIP targetCMD    
    #""")
    #sys.exit()
        
#targetIP=sys.argv[1]
#targetCMD=sys.argv[2]

#wmiUser=raw_input("User:")
#wmiPassword=getpass.getpass()
#c=wmi.WMI(computer=targetIP,user=wmiUser,password=wmiPassword)

#onemin = datetime.datetime.now () + datetime.timedelta (minutes=1)
#job_id, result = c.Win32_ScheduledJob.Create (Command=targetCMD,StartTime=wmi.from_time(year=onemin.year,month=onemin.month,day=onemin.day,hours=onemin.hour,minutes=onemin.minute,seconds=onemin.second,microseconds=0,timezone=-420))
#print("job: %s created" %(job_id))




if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-p", dest='targetIP' , help="destination ip address")
    parser.add_option("-P", dest='targetIPFile' ,  help="file of destination ip addresses")
    parser.add_option("-c", dest='targetCMD' ,  help="command to run")     
    parser.add_option("-m", dest='minutes' , default="1", help="minutes in the future to schedule the job")
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
        #when do we run (calc'd after password entry on purpose)
        runtime = datetime.datetime.now () + datetime.timedelta (minutes=int(options.minutes))
        print(wmi.from_time(year=runtime.year,month=runtime.month,day=runtime.day,hours=runtime.hour,minutes=runtime.minute,seconds=runtime.second,microseconds=0,timezone=-420))
        job_id, result = c.Win32_ScheduledJob.Create (Command=options.targetCMD,StartTime=wmi.from_time(year=runtime.year,month=runtime.month,day=runtime.day,hours=runtime.hour,minutes=runtime.minute,seconds=runtime.second,microseconds=0,timezone=-420))
        print("job: %s created" %(job_id))
  
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
                    #when do we run (calc'd for each server as we reach it in the list)
                    runtime = datetime.datetime.now () + datetime.timedelta (minutes=int(options.minutes))
                    c=wmi.WMI(computer=targetIP,user=wmiUser,password=wmiPassword)
                    job_id, result = c.Win32_ScheduledJob.Create (Command=options.targetCMD,StartTime=wmi.from_time(year=runtime.year,month=runtime.month,day=runtime.day,hours=runtime.hour,minutes=runtime.minute,seconds=runtime.second,microseconds=0,timezone=-420))
                    print("job: %s created" %(job_id))

    sys.exit()
