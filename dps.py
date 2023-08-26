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


class damager:
    active = {}
    now = datetime.datetime.now()
    debug = False
    stdscr = None
    count=0
    looted=""
    looted_price=""

    def tick(time_stamp):
        self = damager
        self.now = time_stamp
        self.tidy()
        for name, instance in self.active.items():
            instance.accounting()
        self.count+=1
        self.display()

    def display():
        self = damager
        if self.stdscr:
            self.stdscr.clear()
            self.stdscr.addstr(0,0,"Name                dps      hpm")
        else:
            print("====")
        index=0
        #print(self.active)
        sort_map={k:v for k,v in sorted(self.active.items(), key=lambda item:item[1].dps, reverse=True)}
        #print (sort_map)
        for name, instance in sort_map.items():
            index+=1
            if self.stdscr:
                self.stdscr.addstr(
                    index,
                    0,
                    instance.name)
                self.stdscr.addstr(index,20,f"{instance.dps:.2f}")
                self.stdscr.addstr(index,30,f"{instance.hpm}")

                self.stdscr.addstr(curses.LINES-1,0,f"Loot: {self.looted} {self.looted_price}")                    
                self.stdscr.refresh()
            else:
                print(
                    f"{index}: {instance.name} - {instance.dps:.2f} dps {instance.hpm} hits/min"
                )

    def tidy():
        self = damager
        now = self.now
        if self.debug:
            print(f"tidying at {now}")
        cut_off = now - datetime.timedelta(minutes=10)
        if self.debug:
            print(f"cut off {cut_off}")
        to_remove = []
        for name, instance in damager.active.items():
            instance.hits=[(h,t) for (h,t) in instance.hits if t>cut_off]
            if instance.now < cut_off:
                if self.debug:
                    print(f"under cut off {instance.now}")
                to_remove += [name]
        for name in to_remove:
            if self.debug:
                print(f"removing {name}")
            del self.active[name]

    def hit(source, target, amount, time_stamp):
        self = damager
        self.tick(time_stamp)
        if source in damager.active:
            self.active[source].do_hit(target, amount, time_stamp)
            return

        self.active[source] = damager(source)
        if self.debug:
            print(f"adding {source}")

    def __init__(self, name):
        self.name = name
        self.dmg_out = 0
        self.dmg_in = 0
        self.now = damager.now
        self.hits = []
        self.dps = 0
        self.hpm = 0

    def do_hit(self, target, amount, time_stamp):
        try:
            amount = int(amount)
        except:
            print(f"{amount=}")
            raise
        self.dmg_out += amount
        # [Mon Mar 27 16:09:32 2023]
        self.now = time_stamp
        self.hits += [(amount, time_stamp)]
        self.accounting()
        # print(f"{self.name} - {self.dps:.2f} dps {len(self.hits)} hits/min")

    def accounting(self):
        window = self.now - datetime.timedelta(seconds=60)

        hits = [hit for hit in self.hits if hit[1] > window]
        if len(hits) > 2:
            first=self.now
            for (hit,hit_time) in hits:
                if hit_time < first:
                    first=hit_time
            total = sum([hit[0] for hit in hits])
            timeframe = self.now-first
            self.timeframe=timeframe.seconds
            if timeframe.seconds>0:
                dps = total/timeframe.seconds
            else:
                dps=0
        else:
            self.timeframe=0
            dps=0
        self.dps = dps
        self.hpm = len(hits)
        if self.dps>10:
            print("***")
            print(f"{self.name} anomaly")
            print(self.hits)
            print(hits)

    def hit_by(self, agressor, amount):
        self.dmg_in += amount

    def __str__(self):
        return self.name



def main(stdscr=None):
    prices={}
    with open("prices.cfg",'r') as fd:
        for line in fd.readlines():
            line=line.rstrip()
            (item,price)=line.split("\t")
            prices[item]=int(price)

    damager.stdscr = stdscr
    if len(sys.argv) > 1:
        logfile_name = sys.argv[1]
        logfile_search = False
    else:
        logfile_name = latest_file("/mnt/h/Games/Everquest/Logs")
        logfile_search = True
    damager.count=0
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
            line = line.strip()
            # print(line)
            p=re.match(".*You have looted a (.+)\.--",line)
            if not p:
                p=re.match(".*has looted a (.+)\.--",line)
            if p:
                item = p.group(1)
                if item in prices:
                    # print(f"{item} {print_price(prices[item])}")
                    damager.looted=item
                    damager.looted_price=print_price(prices[item])
                else:
                    damager.looted=item
                    damager.looted_price="Unknown"

            match = re.match(
                "\[(.*)\] (You) (backstab|punch|bash|strike|crush|pierce|kick|hit|slash) (.+) for ([0-9]+) points of damage",
                line,
            )
            if not match:
                match = re.match(
                    "\[(.*)\] (.+) (backstabs|punches|strikes|bashes|crushes|pierces|kicks|hits|slashes) (.+) for ([0-9]+) points of damage",
                    line,
                )
            if not match:
                match = re.match(
                    "\[(.*)\] ([^ ]+) (Scores a critical) (hit!)\(([0-9]+)\)", line
                )
            if not match:
                match = re.match(
                    "\[(.*)\] ([^ ]+) (Lands a Crippling) (Blow!)\(([0-9]+)\)", line
                )
            # if not match:
            #     match = re.match("\[(.*)\] (.+) (for ([0-9]+) points of damage",line)
            #     print(f"Unmatched: {line}")
            # [Wed Apr 05 20:25:11 2023] Fallalot crushes a ghoul for 18 points of damage.
            # [Wed Apr 05 20:34:01 2023] a barbed bone skeleton was hit by non-melee for 1 points of damage.
            if match:
                try:
                    time_string = match.group(1)
                    source = match.group(2)
                    dmg_type = match.group(3)
                    target = match.group(4)
                    amount = match.group(5)
                except:
                    print(line)
                    print(match.group(1))
                    print(match.group(2))
                    print(match.group(3))
                    print(match.group(4))
                    raise
                time_stamp = datetime.datetime.strptime(
                    time_string, "%a %b %d %H:%M:%S %Y"
                )
                damager.hit(source, time_stamp=time_stamp, target=target, amount=amount)
                damager.tick(time_stamp)
                # print(line)
            damager.tidy()
            # display(stdscr, players)
        return

if __name__ == "__main__":
    # main()
    curses.wrapper(main)
