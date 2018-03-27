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
    nafHeader = ET.SubElement(naf, 'nafHeader')
    linguisticProcessors = ET.SubElement(nafHeader, 'linguisticProcessors')
    linguisticProcessors.set('layer', 'xmi')
    lp = ET.SubElement(linguisticProcessors, 'lp')
    lp.set('name', xminame)
    lp.set('version', sofaid)
    raw = ET.SubElement(naf, 'raw')
    raw.text = ET.CDATA(sofatext)
    return naf

def main():
    try:
        tree = ET.parse(sys.stdin)
        xmi = tree.getroot()
        ns = xmi.nsmap.copy()
        rawtext = ""
        sofaid = "-1"
        sofatag = qname(ns, 'cas', 'Sofa')
        if len(sofatag):
            sofa = xmi.find(sofatag)
            if sofa is not None:
                #rawtext = sofa.get('sofaString').encode("utf-8")
                id = sofa.get(qname(ns, 'xmi', 'id'))
                if id is not None:
                    sofaid = id
                rawtext = sofa.get('sofaString')
        xmiTemp = tempfile.NamedTemporaryFile(delete=False)
        tree.write(xmiTemp)
        naf = create_naf(rawtext, sofaid, xmiTemp.name)
        #print(xmiTemp.name)
        # write
        a = ET.tostring(naf, encoding="utf-8")
        print(a.decode("utf-8"))

    except Exception as e:
        msg = "Warning: an exception occured: {}".format(e)
        warnings.warn(msg)
        raise

main()
