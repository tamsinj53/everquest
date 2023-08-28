# library routines for reading eq logs

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
        with fd=open(self.filename):
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
        
