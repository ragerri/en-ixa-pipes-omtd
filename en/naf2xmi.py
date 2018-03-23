#!/usr/bin/env python3

import sys
import warnings
import xml.etree.ElementTree as ET

class Namespaces(object):
    def register(self, alias, ns):
        ET.register_namespace(alias, ns)
        self.xmlns[alias] = ns
    def get(self, alias):
        return self.xmlns[alias]
    def __init__(self):
        self.xmlns = dict()
        self.register('cas', "http:///uima/cas.ecore")
        self.register('xmi', "http://www.omg.org/XMI")
        self.register('tcas', "http:///uima/tcas.ecore")
        self.register('ixatypes', "http:///ixa/ehu.eus/ixa-pipes/types.ecore")

class Parse_state(object):
    def __init__(self, raw):
        self.sofaId = "1"
        self.raw = raw
        self.omaps = { 'w' : dict(), # tokens
                       't' : dict()  # terms
        }
        self.ns = Namespaces()
        self.viewIds = []
        self.id = 0

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

def parse_naf_fh(fh):
    # NOTE: this does not work if the default coding system of terminal is not UTF8
    tree = ET.parse(fh)
    return tree.getroot()

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
    view = ET.SubElement(out, pstate.qname('cas', 'View'))
    view.set('sofa', pstate.sofaId)
    view.set('members', " ".join(pstate.viewIds))

def main():
    try:
        naf = parse_naf_fh(sys.stdin)
        r = get_raw(naf)
        pstate = Parse_state(r)
        out = ET.Element(pstate.qname('xmi', 'XMI'))

        # add layers
        casnull(pstate, out)
        sofa(pstate, out)
        tok(naf, pstate, out)
        pos(naf, pstate, out)
        ner(naf, pstate, out)
        chunk(naf, pstate, out)
        doc(naf, pstate, out)
        view(pstate, out)

        # write
        otree = ET.ElementTree(out)
        otree.write(sys.stdout, encoding = "unicode")
    except Exception as e:
        msg = "Warning: an exception occured: {}".format(e)
        warnings.warn(msg)
        raise

main()
