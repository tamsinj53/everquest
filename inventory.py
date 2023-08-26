#!/usr/bin/python3

import os 
import sys
import glob

import gspread as gs
import pandas as pd


def read_file(filename):
    rows = []
    with open(filename,'r') as fd:
        for line in fd.readlines():
            if line.startswith("Location"): continue
            if line.startswith("Bank") and not "-" in line:
                if int(line[4:6])>8:
                    continue
            if line.startswith("SharedBank"): continue
            dict1= {}
            (location,name,id,count,slots)=line.split("\t")
            dict1.update({'location':location,'name':name,'count':count})
            rows.append(dict1)
    inv=pd.DataFrame(rows)

    print(inv)

def main():
    for inv_file in glob.glob("/mnt/h/Games/Everquest/*-Inventory.txt"):
        read_file(inv_file)

if __name__ == "__main__":
    main()
