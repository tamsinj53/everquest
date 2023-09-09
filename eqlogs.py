#!/usr/bin/python3
# library routines for reading eq logs
import os
import sys
import glob
import re
import datetime
import sqlite3
import pandas
import psycopg
from psycopg2.extensions import adapt
import toml

def data_import(eqdir):
    # import logs into structured data
    ""

class Money:
    def __init__(self,amount):
        self.coppers=self.parse_money(amount)

    def __add__(self,money):
        if money is str:
            self.coppers+=self.parse_money(money)

    def __int__(self):
        return self.coppers

    def __str__(self):
        return f"{int(self.coppers / 1000)} platinum, {int((self.coppers % 1000)/100)} gold, {int((self.coppers % 100)/10)} silver and {self.coppers % 10} copper"
    
    def parse_money(self,amount):
        # returns coppers
        # 670 platinum, 6 gold, 5 silver and 3 copper
        # 1 gold, 5 silver and 9 copper
        if isinstance(amount,int):
            return amount
        plat=re.search("([0-9]+) platinum",amount)
        gold=re.search("([0-9]+) gold",amount)
        silver=re.search("([0-9]+) silver",amount)
        copper=re.search("([0-9]+) copper",amount)

        coppers=0
        if plat: coppers+=1000*int(plat.group(1))
        if gold: coppers+=100*int(gold.group(1))
        if silver: coppers+=10*int(silver.group(1))
        if copper: coppers+=int(copper.group(1))
        return coppers

class logfile:
    def __init__(self,filename,db,character=None):
        self.debug=True
        self.filename=filename
        self.db=db
        if character is None:
            self.character = self.get_character_name(filename)
        else:
            self.character = character
        self._schema()
        self.ingest()

    def _schema(self):
        print("LOADING SCHEMA")
        to_cur=self.db.cursor()
        to_cur.execute("CREATE TABLE IF NOT EXISTS zoning (timestamp TIMESTAMP UNIQUE, character VARCHAR, zonename VARCHAR);")
        to_cur.execute("CREATE TABLE IF NOT EXISTS cash (timestamp TIMESTAMP UNIQUE, character VARCHAR, amount int);")
        to_cur.execute("CREATE TABLE IF NOT EXISTS loot (timestamp TIMESTAMP UNIQUE, character VARCHAR, item str);")
        to_cur.execute("CREATE TABLE IF NOT EXISTS comms (timestamp TIMESTAMP UNIQUE, character VARCHAR, from str, comm_type strx);")
        self.db.commit()

    def get_character_name(self,filename):
        filename=os.path.basename(filename)
        m=re.match("^([^-]+)-Inventory.txt$",filename)
        if m:
            character_name=m.group(1)
            if self.debug: print(f"match {filename} to {character_name}")
            return character_name
        m=re.match("^eqlog_([^_]+)_P1999Green.txt",filename)
        if m:
            character_name=m.group(1)
            if self.debug: print(f"match {filename} to {character_name}")
            return character_name
        raise("Failed to parse name")

        
    
    def parse_logline(self,line):
        match=re.match('^\[([^\]]+)\] (.*)',line)
        if match:
            timestamp=datetime.datetime.strptime(match.group(1),"%a %b %d %H:%M:%S %Y")
            return (timestamp,match.group(2))
        else:
            return (None,None)
        
    def store_zone(self,cursor,timestamp,text):
        # Zoning table
        match=re.match("^You have entered (.*)\.$",text)
        if match:
            zone=match.group(1)
            print(f"Zoned into {zone}")
            zone=zone.replace("'","\\'")
            cursor.execute(f"INSERT INTO zoning SELECT '{timestamp}', '{self.character}', %s WHERE NOT EXISTS (SELECT timestamp from zoning WHERE timestamp = '{timestamp}');",[zone])

    def store_comms(self,cursor,timestamnp,text):
        ""

    def store_vendor(self,cursor,timestamp,text):
        ""

    def store_trade(self,cursor,timestamp,text):
        ""

    def store_looted(self,cursor,timestamp,text):
        match=re.match("--You have looted (.+).--",text)
        if match:
            looted=match.group(1)
            print(f"Looted {looted}")
            return
        match=re.match("You receive (.+) from the corpse.",text)
        if match:
            looted=Money(match.group(1))
            print(f"Looted {looted}")
            return

    def ingest(self):
        # import specific logfile.
        # - Extract charactername from filename if unspecified
        # Read every logline and then:
        # - Store zone entries in zone table
        # - Store communications in comms table
        # - Store vendors into vendor table
        # - Store player trades in trade table
        # - Record final timestamp in files table for future reference
        
        # [Thu Jun 01 21:26:12 2023] Welcome to EverQuest!
        # [Thu Jun 01 21:26:12 2023] If you need help, click on the EQ Menu button at the bottom of your screen and select the "Help" option.
        # [Thu Jun 01 21:26:12 2023] You have entered Erudin.
        # [Mon Mar 06 21:24:19 2023] You have been slain by an iksar marauder!
        # [Mon Mar 06 21:24:19 2023] You have lost experience.
        # [Sun Mar 05 13:10:53 2023] Klok Mugruk tells you, 'I'll give you 5 gold 1 silver 3 copper for the A Wolf Scale.'
        # [Sun Mar 05 13:10:55 2023] You receive 5 gold 1 silver 3 copper from Klok Mugruk for the A Wolf Scale(s).
        # [Mon Mar 06 21:35:33 2023] You receive 8 copper from the corpse.
        # [Mon Mar 06 21:35:34 2023] --You have looted a Tarnished Sheer Blade.--
        # [Sat Mar 11 13:06:29 2023] Klok Sass tells you, 'I'll give you 1 silver 4 copper per Short Beer'
        # [Sat Mar 11 13:06:32 2023] You receive 7 silver from Klok Sass for the Short Beer(s).
        # [Fri Sep 08 17:36:57 2023] You receive 670 platinum, 6 gold, 5 silver and 3 copper from the corpse.

        
        cursor=self.db.cursor()
        with open(self.filename,'r') as fd:
            for line in fd.readlines():
                (datestamp,text)=self.parse_logline(line)
                if not datestamp: continue
                if self.store_zone(cursor,datestamp,text): continue
                if self.store_looted(cursor,datestamp,text): continue
                if self.store_comms(cursor,datestamp,text): continue
                if self.store_vendor(cursor,datestamp,text): continue
                if self.store_trade(cursor,datestamp,text): continue
        self.db.commit()

