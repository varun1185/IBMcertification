import os
import paramiko
import sys
import subprocess
import functools
#from datetime import date
from datetime import datetime, timedelta
import stat
import socket

#today = date.today()
#ldate = today.strftime("%Y%m%d")
ldate = datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d')
print(ldate)
pdate = datetime.strftime(datetime.now() - timedelta(1), '%m-%d-%Y')
print(pdate)

def doProcess(INPATH, OUTPATH):
    input1 = open(INPATH + "host.txt", "r")
    for i in input1:
        x = i.split()
        lpath = x[0] + "_" + ldate + "\\"
        new_path = OUTPATH + lpath
        print(x[0] + " " + x[1] + " " + x[2] + " " + x[3] + " " + x[5] + " " + OUTPATH + " " + new_path)
        if os.path.isdir(new_path):
           print("Local path exists: " + new_path)
        else:
            try:  
                os.mkdir(new_path)  
            except OSError as error:  
                print(error)
        try:  
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(x[1],x[2],x[3],x[4], banner_timeout=2000)

        except paramiko.AuthenticationException as error:
            print("Incorrect password: " + x[4])
            continue

        except socket.error as error:
            print("Socket error: %s" % error)
            continue

        except OSError as error:  
            print("OSError: %s" % error)        
            continue

        except Exception as error:
            print(error)
            continue
            
##Executing Date command in Server and storing input in cdate variable
#        stdin, stdout, stderr = ssh.exec_command(cmd)
#        lines = stdout.readlines()
#        rdate = lines[0].strip()

##Check if output path is pfm_output
        if "pfm_output" in x[5]:
            file_path = x[5] + ldate + "/"
            print("path is pfm_output",file_path)            
        else:
            file_path = x[5]
            print("path is not pfm_output",file_path)

##SFTP Into server
        sftp = ssh.open_sftp()

## Changing directory to current date directory        
        try:  
            sftp.chdir(file_path)
        except OSError as error:  
            print(error)
            continue
##Running For loop to download all files in the directory
        for filename in sorted(sftp.listdir()):
            file_local = new_path + x[0] + "_" + ldate + "_" + filename
            file_remote = file_path + filename
            fileattr = sftp.lstat(file_remote)

            if stat.S_ISREG(fileattr.st_mode):
                sftp.get(file_remote, file_local)
            if stat.S_ISDIR(fileattr.st_mode):
                continue

##Closing SFTP Connection
        sftp.close()

##Closing Transport Connection        
        ssh.close()
            
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Please provide input/output path")
        sys.exit()

INPATH = sys.argv[1]
OUTPATH = sys.argv[2]

doProcess(INPATH, OUTPATH)