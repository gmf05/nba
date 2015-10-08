# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 10:16:11 2015

@author: gmf
"""

#####
# moving around lines in csv scoreline data
# since placement was switched in between making lists
import re
delim = ","
# delete lines from scores_00214.csv
fr = open("scorelines_00213.csv","r")
#fr = open("scorelines_00214.csv","r")
fw = open("temp.csv","w")
newln = 5 # 
oldln = 25
#while True:    
for r in fr.readlines():
    #r = fr.readline()
    r = r.split(delim)
    if re.match("20150326", r[0]):
        break
    ln = r[-1].strip()
    for i in range(oldln,newln,-1):
        r[i] = r[i-1].strip().replace("\xc2\xa0","")
    r[newln] = ln
    fw.write(delim.join(r) + "\n")

# for first game on 20150326 currently at pointer, write to list
#fw.write(delim.join(r) + "\n")

#for r in fr.readlines():
#    fw.write(r)

fw.close()
