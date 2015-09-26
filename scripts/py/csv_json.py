# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 18:21:20 2015

@author: gmf
"""

# convert csv to json (dataTables likes this JSON format)
import csv
import json
csvfile = open('scorelines_00213.csv', 'r')
fieldnames = tuple(csvfile.readline().strip().split(",")) # get field names
reader = csv.reader( csvfile )
out = "{\n\t\"data\": [\n\t\t" + ",\n\t\t".join([json.dumps(row) for row in reader]) + "\n\t]\n}\n"
jsonfile = open('test2.json', 'w')
jsonfile.write(out)
jsonfile.close()