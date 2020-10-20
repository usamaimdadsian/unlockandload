import os
from random import randint
import pyminizip
from zipfile import ZipFile
import sqlite3
import datetime

import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


# Generate password
def generatePassword(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

# generate password protected zip file
def makeZip(src,password):
    # pyminizip.compress("folder/file.txt","", "folder/file.zip", "noneshallpass", 9)
    dest=src[:src.find(".")]+".zip"
    pyminizip.compress(src,"", dest,password, 9)
    os.remove(src)
    print("{} is successfully Ziped".format(src))
    return dest

# unzip the file
def unzipFile(file_path, password):
    x = file_path[:file_path.find("/")]+"/"
    zf = ZipFile(file_path,'r')
    uncompress_size = sum((file.file_size for file in zf.infolist()))
    if uncompress_size <= 0:
        uncompress_size = 1
    extracted_size = 0
    for file in zf.infolist():
        extracted_size += file.file_size
        # print(extracted_size * 100/uncompress_size)
        print("%s %%" % (extracted_size * 100/uncompress_size))
        zf.extract(file,path=x,pwd=bytes(password,'ascii'))
    os.remove(file_path)

# insert values to the record table
def insertValues(path,password,status):
    conn = sqlite3.connect('unlockandload.db')
    # rows = conn.execute('INSERT INTO record(id, path, password, status) VALUES (1,"folder","1234",0);')
    rows = conn.execute('INSERT INTO record(path, password, status) VALUES ("{}","{}",{});'.format(path,password,status))
    conn.commit()
    conn.close()
def updateValues(path,time):
    conn = sqlite3.connect('unlockandload.db')
    rows = conn.execute('UPDATE record SET status=1 , time="{}" WHERE path = "{}"'.format(time,path))
    conn.commit()
    conn.close()
# get values from the record table
def getValues(param):
    conn = sqlite3.connect('unlockandload.db')
    rows = conn.execute(param)
    rows = rows.fetchall()
    conn.close()
    return rows

def passwordProtectedZipCreation(folder):
    dir_list =  os.listdir()
    for dirr in dir_list:
        if os.path.isdir(dirr) and dirr.find(folder) != -1:
            files = os.listdir(dirr)
            files.sort(key=natural_keys)
            for filee in files:
                path = dirr + "/"+filee
                paswword = str(generatePassword(5))
                path = makeZip(path,paswword)
                insertValues(path,paswword,0)

def extractionProcess():
    st = getValues("SELECT * FROM record WHERE status=1")
    if not st:
        rows = getValues("select * from record ORDER BY id LIMIT 1")
        path = rows[0][1]
        password = rows[0][2]
        then = datetime.datetime.now()-datetime.timedelta(days=1)
    else:
        rows = getValues("SELECT * FROM record ORDER BY time DESC LIMIT 1")
        then = rows[0][4]
        rid = rows[0][0]+1
        rows = getValues("SELECT * FROM record WHERE id={}".format(rid))
        path = rows[0][1]
        password = rows[0][2]
        then = datetime.datetime(int(then[:4]),int(then[5:7]),int(then[8:10]),int(then[11:13]),int(then[14:16]),int(then[17:19]))
    now = datetime.datetime.now()
    timeleft = now - then
    if datetime.timedelta(hours = 18) < timeleft:
        time =now.strftime("%Y-%m-%d %H:%M:%S")
        updateValues(path,time)
        unzipFile(path,password)
    else:
        print(datetime.timedelta(hours = 18)-timeleft)



if __name__ == "__main__":
    x=input("Enter 1 to unlock next file, 2 to zip all files:")
    if x==str(1):
        extractionProcess()
    elif x == str(2):
        folder = input("Enter directory Name")
        passwordProtectedZipCreation(folder)
    
    # rows = getValues("SELECT * FROM record")
    # print(rows)