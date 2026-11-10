"""Tracked-change helpers for a merged-runs word/document.xml (lxml)."""
import copy, datetime
from lxml import etree
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
q = lambda t: "{%s}%s" % (W, t)
XS = "{http://www.w3.org/XML/1998/namespace}space"
AUTHOR = "Claude"
DATE = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_id = [9000]
def nid():
    _id[0] += 1
    return str(_id[0])

def runs(p):
    return [r for r in p if r.tag == q("r")]

def rtext(r):
    return "".join(t.text or "" for t in r if t.tag == q("t"))

def ptext(p):
    return "".join(rtext(r) for r in runs(p))

def split_run(r, off):
    """split run r at text offset off; returns (left, right) both in tree"""
    if off <= 0 or off >= len(rtext(r)):
        return None
    right = copy.deepcopy(r)
    # left keeps first off chars, right keeps rest
    def trim(run, keep_left):
        pos = 0
        for ch in list(run):
            if ch.tag == q("rPr"):
                continue
            if ch.tag == q("t"):
                s = ch.text or ""
                a, b = pos, pos + len(s)
                pos = b
                if keep_left:
                    if a >= off: run.remove(ch)
                    elif b > off: ch.text = s[: off - a]; ch.set(XS, "preserve")
                else:
                    if b <= off: run.remove(ch)
                    elif a < off: ch.text = s[off - a:]; ch.set(XS, "preserve")
            else:
                # non-text (lastRenderedPageBreak etc.) stays on the left side only
                if not keep_left and pos <= off: run.remove(ch)
                if keep_left and pos > off: run.remove(ch)
    trim(r, True); trim(right, False)
    r.addnext(right)
    return r, right

def isolate(p, start, end):
    """make [start,end) of paragraph text map to whole runs; return those runs"""
    pos = 0
    for r in runs(p):
        L = len(rtext(r))
        if pos < start < pos + L:
            split_run(r, start - pos)
            return isolate(p, start, end)
        if pos < end < pos + L:
            split_run(r, end - pos)
            return isolate(p, start, end)
        pos += L
    out, pos = [], 0
    for r in runs(p):
        L = len(rtext(r))
        if pos >= start and pos + L <= end and L > 0:
            out.append(r)
        pos += L
    return out

def mk_run(rpr_src, text):
    r = etree.Element(q("r"))
    rp = rpr_src.find(q("rPr")) if rpr_src is not None else None
    if rp is not None:
        r.append(copy.deepcopy(rp))
    t = etree.SubElement(r, q("t")); t.text = text; t.set(XS, "preserve")
    return r

def mark(tag):
    e = etree.Element(q(tag)); e.set(q("id"), nid()); e.set(q("author"), AUTHOR); e.set(q("date"), DATE)
    return e

def replace_in_par(p, old, new):
    s = ptext(p); i = s.find(old)
    if i < 0: return False
    rs = isolate(p, i, i + len(old))
    first = rs[0]
    d = mark("del"); first.addprevious(d)
    for r in rs:
        for t in r.findall(q("t")):
            t.tag = q("delText")
        d.append(r)
    if new:
        ins = mark("ins"); ins.append(mk_run(rs[0], new)); d.addnext(ins)
    return True

def insert_in_par(p, after_text, new):
    """insert new text right after after_text (tracked)"""
    s = ptext(p); i = s.find(after_text)
    if i < 0: return False
    end = i + len(after_text)
    rs = isolate(p, i, end)
    ins = mark("ins"); ins.append(mk_run(rs[-1], new)); rs[-1].addnext(ins)
    return True

def new_par_after(p, text, bold=False, template=None):
    """insert a tracked new paragraph after p, styled like template (default p)"""
    tpl = template if template is not None else p
    np = etree.Element(q("p"))
    ppr = tpl.find(q("pPr"))
    ppr = copy.deepcopy(ppr) if ppr is not None else etree.Element(q("pPr"))
    rpr = ppr.find(q("rPr"))
    if rpr is None:
        rpr = etree.SubElement(ppr, q("rPr"))
    for old in rpr.findall(q("ins")) + rpr.findall(q("del")):
        rpr.remove(old)
    rpr.insert(0, mark("ins"))
    np.append(ppr)
    src = None
    for r in runs(tpl):
        if rtext(r): src = r; break
    run = mk_run(src, text)
    rp = run.find(q("rPr"))
    if rp is not None:
        for b in rp.findall(q("b")) + rp.findall(q("bCs")): rp.remove(b)
    if bold:
        if rp is None: rp = etree.Element(q("rPr")); run.insert(0, rp)
        etree.SubElement(rp, q("b")); etree.SubElement(rp, q("bCs"))
    for lb in run.findall(q("lastRenderedPageBreak")): run.remove(lb)
    ins = mark("ins"); ins.append(run); np.append(ins)
    p.addnext(np)
    return np

def comment_markers(p, anchor, cid):
    s = ptext(p); i = s.find(anchor)
    if i < 0: return False
    rs = isolate(p, i, i + len(anchor))
    a = etree.Element(q("commentRangeStart")); a.set(q("id"), str(cid)); rs[0].addprevious(a)
    b = etree.Element(q("commentRangeEnd")); b.set(q("id"), str(cid)); rs[-1].addnext(b)
    ref = etree.Element(q("r")); rp = etree.SubElement(ref, q("rPr")); st = etree.SubElement(rp, q("rStyle")); st.set(q("val"), "CommentReference")
    cr = etree.SubElement(ref, q("commentReference")); cr.set(q("id"), str(cid)); b.addnext(ref)
    return True

def delete_par(p):
    """tracked deletion of a whole paragraph (direct runs + paragraph mark)"""
    for ins in [c for c in p if c.tag == q("ins")]:
        p.remove(ins)   # our own pending insertions simply disappear
    for r in runs(p):
        if not rtext(r) and r.find(q("drawing")) is None:
            continue
        d = mark("del"); r.addprevious(d)
        for t in r.findall(q("t")): t.tag = q("delText")
        d.append(r)
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = etree.Element(q("pPr")); p.insert(0, ppr)
    rpr = ppr.find(q("rPr"))
    if rpr is None:
        rpr = etree.SubElement(ppr, q("rPr"))
    rpr.insert(0, mark("del"))


def full_text(p):
    out = []
    for c in p:
        if c.tag == q("r"): out.append(rtext(c))
        elif c.tag == q("ins"):
            for r in c.findall(q("r")): out.append(rtext(r))
    return "".join(out)
