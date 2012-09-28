#!/usr/bin/python
import sys
import lxml.objectify

global level

def walkIndicatorItems(ind):
    global level
    lastii=ind.findall("./*[local-name()='IndicatorItem']")[-1]
    for i in ind.findall("./*[local-name()='IndicatorItem']"):
        logicOperator=str(i.getparent().attrib.get("operator")).lower()        
        if i == lastii:
            print('\t'*level + i.Context.attrib.get("search") + ' ' + i.attrib.get("condition") + ' ' + str(i.Content))
        else:
            print('\t'*level + i.Context.attrib.get("search") + ' ' + i.attrib.get("condition") + ' ' + str(i.Content) + ' ' + str(logicOperator))
    
def walkIndicatorold(ind):
    global level
    logicOperator=str(ind.attrib.get("operator")).lower()    
    
    #if this is only one level of indicator, just walk our indicator items
    #else walk indicators then their indicator items.
    print(len(ind.findall("//*[local-name()='Indicator']")))
    if len(ind.findall("//*[local-name()='Indicator']"))==1:    
        print('\t'*level + logicOperator + ' (')        
        walkIndicatorItems(ind)
    else:
        if len(ind.findall("./*[local-name()='IndicatorItem']"))>0:
            print('walking local indicator items first')
            walkIndicatorItems(ind)        
        for i in ind.findall("./*[local-name()='Indicator']"):          
            #print('\t'*level + str(i.attrib))
            logicOperator=str(i.attrib.get("operator")).lower()
            print('\t'*level + logicOperator + ' (')
            if len(i.findall("./*[local-name()='IndicatorItem']"))>0:
                walkIndicatorItems(i)
            
            if len(i.findall("./*[local-name()='Indicator']"))>0:
                level+=1            
                walkIndicator(i)
                level-=1
            print('\t'*level + ')') 


def walkIndicator(ind):
    global level    
    #walk any indicator items first: 
    if len(ind.findall("./*[local-name()='IndicatorItem']"))>0:
        #print('walking local indicator items first')
        walkIndicatorItems(ind)     

    #walk any indicators (and their indicator items recursively)
    for i in ind.findall("./*[local-name()='Indicator']"):          
        level+=1
        logicOperator=str(i.attrib.get("operator")).lower()
        print('\t'*level + logicOperator + ' (')        
        walkIndicator(i)
        level-=1
        print('\t'*level + ' )')                


print('parsing %s'%(sys.argv[1]))
ioco=lxml.objectify.parse(sys.argv[1])
print(ioco)
root=ioco.getroot()
level=1
print("%s: %s"%(root.short_description, root.description))

#for Indicator in root.findall("//*[local-name()='Indicator']")[0]:
#    walkIndicator(Indicator)
walkIndicator(root.definition.Indicator)

