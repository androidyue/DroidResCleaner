#!/usr/bin/env python
# coding=utf-8
from os import listdir,path, system
from sys import argv
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def genRegionLangPair(filePath):
    basicLanguage = None
    if ('values' in filePath) :
        hasRegionLimit = ('r' == filePath[-3:-2])
        if (hasRegionLimit):
            basicLanguage = filePath[0:-4]
            if (not path.exists(basicLanguage)) :
                return None 
            belongsToEnglish =  ("values-en" in basicLanguage)
            if (belongsToEnglish):
                #Compare with the res/values/strings.xml
                return (path.dirname(basicLanguage) + '/values/strings.xml', filePath + "/strings.xml")
            else:
                return (basicLanguage + '/strings.xml', filePath + "/strings.xml")
    return None

def genLangPair(filePath):
    def shouldGenLanPair(filePath):
        if (not 'values' in filePath ):
            return False
        if('dpi' in filePath):
            return False
        if ('dimes' in filePath):
            return False
        if ('large' in filePath):
            return False 
        return True

    if(shouldGenLanPair(filePath)):
        basicLanguage = path.dirname(filePath) + '/values/strings.xml'
        targetLanguage = filePath + '/strings.xml'
        if (not path.exists(targetLanguage)):
           return None 

        if (not path.samefile(basicLanguage,targetLanguage)) :
            return (basicLanguage, targetLanguage)
    return None

def genCompareList(filePath):
    compareLists = []
    for file in listdir(filePath):
        regionPair = genRegionLangPair(filePath + '/' + file)
        if (None != regionPair):
            compareLists.append(regionPair)
        
        languagePair = genLangPair(filePath + '/' + file) 
        if (None != languagePair) :
            compareLists.append(languagePair)

    return compareLists

def getXmlEntries(filePath):
    root = ET.ElementTree(file=filePath).getroot()
    entries = {}
    for child in root:
        attrib = child.attrib
        if (None != attrib) :
            entries[attrib.get('name')] = child.text
    print 'xmlEntriesCount',len(entries)
    return entries

def rewriteRegionFile(sourceEntries, filePath):
    if (not path.exists(filePath)):
        return 
    ET.register_namespace('xliff',"urn:oasis:names:tc:xliff:document:1.2")
    tree = ET.ElementTree(file=filePath)
    root = tree.getroot()
    print root
    totalCount = 0
    removeCount = 0
    unRemoveCount = 0
    print len(root)
    toRemoveList = []
    for child in root:
        totalCount = totalCount + 1
        attrib = child.attrib
        if (None == attrib):
            continue

        childName = attrib.get('name')

        if (sourceEntries.get(childName) == child.text):
            removeCount = removeCount + 1
            toRemoveList.append(child)
        else:
            unRemoveCount = unRemoveCount + 1
            print childName, sourceEntries.get(childName), child.text
    print filePath,totalCount, removeCount,unRemoveCount

    for aItem in toRemoveList:
        root.remove(aItem)

    if (len(root) != 0 ):
        tree.write(filePath, encoding="UTF-8")
    else:
        command = 'rm -rf %s'%(path.dirname(filePath))
        print command
        system(command)
    


def main(projectDir):
    lists = genCompareList(projectDir + "/res/")

    for item in lists:
        print item
        src = item[0]
        dest = item[1]
        rewriteRegionFile(getXmlEntries(src),dest)

if __name__ == "__main__":
    if (len(argv) == 2) :
        main(argv[1])
