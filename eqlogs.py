#!/usr/bin/python3
# library routines for reading eq logs
import os
import sys
import glob
import re

class character:
    def init(self,eqdir,name):
        self.filename=logfile
        self.eqdir=eqdir
        self.name=name
        self.location=get_location()
        self.inventory=get_inventory()

    def get_inventory():
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

    def upload_to_google(sheet_id):
        if self.inventory is None:
            raise("No inventory found")
        write_to_gsheet("auth.json",sheet_id,character,self.inventory)

    def get_location():
        file_size=os.stat(self.filename).st_size
        with open(self.filename) as fd:
            lines=[]
            iter=1
            done=False
            buffer=8000
            while True:
                fd.seek(file_size-buffer*iter)
                lines.extend(fd.readlines())

                for line in lines:
                    if "You have entered" in line:
                        self.location=line.split("You have entered ")[-1]
                        done=True
                if done or f.tell() == 0: dontinue
        

def get_chars(eqdir):
    # Search {eqdir} for Inventory files
    # Search {eqdir}/Logs for log files
    # Search {eqdir} for .ini files

    characters=[]
    inv_files = glob.glob(f"{eqdir}/*-Inventory.txt")
    for file in inv_files:
        m=re.match("^.*/([^-]+)-Inventory.txt$",file)
        if m:
            char=m.group(0)
            if char not in characters:
                characters+=[char]
    log_files = glob.glob(f"{eqdir}/Logs/eqlog_*P1999*")
    ini_files = glob.glob(f"{eqdir}/*P1999Green.ini")

def parse_research(input):
    research={}
    for line in input.split("\n"):
        if not line: continue
        print(f"x{line}y")
        fields=line.split("\t")
        print(fields)
        
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
    print(f"Characters:\n{get_chars(os.getenv('EQDIR'))}")

    print(parse_research(necro_research))
