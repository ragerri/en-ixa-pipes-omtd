#!/usr/bin/env python3

import sys
import tempfile
import warnings
from lxml import etree as ET

def qname(ns, key, name):
    if key in ns:
        return "{{{}}}{}".format(ns[key], name)
    return name

def create_naf(sofatext, sofaid, xminame):
    naf = ET.Element("NAF")
    naf.set('version', 'v1.naf')
    naf.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')
    nafHeader = ET.SubElement(naf, 'nafHeader')
    linguisticProcessors = ET.SubElement(nafHeader, 'linguisticProcessors')
    linguisticProcessors.set('layer', 'xmi')
    lp = ET.SubElement(linguisticProcessors, 'lp')
    lp.set('name', xminame)
    lp.set('version', sofaid)
    raw = ET.SubElement(naf, 'raw')
    raw.text = ET.CDATA(sofatext)
    return naf

def search_text(xmi):
    ns = xmi.nsmap.copy()
    rawtext = ""
    sofaid = "-1"
    sofatag = qname(ns, 'cas', 'Sofa')
    for sofa in xmi.findall(sofatag):
        #if sofa.get('sofaId') != '_InitialView':
        #    continue
        id = sofa.get(qname(ns, 'xmi', 'id'))
        if id is not None:
            sofaid = id
        rawtext = sofa.get('sofaString')
        break
    return rawtext, sofaid

def emptyNAF():
    naf = ET.Element("NAF")
    naf.set('version', 'v1.naf')
    return naf

def main():
    try:
        tree = ET.parse(sys.stdin)
        xmi = tree.getroot()
        rawtext, sofaid = search_text(xmi)
        xmiTemp = tempfile.NamedTemporaryFile(delete=False)
        tree.write(xmiTemp)
        naf = create_naf(rawtext, sofaid, xmiTemp.name)
    except Exception as e:
        msg = "Warning: an exception occured: {}".format(e)
        warnings.warn(msg)
        naf = emptyNAF()
    #print(xmiTemp.name)
    # write
    a = ET.tostring(naf, encoding="utf-8")
    print(a.decode("utf-8"))

main()
