#!/usr/bin/python3

import os 
import sys
import glob
import re

import gspread as gs
import pandas as pd

import pygsheets

def write_to_gsheet(service_file_path, spreadsheet_id, sheet_name, data_df):
    """
    this function takes data_df and writes it under spreadsheet_id
    and sheet_name using your credentials under service_file_path
    """
    gc = pygsheets.authorize(service_file=service_file_path)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        sh.add_worksheet(sheet_name)
    except:
        pass
    wks_write = sh.worksheet_by_title(sheet_name)
    wks_write.clear('A1',None,'*')
    wks_write.set_dataframe(data_df, (1,1), encoding='utf-8', fit=True)
    wks_write.frozen_rows = 1
    
def read_file(filename):
    rows = []
    actual_file=os.path.basename(filename)
    character=actual_file.split("-")[0]
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
    print(f"Uploading as sheet {character}")
    write_to_gsheet("auth.json","1V9xPxRnjxOFYwkPuGqhOFuuA-L4wcugVy_6G-lYtqPw",character,inv)
    print(inv)

def main(dir):
    for inv_file in glob.glob(f"{dir}/*-Inventory.txt"):
        read_file(inv_file)

if __name__ == "__main__":
    main(os.getenv("EQDIR","Everquest"))
