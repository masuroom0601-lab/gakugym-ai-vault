# 手直し3回目(2026-11-26、益田さんの指示「勇者サークルを普段着で描き直す」)
# 第6・7話のキャンパス・面接の場面で、勇者サークル4人を普段着で描き直す。
# 普段着の見本(characters/designs_v5/casual_*.jpg)を使い、見た目の文の中の冒険の服(魔女帽子・金の縁取りの上着など)を普段着の文に置きかえる。
# 回想(flashback)のコマは、冒険のころの姿なので描き直さない
import importlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import layout
from fix_2026_11_25 import CFG, REFS, R, NEG, FIX_NEG, best_size
from ep05_panels import LOOK, GEAR
from lora_ds_2026_11_25 import CASUAL

REFS = {**REFS, **{f"cas_{w}": f"characters/designs_v5/casual_{w}.jpg" for w in CASUAL}}
COSTUME_NEG = "armor, cape, sword, staff, weapon, witch hat, hat, robe, fantasy costume, gold trim, long coat, holy staff, spell book"
PANELS = {}
EXTRA = {}
def fix(sp):
    p = sp.get("prompt", "")
    if "flashback" in p: return None
    for who, look in LOOK.items():
        if look in p:
            for g in GEAR.values(): p = p.replace(", " + g, "")
            p = p.replace(look, CASUAL[who] + ", casual clothes")
            return {**sp, **R(f"cas_{who}", 0.4), "prompt": p, "seeds": [4, 5, 6], "neg": f"{sp.get('neg', NEG)}, {FIX_NEG}, {COSTUME_NEG}"}
    return None
for ep in (6, 7):
    m = importlib.import_module(f"ep{ep:02d}_panels")
    spec_n = importlib.util.spec_from_file_location("n", os.path.join(HERE, f"ep{ep:02d}_name.py"))
    name = importlib.util.module_from_spec(spec_n); spec_n.loader.exec_module(name)
    for (pg, i), sp in m.PANELS.items():
        j = fix(sp)
        if not j: continue
        b = layout.page_panels(name, pg)[i - 1]["bbox"]; w, h = best_size(b[2] - b[0], b[3] - b[1])
        EXTRA[f"e{ep}_p{pg:02d}_{i}"] = {**j, "w": w, "h": h}
    for nm, sp in m.EXTRA.items():
        j = fix(sp)
        if j: EXTRA[nm] = {**j, "seeds": [4, 5], "w": sp.get("w", 832), "h": sp.get("h", 1216)}
