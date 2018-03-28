#!/usr/bin/env python3

import sys
import os
import warnings
from lxml import etree as ET

class Namespaces(object):
    def get(self, alias):
        if alias in self.k2k:
            alias = self.k2k[alias]
        return self.xmlns[alias]
    def __init__(self, prevns = dict()):
        self.xmlns = prevns
        val2k = { v:k for k,v in prevns.items() }
        self.k2k = dict()
        newns_list = [ ['cas', "http:///uima/cas.ecore"],
                       ['xmi', "http://www.omg.org/XMI"],
                       ['tcas', "http:///uima/tcas.ecore"],
                       ['ixatypes', "http:///ixa/ehu.eus/ixa-pipes/types.ecore"] ]
        for nk, nv in newns_list:
            if nv in val2k:
                if nk != val2k[nv]:
                    self.k2k[nk] = val2k[nv]
            else:
                self.xmlns[nk] = nv
    def get_map(self):
        res = self.xmlns.copy()
        for k in self.k2k:
            res[k] = res[k2k[k]]
        return res

class Parse_state(object):
    def __init__(self, raw, ns = dict()):
        self.sofaId = "1"
        self.raw = raw
        self.omaps = { 'w' : dict(), # tokens
                       't' : dict()  # terms
        }
        self.ns = Namespaces(ns)
        self.viewIds = []
        self.tmpName = None
        self.id = 0

    def get_nsmap(self):
        return self.ns.get_map()

    def next_id(self, updateView = True):
        res = str(self.id)
        if updateView:
            self.viewIds.append(res)
        self.id += 1
        return res

    def qname(self, ns, name):
        return ET.QName(self.ns.get(ns), name)

    # Note, offsets are stored as ints
    def set_offset(self, id, b, e):
        dmap = self.omaps[id[0]]
        if dmap is None:
            raise Exception("[E] Can not guess map type using id {}".format(id))
        dmap[id] = [b, e]

    # Note, offsets are stored as ints
    def oRange(self, tgtids):
        if len(tgtids) == 0:
            return (0, 0)
        # guess map type according to first character in tgtid
        dmap = self.omaps[tgtids[0][0]]
        if dmap is None:
            raise Exception("[E] Can not guess map type using id {}".format(tgtids[0]))
        if tgtids[0] not in dmap:
            raise Exception("[E] undefined id {}".format(tgtids[0]))
        b, e = dmap[tgtids[0]]
        for i in range(len(tgtids) - 1):
            if tgtids[i + 1] not in dmap:
                raise Exception("[E] undefined id {}".format(tgtids[i + 1]))
            bb, ee = dmap[tgtids[i + 1]]
            b = min(b, bb)
            e = max(e, ee)
        return (b, e)

def xmi_info(naf):
    '''Return an XMI doxument given an input NAF'''
    def xtract_xmi_info(naf):
        xmilp = naf.xpath('./nafHeader/linguisticProcessors[@layer="xmi"]/lp')
        if len(xmilp) == 0:
            return (None, None)
        if xmilp[0] is None:
            return (None, None)
        xminame = xmilp[0].get("name")
        if not os.path.exists(xminame):
            return (None, None)
        sofaid = xmilp[0].get("version")
        if sofaid is None:
            sofaid = "-1"
        return (xminame, sofaid)

    def simple_xmi(naf):
        try:
            r = get_raw(naf)
        except:
            warnings.warn("Can not parse input NAF")
            r = ""
        pstate = Parse_state(r)
        out = ET.Element(pstate.qname('xmi', 'XMI'), nsmap = pstate.get_nsmap())
        casnull(pstate, out)
        sofa(pstate, out)
        return out, pstate


    def parse_xmi(name):
        ''' parse XMI and include new namespaces in root element'''
        new_ns = Namespaces().get_map()
        tree = ET.parse(name)
        root = tree.getroot()
        for k,v in root.nsmap.items():
            if k not in new_ns:
                new_ns[k] = v
        new_root = ET.Element(root.tag, nsmap = new_ns)
        new_root[:] = root[:]
        xid = 0
        if 'xmi' in new_ns:
            aidtag = "{{{}}}{}".format(new_ns['xmi'], 'id')
            # {http://www.omg.org/XMI}id
            for item in new_root.iterdescendants():
                xxid = item.get(aidtag)
                if xxid is not None:
                    xid = max(xid, int(xxid))
        return new_root, xid

    xminame, sofaid = xtract_xmi_info(naf)
    if xminame is None:
        return simple_xmi(naf)
    xmiroot, xid = parse_xmi(xminame)
    ns = xmiroot.nsmap
    sofatag = "{{{}}}{}".format(ns['cas'], 'Sofa')
    sofaelem = xmiroot.find(sofatag)
    raw = ""
    if sofaelem is not None:
        raw = sofaelem.get('sofaString')
    pstate = Parse_state(raw, ns)
    pstate.sofaId = sofaid
    pstate.id = xid + 1
    pstate.tmpName = xminame
    return xmiroot, pstate

