import sys
from lxml import etree
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"; q = lambda t: "{%s}%s" % (W, t)
path = sys.argv[1] + "/word/document.xml"
tree = etree.parse(path); body = tree.getroot().find(q("body"))
def ptext(p): return "".join(t.text or "" for r in p if r.tag == q("r") for t in r.findall(q("t")))
def find_par(sub):
    for p in body.iter(q("p")):
        if sub in ptext(p): return p
# 段落の字下げ(本文は1字下げ、「で始まる会話・見出し・箇条書き・図・参考文献は除く)
def vis_text(p):
    out = []
    for c in p.iter(q("t")): out.append(c.text or "")
    return "".join(out).strip()
start = find_par("まえがき：この本を開いてくれた「君」へ")
in_body = False; refs = False; changed = 0
import re as _re
for p in body.iter(q("p")):
    if p is start: in_body = True; continue
    if not in_body: continue
    txt = vis_text(p)
    if txt == "参考文献": refs = True; continue
    if txt == "著者プロフィール": refs = False
    if not txt or refs: continue
    ppr = p.find(q("pPr"))
    if ppr is None: ppr = etree.Element(q("pPr")); p.insert(0, ppr)
    if ppr.find(q("numPr")) is not None or ppr.find(q("jc")) is not None: continue
    bold = any(r.find(q("rPr")) is not None and r.find(q("rPr")).find(q("b")) is not None for r in p.iter(q("r")) if (r.findtext(q("t")) or "").strip())
    if bold: continue
    first = txt[0]
    if first in "「『【□・（(-" or _re.match(r"^[0-9０-９]+[.．]", txt) or _re.match(r"^[A-Za-z]", txt): continue
    ind = ppr.find(q("ind"))
    if ind is None:
        ind = etree.Element(q("ind"))
        AFTER = {q(x) for x in ["contextualSpacing","mirrorIndents","suppressOverlap","jc","textDirection","textAlignment","textboxTightWrap","outlineLvl","divId","cnfStyle","rPr","sectPr","pPrChange"]}
        nxt_ = next((c for c in ppr if c.tag in AFTER), None)
        if nxt_ is not None: nxt_.addprevious(ind)
        else: ppr.append(ind)
    if ind.get(q("firstLineChars")) != "100":
        ind.set(q("firstLineChars"), "100"); ind.set(q("firstLine"), "220")
        for k in (q("hanging"), q("hangingChars")):
            if k in ind.attrib: del ind.attrib[k]
        changed += 1
print("indent fixed:", changed)
tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)
