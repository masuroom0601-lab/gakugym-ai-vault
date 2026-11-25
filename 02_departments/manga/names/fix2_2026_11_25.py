# 全話の手直し 2回目(2026-11-25)。1回目で描いた見本の絵(characters/designs_v5/)を使い、
# 第6・7話の人事の男性・キャリアセンターの職員のコマと部品を、同じ顔で描き直す。
# あわせて第2話20ページ1コマ目(暗い勇者サークルの部室。白紙の作戦メモ)を描き直す
import importlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import layout
from fix_2026_11_25 import CFG, REFS, R, NEG, FIX_NEG, best_size
from ep06_panels import STAFF, HR

REFS = {**REFS, "hr": "characters/designs_v5/hr.jpg", "staff": "characters/designs_v5/staff.jpg"}
PANELS = {}
EXTRA = {}
for ep in (6, 7):
    m = importlib.import_module(f"ep{ep:02d}_panels")
    spec_n = importlib.util.spec_from_file_location("n", os.path.join(HERE, f"ep{ep:02d}_name.py"))
    name = importlib.util.module_from_spec(spec_n); spec_n.loader.exec_module(name)
    def fix(sp):
        who = "hr" if HR in sp["prompt"] else "staff" if STAFF in sp["prompt"] else None
        if not who: return None
        return {**sp, **R(who, 0.55), "seeds": [4, 5, 6], "neg": f"{sp.get('neg', NEG)}, {FIX_NEG}"}
    for (p, i), sp in m.PANELS.items():
        j = fix(sp)
        if not j: continue
        b = layout.page_panels(name, p)[i - 1]["bbox"]; w, h = best_size(b[2] - b[0], b[3] - b[1])
        EXTRA[f"e{ep}_p{p:02d}_{i}"] = {**j, "w": w, "h": h}
    for nm, sp in m.EXTRA.items():
        j = fix(sp)
        if j: EXTRA[nm] = {**j, "seeds": [4, 5], "w": sp.get("w", 832), "h": sp.get("h", 1216)}

EXTRA["e2_p20_1"] = {"seeds": [4, 5, 6], "w": 1216, "h": 832,
                     "prompt": "no humans, dark messy club room at night, sofa, trophies on a shelf, a table with a single blank sheet of paper and a folded map on it, "
                               "window, moonlight, wide shot, detailed background, indoors",
                     "neg": f"{NEG}, {FIX_NEG}, classroom, rows of desks, people"}
