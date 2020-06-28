import requests
import json
import time
import xml.etree.ElementTree
import glob
import urllib.parse
import CC3DICT	 
import sys
import os
import re
from lxml import etree

def getPlaceid(queryString, apiKey):    
    endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + queryString + "&inputtype=textquery&fields=place_id&key="+apiKey
    #print(endpoint_url)
    
    res = requests.get(endpoint_url)
    data =  json.loads(res.content)
    #print(data)
    
    if data['status']=="OK":
        placeId =data['candidates'][0]['place_id']
    else:
        placeId ="notfound"
    return(placeId)

def address_components(place_id, apiKey):
    epUrl = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place_id + "&fields=name,address_component&key=" + apiKey + "&types=establishment"
    res = requests.get(epUrl)
    data =  json.loads(res.content)
    return(data)

def main(queryString):
    #log.write("\nmain sub")
    f = open("./lib/apikey", "r")
    key = f.readline()
    f.close()
    returnString=''
    pId=getPlaceid(queryString, key.rstrip())
    log.write("\n\nGot Place ID: " + pId)
    #print(pId)
    if pId != "notfound":
        cData=address_components(pId, key.rstrip())
        for (k, v) in cData.items():
            if k == "result":
                for (k, v) in v.items():
                    if k=="address_components":
                        rdata=[]
                        rdata=v
                        for key in rdata:
                            #if(key['types'][0]) == 'locality':
                                #print('City: ' + key['long_name'])
                                #print('City: ' + key['short_name'])
                                #returnString= key['long_name']
                            #if(key['types'][0]) == 'postal_town':
                                #print('City: ' + key['long_name'])
                                #print('City: ' + key['short_name'])
                                #returnString= key['long_name']
                            #if(key['types'][0]) == 'administrative_area_level_1':
                                #print('State: ' + key['long_name'])
                                ##print('State: ' + key['short_name'])
                            try:
                                if(key['types'][0]) == 'country':
                                    #print('Country: ' + key['long_name'])
                                    #print('Countryy: ' + key['short_name'])
                                    returnString= key['short_name']
                            except:
                                    pass
    else:
        log.write("\nPlace ID not found")
        print("################### place id not found #####################")
    #log.write("\nGet country code: " + returnString)
    return(returnString)
 
def ppxml(xml):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml, parser)
    tree.write(xml, encoding='utf-8', pretty_print=True, xml_declaration=True)
 
    
if __name__=="__main__":
    
    xmlInPath=''
    
    if len(sys.argv) <= 1:
        print("\nPlease provide XML path...")
        print("\n>>python innopd.py ./xml/file/path") 
        exit(0)
    
    xmlInPath = sys.argv[1]
    
    # Check if path exits
    if not os.path.exists(xmlInPath):
        print("\nPath " + str(sys.argv[1]) + " does not exist in your file system...")
        exit(0)
    
    try:
        if xmlInPath.index("/") > 0:
            if xmlInPath[-1:] != "/":
                xmlInPath=xmlInPath + '/'
                
    except:
        pass
        
    try:
        if xmlInPath.index("\\") > 0:
            if xmlInPath[-1:] != "\\":
                xmlInPath=xmlInPath + "\\"                
    except:
        pass
    

    print("importing CC3 country code library...")
    
    counter=0
    log = open(xmlInPath + "log.txt", "w", encoding='utf-8')
    log.write("Google Map API Hit: Place Detal API")
    log.write("\n-----------------------------------------------------------------")
    #Open original file
    
    for filepath in glob.iglob(xmlInPath + '*.xml'):
        counter=counter+1
        log.write('\n\n\n' + str(counter) + '     Processing ' + filepath)
        print(str(counter) + '      Processing ' + filepath)
        xml.etree.ElementTree.register_namespace('', 'http://www.elsevier.com/xml/ani/ani')
        xml.etree.ElementTree.register_namespace('ce', 'http://www.elsevier.com/xml/ani/common')
        
        et = xml.etree.ElementTree.parse(filepath)
        
        
        for description in et.iter('{http://www.elsevier.com/xml/ani/ani}affiliation'):
            cntFound='false'
            for cntry in description.findall('{http://www.elsevier.com/xml/ani/ani}country'):
                cntFound='true'
                #if cntry.attrib:
                #    if len(cntry.attrib['iso-code']) > 3  or len(cntry.attrib['iso-code']) < 3:
                #        print('##################################################### FOUND')
                #        print(cntry.attrib['iso-code'])
                        #cntFound='false'
                        #description.remove(cntry)
                    
                if cntry.attrib:
                    if bool(re.match('^[A-Z][A-Z][A-Z]$', cntry.attrib['iso-code'])):
                        cntFound='true'
                    else:
                        cntFound='false'
                        description.remove(cntry)
                else:
                    cntFound='false'
                    description.remove(cntry)               
                
                
            if description.find('{http://www.elsevier.com/xml/ani/common}source-text').text == None:
                print("Source-text is missing...." )
                log.write("\nSource-text is missing....")
            else:
                #if description.find('country') == None:
                if cntFound == 'false':
                    queryString=description.find('{http://www.elsevier.com/xml/ani/common}source-text').text
                    queryString=queryString.replace("&amp;", "and")
                    queryString=queryString.replace(" & ", " and ")
                    cntr= str(main(queryString))
                    
                    if len(cntr) > 1:
                        newElement = xml.etree.ElementTree.Element('country')
                        newElement.attrib['iso-code'] = CC3DICT.thisdict[cntr]   #cntr
                        description.insert(-1, newElement)
                    
                    log.write("\nQuery: " + str(queryString))
                    log.write("\nCountry Code: " + str(cntr))
                    cntr=''
                    queryString=''  
                else:
                    log.write('\nQuery: ' + description.find('{http://www.elsevier.com/xml/ani/common}source-text').text)
                    log.write("\nCountry present")
                    cntFound='false'
        
					
        et.write(filepath)
        ppxml(filepath)
    log.close()

    
    