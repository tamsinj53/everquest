#!/usr/bin/python

import os
import re

DEBUG=True

# [Tue Apr 11 21:04:43 2023] Merchant Yisasan tells you, 'I'll give you 2 gold 4 silver 7 copper per Warbone Chips'
# [Sat Apr 15 23:18:41 2023] Handaaf Orcslicer tells you, 'I'll give you 7 gold 4 silver 6 copper for the Raw-hide Skullcap.'
# line miss: [Thu Mar 23 21:52:24 2023] Merchant Uaylain tells you, 'I'll give you 1 silver 4 copper per Bone Chips'
def parse_price(price):
    copper=0
    pm=re.search("([0-9]+) platinum",price)
    if pm: copper+=int(pm.group(1))*1000
    pg=re.search("([0-9]+) gold",price)
    if pg: copper+=int(pg.group(1))*100
    ps=re.search("([0-9]+) silver",price)
    if ps: copper+=int(ps.group(1))*10
    pc=re.search("([0-9]+) copper",price)
    if pc: copper+=int(pc.group(1))
    return copper

def print_price(copper):
    plat=int(copper/ 1000)
    copper-=plat*1000
    gold=int(copper /100)
    copper-=gold*100
    silver=int(copper /10)
    copper-=silver*10
    return f"{plat}p {gold}g {silver}s {copper}c"

vendor_price={}
item_price={}
item_line={}

for file in os.listdir("Logs"):
    if file.startswith('eqlog'):
        print(file)
        with open(f"Logs/{file}") as fd:
            lines=fd.readlines()
            print(f"{len(lines)} lines")
            for line in lines:
                # print(line)
                m=re.match("\[[^\]]+\] (.+) tells you, 'I'll give you (.+) per (.+)\.*'$",line)
                if not m:
                    m=re.match("\[[^\]]+\] (.+) tells you, 'I'll give you (.+) for the (.+)\.*'$",line)
                if m:
                    vendor=m.group(1)
                    price=m.group(2)
                    item=m.group(3)
                    copper=parse_price(price)
                    # print(f"{vendor=} {item=} {price=} {copper=}")
                    vendor_price[item]=copper
                    if item not in item_price:
                        print(f"Seen new {item}")
                        item_price[item]=copper
                    else:
                        if item_price[item]<copper:
                            print(f"Seen better price {item}")
                            item_price[item]=copper

                    item_line[item]=lines
                    if DEBUG: print(f"line hit : {line}")
                else:
                    if DEBUG: print(f"line miss: {line}")
                m=re.match("\[[^\]]+\] (.+) tells you, 'That'll be (.+) for the (.+)\.'$",line)
                if m:
                    vendor=m.group(1)
                    price=m.group(2)
                    item=m.group(3)
                    copper=parse_price(price)
                    if item in item_price:
                        sell=item_price[item]
                    else:
                        sell=0
                    print(f"Sell/buy loss {item} - {print_price(copper-sell)}")
with open("prices.cfg",'w') as fd:
    for item, price in item_price.items():
        print(f"{item}\t{price}",file=fd)
