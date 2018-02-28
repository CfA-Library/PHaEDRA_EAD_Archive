# coding: utf-8
import MySQLdb
from datetime import datetime

timestamp = datetime.now().strftime("%Y_%m%d_%H%M")

#open files
connection = open("db_connection.txt","r")
header  = open("PHaEDRA_EAD_header.txt", "r")
phaedraXML = open("PHaEDRA_EAD_"+timestamp+".xml","w")

for line in header:
    phaedraXML.write(line)

phaedraXML.write("\n")

#get database connection info
dbaseinfo = []
for line in connection:
    dbaseinfo.append(line)
username = dbaseinfo[0].replace("\n","")
password = dbaseinfo[1].replace("\n","")
dbase = dbaseinfo[2].replace("\n","")

db = MySQLdb.connect(host="mysql.altbibl.io", user=username, passwd=password, db=dbase) 

cur = db.cursor()
cur.execute("SELECT * FROM items")
result = cur.fetchall()

for row in result:

    unitid = row[0]
    unittitle = row[3]
    kgnum = row[1]
    altid = row[2]
    yearstart = row[4]
    monthstart = row[5]
    daystart = row[6]
    yearend = row[7]
    monthend = row[8]
    dayend = row[9]
    boxnum = str(row[10])
    bibcode = row[13]

    #if the item has been digitized, ingest by ADS, and given a bibcode...
    #link out to the ADS record from the item's title
    if bibcode != None:
        ead = "<c level='item'>\n\t<did>\n\t\t<unitid>"+unitid+"</unitid>\n\t\t<unittitle><extref xlink:show='new' xlink:href='http://adsabs.harvard.edu/cgi-bin/nph-data_query?bibcode="+bibcode+"&amp;link_type=ARTICLE'>"+unittitle.replace('&','&amp;')+"</extref></unittitle>"

    #otherwise just include the title in plane text
    else:
        ead = "<c level='item'>\n\t<did>\n\t\t<unitid>"+unitid+"</unitid>\n\t\t<unittitle>"+unittitle.replace('&','&amp;')+"</unittitle>"

    #complicated logic to ascertain the correct format for the date of the item
    if yearstart != None:
        ead += "\n\t\t<unitdate calendar='gregorian' era='ce' normal='"+str(yearstart)
        if monthstart != None:
            ead += "-"+str(monthstart).zfill(2)
            if daystart != None:
                ead += "-"+str(daystart).zfill(2)
        if yearend != None:
            ead += "/"+str(yearend)
            if monthend != None:
                ead += "-"+str(monthend).zfill(2)
                if dayend != None:
                    ead += "-"+str(dayend).zfill(2)
        else:
            ead+= "/"+str(yearstart)
            if monthstart != None:
                ead += "-"+str(monthstart).zfill(2)
                if daystart != None:
                    ead += "-"+str(daystart).zfill(2)
        #if datecert!=None:
        #    ead += "' certainty='"+datecert+"'>"
        #else:
        #    ead += "'>"
        ead += "'>" #comment this out if previous four lines are uncommented
    else:
        if yearend !=None:
            ead += "\n\t\t<unitdate calendar='gregorian' era='ce' normal='"+str(yearend)
            if monthend != None:
                ead += "-"+str(monthend).zfill(2)
                if dayend != None:
                    ead += "-"+str(dayend).zfill(2)
            ead +="'>"

    if yearstart != None:
        ead += str(yearstart)
        if monthstart != None:
            ead += "-"+str(monthstart).zfill(2)
            if daystart != None:
                ead += "-"+str(daystart).zfill(2)
        if yearend != None:
            ead += "/"+str(yearend)
            if monthend != None:
                ead += "-"+str(monthend).zfill(2)
                if dayend != None:
                    ead += "-"+str(dayend).zfill(2)
        ead += "</unitdate>"
    else:
        if yearend !=None:
            ead += str(yearend)
            if monthend != None:
                ead += "-"+str(monthend).zfill(2)
                if dayend != None:
                    ead += "-"+str(dayend).zfill(2)
            ead += "</unitdate>"

    #Box numnber for the item
    if boxnum != None:
        ead += "\n\t\t<container type='Box' label='Unspecified'>"+boxnum+"</container>"

    ead += "\n\t</did>"

    
    cur.execute("SELECT nt.note_type_description, n.note_type_id, n.note FROM notes AS n LEFT JOIN note_types AS nt USING (note_type_id) WHERE n.item_id='"+unitid+"'")
    notes = cur.fetchall()

    #date note
    for note in notes:
        if note[1] == 2:
            ead += "\n\t<odd><head>"+note[0]+":</head><p>"+note[2]+"</p></odd>"

    #if item hsa a KG number...not all do!
    if kgnum != None:
        ead += "\n\t<odd><head>KG Number:</head><p>"+kgnum+"</p></odd>"

    #used to 
    if altid != None:
        ead += "\n\t<odd><head>Sequence volume:</head><p>"+altid+"</p></odd>"

    #authors
    cur.execute("SELECT p.person_name, ip.item_person_position, pt.person_type_full, p.person_last, p.person_given FROM item_persons AS ip LEFT JOIN persons AS p USING (person_id) LEFT JOIN person_types AS pt USING (person_type_id) WHERE item_id='"+unitid+"'")
    people = cur.fetchall()

    roleType = []
    group = {}

    for person in people:
        roleType.append(person[2])

    for role in set(roleType):
        personlist = []
        for person in people:
            if person[2] == role:
                personlist.append(person[0])
        group[role] = personlist

    for i in group:
        if i == "Author":
            otherAuths = []
            mainAuth = None

            if len(group['Author']) > 1:
                for person in people:
                    if person[2] == "Author" and person[1] == 1:
                        mainAuth = [person[0]]
                    elif person[2] == "Author" and person[1] != 1:
                        otherAuths.append(person[0])
            else:
                mainAuth = [group['Author'][0]]

            if otherAuths != []:
                ead += "\n\t<odd><head>Authors:</head><p>"+mainAuth[0]+", "+", ".join(otherAuths)+"</p></odd>"
            else:
                ead += "\n\t<odd><head>Author:</head><p>"+mainAuth[0]+"</p></odd>"
                
        else:
            if len(group[i]) > 1:
                ead += "\n\t<odd><head>"+i+"s:"+"</head><p>"+", ".join(group[i])+"</p></odd>"
            else:
                ead += i+": "+group[i][0]
                ead += "\n\t<odd><head>"+i+":"+"</head><p>"+group[i][0]+"</p></odd>"


    #link out to the ADS record from the item's title
    if bibcode != None:
        ead += "\n\t<odd><head>ADS Record:</head><p><extref xlink:show='new' xlink:href='https://ui.adsabs.harvard.edu/#abs/"+bibcode+"/'>"+bibcode+"</extref></p></odd>"

    #if full text...
    #<odd><head>Full Text Searchable PDF</head><p><extref xlink:show='new' xlink:href='http://adsabs.harvard.edu/cgi-bin/nph-data_query?bibcode=1924phae.proj.1092P&amp;link_type=ARTICLE'>phaedra1092 full text</extref></p></odd> 

    #physical condition notes
    for note in notes:
        if note[1] == 4:
           ead += "\n\t<odd><head>Physical condition:</head><p>"+note[2]+"</p></odd>"
   
    #scope and contents notes
    cnoteList = []
    jList = ""
    for note in notes:
        if note[1] == 1 or note[1] == 3:
            cnoteList.append(note[2])
            jList = "</p><p>".join(cnoteList)
    if jList != "":
        ead += "\n\t<scopecontent><head>Scope and Contents</head><p>"+jList.replace('&','&amp;')+"</p></scopecontent>"

    ead +="\n</c>\n"
    
    print ead #display EAD line to screen, for troubleshooting

    phaedraXML.write(ead)

#close the XML file
phaedraXML.write("\n\n\t\t</dsc>\n\t</archdesc>\n</ead>")
phaedraXML.close()