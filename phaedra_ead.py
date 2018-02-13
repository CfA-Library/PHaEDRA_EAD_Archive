# coding: utf-8

import os
import json
import shutil
import rdflib
import unicodedata
import pandas as pd
from datetime import datetime

print "Reading the tsv file...this may take a few seconds."

timestamp = datetime.now().strftime("%Y_%m%d_%H%M")

#brute foce method of generating an EAD file...its not pretty but it works

"""

certainty inferred

phaedra0009. Box 1, Transit Circle
Date: 1851-04-03 to 1851-07-13
KG Number KG11365.9.
Sequence volume A9. 



KG11365.9. Box 1, Transit Circle
Date: 1851-04-03 to 1851-07-13
Additional identifier Also identified as: A9. 


"""


tsv = "phaedra2.tsv"


phaedra1  = open(tsv, "r")

header  = open("PHaEDRA_EAD_header.txt", "r")

phaedra2 = open("PHaEDRA_EAD_"+timestamp+".xml","w")


for linex in header:
    phaedra2.write(linex)

phaedra2.write("\n")


#print phaedra1

for line in phaedra1:
    data =  line.split("\t")
    unitid=data[0].strip()
    kgnum=data[1].strip()
    altid=data[2].strip()
    unittitle=data[3].strip()
    yearstart=data[4].strip()
    monthstart=data[5].strip()
    daystart=data[6].strip()
    yearend=data[7].strip()
    monthend=data[8].strip()
    dayend=data[9].strip()
    boxnum=data[10].strip()
    author1= data[11].strip()
    author2=data[12].strip()
    notes=data[13].strip("\n").strip()
    datecert=data[14].strip()
   
    ead = "<c level='item'><did><unitid>"+unitid+"</unitid><unittitle>"+unittitle.replace('&','&amp;')+"</unittitle>"

    #if datecert!="":
    #    ead += "<unitdate calendar='gregorian' certainty='"+datecert+"' era='ce' normal='"
    #else:
    #    ead += "<unitdate calendar='gregorian' era='ce' normal='"
    if yearstart != "":
        ead += "<unitdate calendar='gregorian' era='ce' normal='"+yearstart
        if monthstart != "":
            ead += "-"+monthstart.zfill(2)
            if daystart != "":
                ead += "-"+daystart.zfill(2)
        if yearend != "":
            ead += "/"+yearend
            if monthend != "":
                ead += "-"+monthend.zfill(2)
                if dayend != "":
                    ead += "-"+dayend.zfill(2)
        else:
            ead+= "/"+yearstart
            if monthstart != "":
                ead += "-"+monthstart.zfill(2)
                if daystart != "":
                    ead += "-"+daystart.zfill(2)
        if datecert!="":
            ead += "' certainty='"+datecert+"'>"
        else:
            ead += "'>"

    else:
        if yearend !="":
            ead += "<unitdate calendar='gregorian' era='ce' normal='"+yearend
            if monthend != "":
                ead += "-"+monthend.zfill(2)
                if dayend != "":
                    ead += "-"+dayend.zfill(2)
            ead +="'>"


    if yearstart != "":
        ead += yearstart
        if monthstart != "":
            ead += "-"+monthstart.zfill(2)
            if daystart != "":
                ead += "-"+daystart.zfill(2)
        if yearend != "":
            ead += "/"+yearend
            if monthend != "":
                ead += "-"+monthend.zfill(2)
                if dayend != "":
                    ead += "-"+dayend.zfill(2)
        ead += "</unitdate>"

    else:
        if yearend !="":
            ead += yearend
            if monthend != "":
                ead += "-"+monthend.zfill(2)
                if dayend != "":
                    ead += "-"+dayend.zfill(2)
            ead += "</unitdate>"

    if boxnum != "":
        ead += "<container type='Box' label='Unspecified'>"+boxnum+"</container>"

    ead += "</did>"

    if kgnum != "":
        ead += "<odd><head>KG Number</head><p>"+kgnum+".</p></odd>"

    if altid != "":
        ead += "<odd><head>Sequence volume</head><p>"+altid+".</p></odd>"

    if author1 !="":
        ead += "<odd><head>Author/s</head><p>"+author1
        if author2 !="":
                ead += " and "+author2
        ead += ".</p></odd>"

    if notes != "":
        ead += "<odd><p>"+notes+".</p></odd>"

    ead +="</c>\n"
    print ead  

    phaedra2.write(ead)


phaedra2.write("        </dsc>\n    </archdesc>\n</ead>")

phaedra2.close()