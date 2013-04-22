#!/usr/bin/python
import sys
from lxml import etree
'''
2013 Jeff Bryner
semi-ugly, semi-hard-coded method of getting the juicy bits of a STIX.xml file for IOC processing
Tested against: 
    http://stix.mitre.org/language/version1.0/stix_v1.0_samples_20130408.zip
    and samples from NESCO
'''

stixtree=etree.parse(sys.argv[1])
root=stixtree.getroot()

for indicator in root.xpath("//*[local-name()='STIX_Package']"):
    for it in indicator.xpath(".//*[local-name()='Text_Title']"):
        print(it.text.encode('ascii','ignore'))
    for it in indicator.xpath(".//*[local-name()='Title']"):
        print(it.text.encode('ascii','ignore'))

    for v in indicator.xpath(".//*[contains(local-name(),'Value')]"):
        if 'URIObj' in root.nsmap.keys() and root.nsmap['URIObj'] in v.tag:
            print('\t{0}:{1}'.format(v.getparent().attrib["type"],v.text.encode('ascii','ignore')))
        if 'URIObject' in root.nsmap.keys() and root.nsmap['URIObject'] in v.tag: 
            print('\t{0}:{1}'.format(v.getparent().attrib["{" + root.nsmap['xsi']+"}type"],v.text.encode('ascii','ignore')))
        #if 'AddrObj' in root.nsmap.keys() and root.nsmap['AddrObj'] in v.tag:
        if 'Addr' in v.tag:
            print('\t{0}:{1}'.format(v.getparent().attrib["category"],v.text.encode('ascii','ignore')))
        if 'Simple_Hash_Value' in v.tag:
            print('\t{0}:{1}'.format(v.getparent().getchildren()[0].text.encode('ascii','ignore'),v.text.encode('ascii','ignore')))
    #snort rules
    for v in indicator.xpath(".//*[contains(local-name(),'Rule')]"):
        if 'testMechSnort' in root.nsmap.keys() and root.nsmap['testMechSnort'] in v.tag:
            print('\t{0}'.format(v.getparent().getparent().getparent().getchildren()[1].text))
            print('\t{0}'.format(v.text))

    #malware sample
    for v in indicator.xpath(".//*[contains(local-name(),'Raw_Artifact')]"):
        print('\t{0}:{1}'.format(v.getparent().getchildren()[0].getchildren()[0].attrib['algorithm'],v.text[0:60]))