class character:
    def __init__(self,eqdir,name):
        self.eqdir=eqdir
        self.name=name
        self.location=self.get_location()
        self.inventory=self.get_inventory()
        
    def get_logfile(self):
        return f"{self.eqdir}/Logs/eqlog_{self.name}_P1999Green.txt"
    def get_invfile(self):
        return f"{self.eqdir}/{self.name}-Inventory.txt"

    def get_inventory(self):
        rows = []
        with open(self.get_invfile(),'r') as fd:
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
        return pandas.DataFrame(rows)

    def upload_to_google(self,sheet_id):
        if self.inventory is None:
            raise("No inventory found")
        write_to_gsheet("auth.json",sheet_id,character,self.inventory)

    def get_location(self):
        file_size=os.stat(self.get_logfile()).st_size
        with open(self.get_logfile()) as fd:
            lines=[]
            iter=1
            location=None
            buffer=8000
            while True:
                fd.seek(file_size-buffer*iter)
                lines.extend(fd.readlines())

                for line in lines:
                    if "You have entered" in line:
                        location=line.split("You have entered ")[-1]
                        return location
                if fd.tell() == 0: continue
                iter+=1
        return "Unknown"
                
        

def get_chars(eqdir):
    # Search {eqdir} for Inventory files
    # Search {eqdir}/Logs for log files
    # Search {eqdir} for .ini files

    characters=[]
    inv_files = glob.glob(f"{eqdir}/*-Inventory.txt")
    for file in inv_files:
        print(file)
        m=re.match("^.*/([^-]+)-Inventory.txt$",file)
        if m:
            char=m.group(1)
            print(f"match {char}")
            if char not in characters:
                characters+=[char]
    log_files = glob.glob(f"{eqdir}/Logs/eqlog_*P1999*")
    ini_files = glob.glob(f"{eqdir}/*P1999Green.ini")
    return characters

