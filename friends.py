#!/usr/bin/python3 
import os 
import sys 
import glob 
from configparser import ConfigParser

# requires extra steps:
# mainly.. remove lowercase version


class CaseConfigParser(ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

def main(eqdir):
    friends=[]
    config=CaseConfigParser()
    if True:
        for ui_file in glob.glob(f"{eqdir}/*_P1999Green.ini"):
            if 'UI' in ui_file:
                continue
            config.read(ui_file)
            for key in config['Friends']:
                friend=config['Friends'][key]
                if friend != "*NULL*":
                    if friend not in friends:
                        friends.append(friend)
                        
    print(friends)
                        
    if True:
        for ui_file in glob.glob(f"{eqdir}/*_P1999Green.ini"):
            if 'UI' in ui_file:
                continue
            config=CaseConfigParser()
            config.read(ui_file)
            for i in range(0,100):
                if i<len(friends):
                    config['Friends'][f"Friend{i}"]=friends[i]
                else:
                    config['Friends'][f"Friend{i}"]="*NULL*"
            os.rename(ui_file,f"{ui_file}.old")
            print(f"writing {ui_file}")
                    
            with open(ui_file,'w') as fd:
                config.write(fd, space_around_delimiters=False)

if __name__=="__main__":
    main(os.getenv("EQDIR","Everquest"))
