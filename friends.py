#!/usr/bin/python3 
import os 
import sys 
import glob 
from configparser import ConfigParser

class CaseConfigParser(ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

friends=[]
config=CaseConfigParser()
if True:
	for ui_file in glob.glob("/mnt/h/Games/Everquest/*_P1999Green.ini"):
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
	for ui_file in glob.glob("/mnt/h/Games/Everquest/*_P1999Green.ini"):
		if 'UI' in ui_file:
			continue
		config=CaseConfigParser()
		config.read(ui_file)
		for i in range(0,100):
			if i<len(friends):
				config['Friends'][f"Friend{i}"]=friends[i]
			else:
				config['Friends'][f"Friend{i}"]="*NULL*"
	
		filename=os.path.basename(ui_file)
		print(f"writing {filename}")
		with open(filename,'w') as fd:
			config.write(fd, space_around_delimiters=False)