def parse_research(input):
    research={}
    for line in input.split("\n"):
        if not line: continue
        fields=line.split("\t")
        
        (level,name,trivial,location)=fields[0:4]
        components=fields[4:]
        if location == 'No': location='Research'
        print(name,components)
        research[name]={
            'level': level,
            'trivial': trivial,
            'location': location,
            'components': components
            }
    return research



necro_research="""
16	Banshee Aura	21	Kun	Words of Derivation	Words of Eradication
16	Hungry Earth	21	No	Words of Materials	Words of Spirit
16	Restless Bones	21	Cla	Words of Reviviscence	Words of the Sentient (Azia)
16	Feign Death	26	Cla	Words of Imitation	Words of Resolution (?)	Thinking this cannot be researched.
20	Harmshield	41	No	Words of Refuge	Words of Absorption
20	Identify	41	Cla	Words of Enlightenment	Words of Anthology
20	Shadow Vortex	41	Cla	Words of Imitation	Words of Dissolution
20	Animate Dead	41	Cla	Words of the Extinct	Words of the Quickening
20	Word of Shadow	41	Cla	Words of Cazic-Thule	Words of Radiance
24	Shadow Sight	62	Cla	Words of Discernment	Words of Eventide
24	Intensify Death	62	No (Quest)	Words of the Sentient (Beza)	Words of Recluse	Words of Absorption
24	Breath of the Dead	62	Cla	Words of Cloudburst	Words of Mistbreath	Words of Cazic-Thule
24	Haunting Corpse	62	No	Words of Possession	Words of Detachment	Words of Allure
29	Summon Dead	87	Cla	Words of Possession	Words of Haunting	Words of Rupturing
29	Renew Bones	93+	No	Words of Purification	Words of the Incorporeal	Words of Acquisition (Azia)
29	Vampiric Curse	95	Kun	Words of Possession	Words of Dissemination	Words of Parasitism
34	Invoke Fear	120+	Cla	Words of Duration	Words of Quivering	Words of Resolve
34	Call of Bones	120	No	Words of Motion	Words of Neglect	Words of Endurance
34	Surge of Enfeeblement	122	No	Words of Abatement	Words of Cazic-Thule	Words of Efficacy
34	Invoke Shadow	122	No	Words of Dark Paths	Words of Haunting	Words of the Suffering
39	Nullify Magic	142	Cla	Words of Descrying	Words of Seizure	Words of Dissolution
39	Word of Souls	142	Cla	Words of Projection	Words of Cazic-Thule	Words of the Spectre
39	Malignant Dead	142	Kun	Words of Bidding	Words of the Suffering	Words of Collection (Beza)
44	Dead Man Floating	162	No	Words of the Psyche	Words of Burnishing
44	Cackling Bones	162	Kun	Words of Obligation	Words of Collection (Caza)
49	Invoke Death	184	No	Words of Requisition	Words of Acquisition (Beza)
49	Lich	184	No	Words of the Ethereal
49	Paralyzing Earth	184	Kun	Words of Crippling Force
49	Bond of Death	184	No	Words of Grappling	Words of Odus
"""
mage_research="""
16	Summon Heatstone	21	True	Words of the Element	Elemental Armor	Bloodstone
16	Minor Summoning: Air	22	True	Words of Tyranny	Elemental: Air	Aviak Feather
16	Minor Summoning: Earth	22	True	Words of Tyranny	Elemental: Earth	Small Brick of Ore
16	Minor Summoning: Fire	22	True	Words of Tyranny	Elemental: Fire	Halas Heater
16	Minor Summoning: Water	22	True	Words of Tyranny	Elemental: Water	Shark Skin
20	Lesser Summoning: Air	41	True	Words of Dominion	Minor Summoning: Air	Pearl Shard
20	Lesser Summoning: Earth	41	True	Words of Dominion	Minor Summoning: Earth	Topaz
20	Lesser Summoning: Fire	41	True	Words of Dominion	Minor Summoning: Fire	Jade Shard
20	Lesser Summoning: Water	41	True	Words of Dominion	Minor Summoning: Water	Ice of Velious
24	Cornucopia	62	False	Words of Transcendence	Summon Food	Loaf of Bread
24	Everfount	62	False	Words of Transcendence	Summon Drink	Water Flask
24	Summoning: Air	62	False	Words of Dimension	Lesser Summoning: Air	Pearl Shard
24	Summoning: Earth	62	True	Words of Dimension	Lesser Summoning: Earth	Glove of Rallos Zek
24	Summoning: Fire	62	False	Words of Dimension	Lesser Summoning: Fire	Jade Shard
24	Summoning: Water	62	False	Words of Dimension	Lesser Summoning: Water	Ice of Velious
29	Summon Coldstone	82	True	Words of Sight	Summon Heatstone	Eye of Serilis
29	Greater Summoning: Air	82	True	Words of Coercion	Summoning: Air	The Scent of Marr
29	Greater Summoning: Earth	82	False	Words of Coercion	Summoning: Earth	Glove of Rallos Zek
29	Greater Summoning: Fire	82	True	Words of Coercion	Summoning: Fire	Breath of Solusek
29	Greater Summoning: Water	82	False	Words of Coercion	Summoning: Water	Flame of Vox
34	Nullify Magic	122	True	Words of Detention	Cancel Magic	Blood of Velious
34	Minor Conjuration: Air	122	False	Words of Duress	Greater Summoning: Air	The Scent of Marr
34	Minor Conjuration: Fire	122	False	Words of Duress	Greater Summoning: Fire	Breath of Solusek
39	Dagger of Symbols	142	True	Words of Collection (Azia)		Dagger
39	Summon Ring of Flight	142	True	Words of Collection (Azia)		Star Rose Quartz
39	Lesser Conjuration: Earth	142	False	Words of Convocation	Minor Conjuration: Earth	Glove of Rallos Zek
39	Lesser Conjuration: Water	142	False	Words of Convocation	Minor Conjuration: Water	Flame of Vox
44	Conjuration: Air	162	False	Words of Incarceration	Lesser Conjuration: Air	The Scent of Marr
44	Conjuration: Earth	162	False	Words of Incarceration	Lesser Conjuration: Earth	Essence of Rathe
44	Conjuration: Water	162	False	Words of Incarceration	Lesser Conjuration: Water	Tears of Prexus
44	Conjuration: Fire	162	True	Words of Incarceration	Lesser Conjuration: Fire	Breath of Ro
49	Greater Conjuration: Air	182	False	Words of Bondage	Conjuration: Air	Wing of Xegony
49	Greater Conjuration: Fire	182	False	Words of Bondage	Conjuration: Fire	Breath of Ro
49	Greater Conjuration: Water	182	False	Words of Bondage	Conjuration: Water	Tears of Prexus
49	Greater Conjuration: Earth	182	True	Words of Bondage	Conjuration: Earth	Essence of Rathe
"""
enchanter_research="""
16	Levitate	22	Yes	Part of Tasarin's Grimoire Pg. 23 (Left)	Part of Tasarin's Grimoire Pg. 23 (Right)
16	Disempower	22	Yes	Part of Tasarin's Grimoire Pg. 24 (Left)	Part of Tasarin's Grimoire Pg. 24 (Right)
16	Mesmerization	22	No	Part of Tasarin's Grimoire Pg. 26 (Left)	Part of Tasarin's Grimoire Pg. 26 (Right)
20	Berserker Strength	42	No	Part of Tasarin's Grimoire Pg. 30 (Left)	Part of Tasarin's Grimoire Pg. 30 (Right)
20	Color Shift	42	No	Part of Tasarin's Grimoire Pg. 312 (Left)	Part of Tasarin's Grimoire Pg. 312 (Right)
20	Endure Magic	42	Yes	Part of Tasarin's Grimoire Pg. 375 (Left)	Part of Tasarin's Grimoire Pg. 375 (Right)
24	Strip Enchantment	62	No	Part of Tasarin's Grimoire Pg. 390 (Left)	Part of Tasarin's Grimoire Pg. 390 (Right)
24	Tepid Deeds	62	No	Velishoul's Tome Pg. 8	Velishoul's Tome Pg. 9
24	Invigor	62	Yes	Velishoul's Tome Pg. 16 (Faded)	Velishoul's Tome Pg. 17
29	Ultravision	95	Yes	Velishoul's Tome Pg. 43	Velishoul's Tome Pg. 44
29	Nullify Magic	95	Yes	Velishoul's Tome Pg. 67	Velishoul's Tome Pg. 68
29	Enstill	95	Yes	Velishoul's Tome Pg. 75	Velishoul's Tome Pg. 76
29	Feedback	95	No	Velishoul's Tome Pg. 108 (Faded)	Velishoul's Tome Pg. 109
34	Insipid Weakness	122	No	Salil's Writ Pg. 60 (Left)	Salil's Writ Pg. 60 (Right)
34	Radiant Visage	122	No	Salil's Writ Pg. 64 (Left) (Faded)	Salil's Writ Pg. 64 (Right)
34	Mana Sieve	122	No	Salil's Writ Pg. 90 (Left)	Salil's Writ Pg. 90 (Right) (Faded)
39	Resist Magic	142	Yes	Salil's Writ Pg. 153 (Left) (Faded)	Salil's Writ Pg. 153 (Right)
39	Gravity Flux	142	No	Salil's Writ Pg. 174 (Left)	Salil's Writ Pg. 174 (Right)
39	Immobilize	142	Yes	Salil's Writ Pg. 282 (Left)	Salil's Writ Pg. 282 (Right) (Faded)
39	Mind Wipe	142	No	Salil's Writ Pg. 288 (Left)	Salil's Writ Pg. 288 (Right) (Faded)
44	Pillage Enchantment	162	No	Nilitim's Grimoire Pg. 35	Nilitim's Grimoire Pg. 36
44	Color Skew	162	No	Nilitim's Grimoire Pg. 115	Nilitim's Grimoire Pg. 116
44	Shiftless Deeds	162	No	Nilitim's Grimoire Pg. 300	Nilitim's Grimoire Pg. 301
44	Extinguish Fatigue	162	Yes	Nilitim's Grimoire Pg. 351	Nilitim's Grimoire Pg. 352
49	Allure	182	No	Nilitim's Grimoire Pg. 378	Nilitim's Grimoire Pg. 379
49	Paralyzing Earth	182	Kun	Nilitim's Grimoire Pg. 400	Nilitim's Grimoire Pg. 401
49	Blanket of Forgetfulness	182	No	Nilitim's Grimoire Pg. 415	Nilitim's Grimoire Pg. 416
49	Reoccurring Amnesia	182	No	Nilitim's Grimoire Pg. 449	Nilitim's Grimoire Pg. 450
"""


if __name__=="__main__":

    if os.path.isfile(f"db.conf"):
        with open(f"db.conf",'r') as fd:
            config=toml.load(fd)
            print(config)
    else:
        print("database file missing")
        sys.exit(1)

    db=psycopg.connect(f"host={config['host']} dbname={config['database']} user={config['user']} password='{config['password']}' port={config['port']}")

    albeddo=logfile("Everquest/Logs/eqlog_Albeddo_P1999Green.txt",db)
        
    eqdir=os.getenv('EQDIR')
    char_names=get_chars(eqdir)
    print(f"Characters:\n{char_names}")
    char_log={}
    for char in char_names:
        char_log[char]=logfile(f"{eqdir}/Logs/eqlog_{char}_P1999Green.txt",db)
    #print(chars)
    #    print(parse_research(necro_research))
    #    print(parse_research(mage_research))


