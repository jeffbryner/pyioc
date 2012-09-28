#!/usr/bin/python
import sys
import lxml.objectify

ioco=lxml.objectify.parse(sys.argv[1])
root=ioco.getroot()
print("%s: %s"%(root.short_description, root.description))
for ii in root.findall("//*[local-name()='IndicatorItem']"):
       print('\t%s\t%s\t%s'%(ii.getparent().attrib.get("operator"), ii.Context.attrib.get("search"),ii.Content))