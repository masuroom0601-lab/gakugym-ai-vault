"""見出しスタイル・章の太字と行空け・目次リンク・残りの横向き文字を整える(書式のみ、本文の言葉は変えない)"""
import sys, re, copy
from lxml import etree
D = sys.argv[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"; q = lambda t: "{%s}%s" % (W, t)
XS = "{http://www.w3.org/XML/1998/namespace}space"
doc = etree.parse(D + "/word/document.xml"); body = doc.getroot().find(q("body"))
def tx(p): return "".join(x.text or "" for x in p.iter(q("t")))
def ppr(p):
    e = p.find(q("pPr"))
    if e is None: e = etree.Element(q("pPr")); p.insert(0, e)
    return e
# 目次で第６章の行につながっている第一節を別の行に分ける
for p in list(body.iter(q("p"))):
    s_ = tx(p)
    if s_.startswith("第６章：") and "・第一節" in s_:
        k = s_.index("・第一節"); tail = s_[k:]
        pos = 0
        for t in p.iter(q("t")):
            L = len(t.text or "")
            if pos + L > k:
                cut = max(0, k - pos); t.text = (t.text[:cut]).rstrip(" 　"); t.set(XS, "preserve")
                for t2 in [x for x in p.iter(q("t"))][list(p.iter(q("t"))).index(t) + 1:]: t2.text = ""
                break
            pos += L
        nxt = p.getnext()
        np_ = copy.deepcopy(nxt if nxt is not None and tx(nxt).startswith("・第二節") else p)
        ts = list(np_.iter(q("t")))
        ts[0].text = tail; ts[0].set(XS, "preserve")
        for t2 in ts[1:]: t2.text = ""
        p.addnext(np_)
        break
ps = list(body.iter(q("p")))
first_body = next(i for i, p in enumerate(ps) if tx(p).strip() == "まえがき：この本を開いてくれた「君」へ")

H1 = re.compile(r"^(まえがき：|序章：|第[０-９0-9]+章：|終章：|あとがき$|参考文献$|著者プロフィール$|「学ジム」が大切にしていること$|難関に挑む学習者向けコミュニティのご案内$)")
H2 = re.compile(r"^第[一二三四五六七八九]節：")
heads = []
for i in range(first_body, len(ps)):
    s = tx(ps[i]).strip()
    lvl = 1 if H1.match(s) else 2 if H2.match(s) else 0
    if not lvl: continue
    p = ps[i]; pp = ppr(p)
    for old in pp.findall(q("pStyle")): pp.remove(old)
    st = etree.Element(q("pStyle")); st.set(q("val"), "Heading%d" % lvl); pp.insert(0, st)
    for ind in pp.findall(q("ind")): pp.remove(ind)          # 見出しは字下げしない
    for r in p.iter(q("r")):
        if not (r.findtext(q("t")) or "").strip(): continue
        rp = r.find(q("rPr"))
        if rp is None: rp = etree.Element(q("rPr")); r.insert(0, rp)
        if rp.find(q("b")) is None:
            b = etree.Element(q("b")); bcs = etree.Element(q("bCs"))
            # rFonts/rStyle の後ろに置く
            pos = 0
            for k, c in enumerate(rp):
                if c.tag in (q("rStyle"), q("rFonts")): pos = k + 1
            rp.insert(pos, b); rp.insert(pos + 1, bcs)
    heads.append((i, lvl, s))

# 第２章以降(第２〜６章・終章)の前に空行を1つ
added = 0
for i, lvl, s in heads:
    if lvl == 1 and re.match(r"^(第[２-６2-6]章：|終章：)", s):
        p = ps[i]; prev = p.getprevious()
        if prev is None or prev.tag != q("p") or tx(prev).strip():
            blank = etree.Element(q("p")); p.addprevious(blank); added += 1

# 目次の各行を本文の見出しへのリンクにする
toc_start = next(i for i, p in enumerate(ps) if tx(p).strip() == "目次")
toc = [(i, tx(ps[i]).strip()) for i in range(toc_start + 1, first_body) if tx(ps[i]).strip()]
norm = lambda s: re.sub(r"[・：「」\s　]", "", s)
hi = 0; linked = 0
for n, (i, s) in enumerate(toc):
    key = norm(s)
    for j in range(hi, len(heads)):
        if norm(heads[j][2]) == key:
            name = "_Toc_h%03d" % j
            hp = ps[heads[j][0]]
            if hp.find(q("bookmarkStart")) is None:
                bs = etree.Element(q("bookmarkStart")); bs.set(q("id"), str(7000 + j)); bs.set(q("name"), name)
                be = etree.Element(q("bookmarkEnd")); be.set(q("id"), str(7000 + j))
                pp = hp.find(q("pPr")); (pp.addnext(bs) if pp is not None else hp.insert(0, bs)); hp.append(be)
            tp = ps[i]; rs = [c for c in tp if c.tag == q("r")]
            if rs:
                hl = etree.Element(q("hyperlink")); hl.set(q("anchor"), name); hl.set(q("history"), "1")
                rs[0].addprevious(hl)
                for r in rs: hl.append(r)
                linked += 1
            hi = j + 1
            break

# 残りの横向き文字: 全角数字のあとの半角ピリオド、URL行の「QR」
dots = 0
for p in body.iter(q("p")):
    if re.match(r"^[０-９]\.", tx(p).strip()):
        for t in p.iter(q("t")):
            if t.text and t.text.startswith("."):
                t.text = "．" + t.text[1:]; t.set(XS, "preserve"); dots += 1; break
for t in body.iter(q("t")):
    if t.text:
        new = re.sub(r"(?<=[０-９])\.(?=\s)", "．", t.text)
        new = new.replace("QRコード", "ＱＲコード")
        if new != t.text: t.text = new; t.set(XS, "preserve"); dots += 1
doc.write(D + "/word/document.xml", xml_declaration=True, encoding="UTF-8", standalone=True)

# 見出しスタイル: 太字・黒・本文に近い大きさ・字下げなし
st = etree.parse(D + "/word/styles.xml")
for s in st.getroot().findall(q("style")):
    sid = s.get(q("styleId"))
    if sid in ("Heading1", "Heading2"):
        rp = s.find(q("rPr"))
        for c in list(rp): rp.remove(c)
        rf = etree.SubElement(rp, q("rFonts")); rf.set(q("asciiTheme"), "majorHAnsi"); rf.set(q("eastAsiaTheme"), "majorEastAsia"); rf.set(q("hAnsiTheme"), "majorHAnsi")
        etree.SubElement(rp, q("b")); etree.SubElement(rp, q("bCs"))
        c = etree.SubElement(rp, q("color")); c.set(q("val"), "000000")
        sz = "28" if sid == "Heading1" else "24"
        e = etree.SubElement(rp, q("sz")); e.set(q("val"), sz); e = etree.SubElement(rp, q("szCs")); e.set(q("val"), sz)
        for x in (s.find(q("semiHidden")), s.find(q("unhideWhenUsed"))):
            if x is not None: s.remove(x)
st.write(D + "/word/styles.xml", xml_declaration=True, encoding="UTF-8", standalone=True)

# 自動の番号(1. 2. …)を全角に
nb = etree.parse(D + "/word/numbering.xml"); nn = 0
for l in nb.iter(q("lvl")):
    f = l.find(q("numFmt")); lt = l.find(q("lvlText"))
    if f is not None and f.get(q("val")) == "decimal":
        f.set(q("val"), "decimalFullWidth"); nn += 1
        if lt is not None and lt.get(q("val"), "").endswith("."): lt.set(q("val"), lt.get(q("val"))[:-1] + "．")
nb.write(D + "/word/numbering.xml", xml_declaration=True, encoding="UTF-8", standalone=True)
print("unlinked:", [s for i,s in toc if not any(c.tag==q("hyperlink") for c in ps[i])])
print("headings:", sum(1 for h in heads if h[1] == 1), "chapter-level /", sum(1 for h in heads if h[1] == 2), "sections; blank lines added:", added, "; toc linked:", linked, "/", len(toc), "; dots fixed:", dots, "; numbering levels:", nn)