def targets(elem):
    targets = []
    head = None
    if elem is None:
        return (targets, head)
    span = elem.find("span")
    if span is None:
        return (targets, head)
    for t in span.findall("target"):
        tid = t.get("id")
        if "head" in t:
            head = tid
        targets.append(tid)
    return (targets, head)

def get_raw(tree):
    relem = tree.find("raw")
    return relem.text

def tok(tree, pstate, out):
    text = tree.find("text")
    if text is None:
        return
    for wf in text.findall("wf"):
        b = int(wf.get("offset"))
        e = b + int(wf.get("length"))
        pstate.set_offset(wf.get("id"), b, e)
        tcas = ET.SubElement(out, pstate.qname('ixatypes', 'tok'))
        tcas.set(pstate.qname('xmi', 'id'), pstate.next_id())
        tcas.set('sofa', pstate.sofaId)
        tcas.set('begin', str(b))
        tcas.set('end', str(e))

def pos(tree, pstate, out):
    terms = tree.find("terms")
    if terms is None:
        return
    for term in terms.findall("term"):
        lemma = term.get("lemma")
        pos = term.get("pos")
        morphofeat = term.get("morphofeat")
        wids, _ = targets(term)
        b, e = pstate.oRange(wids)
        pstate.set_offset(term.get("id"), b, e)
        tcas = ET.SubElement(out, pstate.qname('ixatypes', 'lexUnit'))
        tcas.set(pstate.qname('xmi', 'id'), pstate.next_id())
        tcas.set('sofa', pstate.sofaId)
        tcas.set('begin', str(b))
        tcas.set('end', str(e))
        tcas.set('lemma', lemma)
        tcas.set('posTag', pos)
        tcas.set('morphofeat', morphofeat)

def ner(tree, pstate, out):
    entities = tree.find("entities")
    if entities is None:
        return
    for entity in entities.findall("entity"):
        etype = entity.get("type")
        tcas = ET.SubElement(out, pstate.qname('ixatypes', 'entity'))
        tids, _ = targets(entity.find("references"))
        b, e = pstate.oRange(tids)
        tcas.set(pstate.qname('xmi', 'id'), pstate.next_id())
        tcas.set('sofa', pstate.sofaId)
        tcas.set('begin', str(b))
        tcas.set('end', str(e))
        tcas.set('type', etype)

def chunk(tree, pstate, out):
    chunks = tree.find("chunks")
    if chunks is None:
        return
    for chunk in chunks.findall("chunk"):
        phrase = chunk.get("phrase")
        tcas = ET.SubElement(out, pstate.qname('ixatypes', 'chunk'))
        tids, _ = targets(chunk)
        b, e = pstate.oRange(tids)
        tcas.set(pstate.qname('xmi', 'id'), pstate.next_id())
        tcas.set('sofa', pstate.sofaId)
        tcas.set('begin', str(b))
        tcas.set('end', str(e))
        tcas.set('phrase', phrase)

def doc(tree, pstate, out):
    e = str(len(pstate.raw))
    topics = tree.find("topics")
    if topics is None:
        return
    for topic in topics.findall("topic"):
        tcas = ET.SubElement(out, pstate.qname('ixatypes', 'topic'))
        tcas.set(pstate.qname('xmi', 'id'), pstate.next_id())
        tcas.set('sofa', pstate.sofaId)
        tcas.set('begin', "0")
        tcas.set('end', str(e))
        conf = topic.get("confidence")
        if conf is not None:
            conf = "1.0"
        value = topic.text
        tcas.set('confidence', conf)
        tcas.set('value', value)

def casnull(pstate, out):
    null = ET.SubElement(out, pstate.qname('cas', 'NULL'))
    null.set(pstate.qname('xmi', 'id'), pstate.next_id(updateView = False))

def sofa(pstate, out):
    sofa = ET.SubElement(out, pstate.qname('cas', 'Sofa'))
    pstate.sofaId = pstate.next_id(updateView = False)
    sofa.set(pstate.qname('xmi', 'id'), pstate.sofaId)
    sofa.set('sofaNum', "1")
    sofa.set('sofaId', "_initialView")
    sofa.set('mimeType', "text")
    sofa.set('sofaString', pstate.raw)

def view(pstate, out):
    view_ids = pstate.viewIds
    if len(view_ids) == 0:
        return
    view = ET.SubElement(out, pstate.qname('cas', 'View'))
    view.set('sofa', pstate.sofaId)
    view.set('members', " ".join(view_ids))

def main():
    try:
        naftree = ET.parse(sys.stdin)
        naf = naftree.getroot()
        oroot, pstate = xmi_info(naf)
        # add layers
        tok(naf, pstate, oroot)
        pos(naf, pstate, oroot)
        ner(naf, pstate, oroot)
        chunk(naf, pstate, oroot)
        doc(naf, pstate, oroot)
        view(pstate, oroot)

        # write
        a = ET.tostring(oroot, encoding="utf-8")
        print(a.decode("utf-8"))
        if pstate.tmpName is not None:
            os.remove(pstate.tmpName)
    except Exception as e:
        msg = "Warning: an exception occured: {}".format(e)
        warnings.warn(msg)
        raise

main()
