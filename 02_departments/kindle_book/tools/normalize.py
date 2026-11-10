"""Accepted docx (unpacked dir): strip comments, convert numbers/Latin for vertical text."""
import sys, re, copy, os, glob
from lxml import etree
D = sys.argv[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"; q = lambda t: "{%s}%s" % (W, t)
XS = "{http://www.w3.org/XML/1998/namespace}space"
path = D + "/word/document.xml"
tree = etree.parse(path); root = tree.getroot(); body = root.find(q("body"))

# 1) コメントを全部はずす
for tag in ("commentRangeStart", "commentRangeEnd"):
    for e in list(root.iter(q(tag))): e.getparent().remove(e)
for e in list(root.iter(q("commentReference"))):
    r = e.getparent(); r.getparent().remove(r)
for f in glob.glob(D + "/word/comments*.xml"): os.remove(f)
rel = D + "/word/_rels/document.xml.rels"; s = open(rel, encoding="utf-8").read()
s = re.sub(r'<Relationship [^>]*Target="comments[^"]*"[^>]*/>', "", s); open(rel, "w", encoding="utf-8").write(s)
ct = D + "/[Content_Types].xml"; s = open(ct, encoding="utf-8").read()
s = re.sub(r'<Override [^>]*PartName="/word/comments[^"]*"[^>]*/>', "", s); open(ct, "w", encoding="utf-8").write(s)

# 2) 縦書き用に数字・英字を整える
Z = str.maketrans("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ%.,", "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ％．，")
H = str.maketrans("０１２３４５６７８９", "0123456789")
TOK = re.compile(r"P\.(?=[0-9０-９])|[0-9０-９]+(?:[.,．，][0-9０-９]+)*|(?<![A-Za-z])[A-Z]{1,4}(?![A-Za-z])|%")
def pieces(text):
    out = []; pos = 0
    for m in TOK.finditer(text):
        if m.start() > pos: out.append((text[pos:m.start()], False))
        tk = m.group(0)
        if tk == "P.": out.append(("Ｐ．", False))
        elif tk == "%": out.append(("％", False))
        elif tk[0].isalpha(): out.append((tk.translate(Z), False))
        else:
            plain = tk.translate(H)
            if any(c in plain for c in ".．"): out.append((plain.translate(Z), False))
            elif any(c in plain for c in ",，"): out.append((plain.replace(",", "").replace("，", "").translate(Z), False))
            elif len(plain) == 2: out.append((plain, True))   # 縦中横
            else: out.append((plain.translate(Z), False))
        pos = m.end()
    if pos < len(text): out.append((text[pos:], False))
    return out

def ptxt(p): return "".join(t.text or "" for t in p.iter(q("t")))
paras = list(body.iter(q("p")))
start = next(i for i, p in enumerate(paras) if "【タイトル】" in ptxt(p))
ref = next(i for i, p in enumerate(paras) if ptxt(p).strip() == "参考文献" and i > 50)
prof = next(i for i, p in enumerate(paras) if ptxt(p).strip() == "著者プロフィール" and i > ref)
targets = [p for i, p in enumerate(paras) if start <= i < ref or i > prof]
tcy_id = [500]; nt = 0; nz = 0
for p in targets:
    t_all = ptxt(p)
    if "https://" in t_all: continue
    for r in list(p.iter(q("r"))):
        ts = r.findall(q("t"))
        if len(ts) != 1 or not ts[0].text: continue
        _rp = r.find(q("rPr"))
        if _rp is not None and _rp.find(q("eastAsianLayout")) is not None: continue
        text = ts[0].text
        pcs = pieces(text)
        if len(pcs) == 1 and not pcs[0][1]:
            if pcs[0][0] != text: ts[0].text = pcs[0][0]; ts[0].set(XS, "preserve"); nz += 1
            continue
        # 分割して新しいランを並べる
        parent = r.getparent(); idx = parent.index(r)
        rpr = r.find(q("rPr"))
        extra = [c for c in r if c.tag not in (q("rPr"), q("t"))]
        new_runs = []
        for k, (seg, tcy) in enumerate(pcs):
            nr = etree.Element(q("r"))
            if rpr is not None: nr.append(copy.deepcopy(rpr))
            if k == 0:
                for c in extra: nr.append(copy.deepcopy(c))
            if tcy:
                rp = nr.find(q("rPr"))
                if rp is None: rp = etree.Element(q("rPr")); nr.insert(0, rp)
                ea = etree.Element(q("eastAsianLayout")); tcy_id[0] += 1
                ea.set(q("id"), str(tcy_id[0])); ea.set(q("vert"), "1")
                after = [c for c in rp if c.tag in (q("specVanish"), q("oMath"))]
                (after[0].addprevious(ea) if after else rp.append(ea)); nt += 1
            tt = etree.SubElement(nr, q("t")); tt.text = seg; tt.set(XS, "preserve")
            new_runs.append(nr)
        parent.remove(r)
        for k, nr in enumerate(new_runs): parent.insert(idx + k, nr)
        nz += 1
tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)
print("tate-chu-yoko:", nt, "runs changed:", nz)
