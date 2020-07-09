#!/usr/bin/python3
'''
Created on May 5, 2020

@author: RaghuwanshiS

'''
import time
import sys
import os
from getpass import getpass
from ftplib import FTP
from datetime import date

def Ftp_loop_func():
    ftp_y_n = input("Please enter your option as '1' or '2' : ")
    print('                                         ')
    ftp_decision = 0
    
    while ftp_decision != None:
        if (ftp_y_n.isnumeric() and int(ftp_y_n) == 1) or (ftp_y_n.isnumeric() and int(ftp_y_n) == 2):
            print('You Selected "' + ftp_y_n + '" i.e.', end='  ')
            ftp_decision = None
        elif len(ftp_y_n) == 0:
            print('No input received...Bye!!')
            time.sleep(5)
            sys.exit()
        else:
            print('Invalid option selected. Please try again!')
            print('                                         ')    
            ftp_y_n = input("Please Select From '1' & '2' : ")
            print('                                         ')
    else:
        return ftp_y_n

def Pctomf(usrname):
    print("PC -------> MF")
    local_file_w_path =  input('Please enter the file name with complete PATH: ')
    print('                                          ')   
    print("Copying " + local_file_w_path)
    
    #EOL for Window = CRLF, LINUX=LF, MAINFRAME=CR
    #CR = \r
    #LF = \n
    try:
        f1 = open(local_file_w_path, 'rb')
        eol_seek = f1.readline()
        if eol_seek.find(b'\r\n') != -1 :
            print("Windows Format")
            file_format = 'W'
        elif eol_seek.find(b'\n') != -1 :
            print("Unix Format")
            file_format = 'U'
        else:
            print("Mainframe Format")
            file_format = 'M'
    except:
        raise
    finally:
        f1.close()
    
    if file_format == 'M' :
        with open(local_file_w_path, 'rb') as open_file:
            content = open_file.read()
        
        content = content.replace(b'\r',b'\n')
        
        with open(local_file_w_path, 'wb') as open_file:
            open_file.write(content)

    #Get the LRECL of the text file for FTP
    try:
        lrecl = len(max(open(local_file_w_path, 'rb'), key=len))
    except Exception as e:
        print("Error Occurred while using file " + local_file_w_path)
        print("Problem: ", e)
        time.sleep(60)
        ftp.quit()
        sys.exit()
    
    if file_format == 'W':
        lrecl = lrecl - 2
    elif file_format == 'U':
        lrecl = lrecl = 2
    else:
        lrecl = lrecl - 1
        
    local_file_size = os.stat(local_file_w_path).st_size
    print("---------------")
    print("File Attributes")
    print("---------------")
    print("     LENGTH : " + str(lrecl))
    print("     SIZE   : " + str(local_file_size/1024) + " KB")
    print("                ")
    t1 = time.time()
    send_instrution = "SITE LRECL=" + str(lrecl) + " RECFM=FB BLKSIZE=0 CYLINDERS PRIMARY=500 SECONDARY=500 TRAILingblanks NOWRAPRECORD"
    ftp.voidcmd(send_instrution)
    local_file = str(local_file_w_path.rsplit(sep='\\',maxsplit=1)[-1])
       
    if len(local_file) > 36:
        local_file = local_file[:35]
    
    try:
        print("Please Wait...")
        ftp.storlines("STOR " + local_file, open(local_file_w_path,'rb'))
    
        t2 = time.time()
    
        print("Time Elapsed: ", round(((t2-t1)/60),2), "Minutes")
        print("                                ")
        print("File Transfer complete!\n\nPlease look for dataset '" + usrname.upper() + '.' + local_file.upper() + "' in mainframe.\n")
        print("NOTE: THE CREATED FILE IS IN 'WORK' VOLUME. PLEASE COPY IT IN YOUR PERMANENT DATASET.")
        ftp.voidcmd('CDUP')
    except Exception as e:
        print("Error Occurred!!! Please report below to Sachin.raghuwanshi@broadridge.com.")
        print("Problem: ", e)
        time.sleep(200)
    
    return
    

def Mftopc():
    print("MF -------> PC")
    
    mf_file =  input('Please enter the Dataset name: ')
    print('                                          ')
    mf_file_path = '\\' + mf_file
    print("Transferring " + mf_file.upper() + ' to your DESKTOP!' ,end="\n")

    try:
        ftp.voidcmd('CDUP') #to remove the default Current Working directory from TBSARAG.
    except Exception as e:
        print("Warning: ", e, "Continuing with ftp request")
    ftp.sendcmd('SITE AUTORECALL') #perform HRECALL on the MF dataset in case dataset is migrated.
    
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    local_filename = desktop + mf_file_path + '.txt'
    
    try:
        foo=open(local_filename,'w')
        def customWriter(line):
            foo.write(line + '\r')
    
        print("Please Wait...")
        ftp.retrlines("RETR " + mf_file, customWriter)
        print("File Transfer complete!\n\nFile is copied in your DESKTOP.\n")
    except Exception as e:
        print("\nError Occurred!!")
        print("Error is : ", e)
            
    return

print(date.today().strftime("%B %d, %Y"))
print('=========================================')
print(r'|         BROADRIDGE FTP UTILITY        |')
print('=========================================')
print('                                        ')

usernm = input("Please Enter your Mainframe ID      : ")
passwd = getpass(prompt='Please Enter your Mainframe Password: ', stream=None) 
continue_ftp = 'Y'
continue_decision = True
print('                                         ')

try:
    ftp = FTP('112.12.223.13')  
    ftp.login(usernm,passwd) 
except:
    print('Your credentials are invalid. \nTerminal will close in 5 seconds!!')
    time.sleep(5)
    sys.exit()
else:
    print('Login Successful')
    print('                ')

    while continue_decision:
        print('=========================================')
        print('FTP OPTIONS:                            ')
        print('1. FTP from MF(Remote) ----> PC(Local)')
        print('2. FTP from PC(Local) ----> MF(Remote)')
        print('=========================================')
        print('                                         ')
        ftp_direction = Ftp_loop_func()
        
        if int(ftp_direction) == 1:
            Mftopc()
        else:
            Pctomf(usernm)
    
        continue_ftp = input("Would you like to do another FTP. Type (Y/N): ")

        if continue_ftp == 'N' or  continue_ftp == 'n':
            continue_decision = False

            
    
    else:
        print('                                ')
        print('=========================================================================================')
        print('THANKS!!! YOU CAN SHARE ANY FEEDBACK FOR IMPROVEMENT @ Sachin.Raghuwanshi@broadridge.com ')
        print('=========================================================================================')
        time.sleep(600)
        ftp.quit()
        time.sleep(3)
