import time
import os
import sys
import re
import datetime
import glob
import curses

def print_price(copper):
    plat=int(copper/ 1000)
    copper-=plat*1000
    gold=int(copper /100)
    copper-=gold*100
    silver=int(copper /10)
    copper-=silver*10
    return f"{plat}p {gold}g {silver}s {copper}c"


def follow(thefile):
    """generator function that yields new lines in a file"""
    # seek the end of the file
    thefile.seek(0, os.SEEK_END)
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()
        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue
        yield line

def latest_file(folder_path):
    file_type = r"/eqlog*.txt"
    files = glob.glob(folder_path + file_type)
    return max(files, key=os.path.getctime)

def main(stdscr=None):
    prices={}
    with open("prices.cfg",'r') as fd:
        for line in fd.readlines():
            line=line.rstrip()
            (item,price)=line.split("\t")
            prices[item]=int(price)

    if len(sys.argv) > 1:
        logfile_name = sys.argv[1]
        logfile_search = False
    else:
        logfile_name = latest_file("/mnt/h/Games/Everquest/Logs")
        logfile_search = True
    while True:
        logfile = open(logfile_name)
        if logfile_search:
            loglines = follow(logfile)
        else:
            loglines = logfile.readlines()
        # iterate over the generator
        for line in loglines:
            if logfile_search:
                latest_logfile = latest_file("/mnt/h/Games/Everquest/Logs")
                if latest_logfile != logfile_name:
                    break
            m=re.match(".*You have looted a (.+)\.--",line)
            if m:
                item = m.group(1)
                if item in prices:
                    print(f"{item} {print_price(prices[item])}")
                else:
                    print(f"Not seen {item}")
        if not logfile_search: break
if __name__=='__main__':
    main()