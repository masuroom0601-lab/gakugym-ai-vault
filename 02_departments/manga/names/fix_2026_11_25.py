# 全話の手直し 1回目(2026-11-25、益田さんの指示「気になるところをKaggleで描き直して」「第1・2話を新しい設定に合わせて」)
# 話をまたいで1回の作業で描くため、すべて EXTRA(名前つきの部品)として書く。コマは「e話_pページ_コマ」の名前で、
# 元のネームのコマと同じ縦横比で描く。元の作画指示をそのまま使い、シードを変え、墨・文字・集中線を強く禁止する
# - 第3話のシロ: 見本の絵の効きを弱めて(0.25)集中線を防ぐ
# - 第1話2ページ: 「学内イベントの帰り道」を「冒険から帰った夕方の帰り道」に。合成用の部品を描く(ep01_group_fix.py)
# - 人事の男性・キャリアセンターの職員: 顔をそろえるため、まず見本の絵(全身・白背景)を描く。第6・7話のコマは2回目で描き直す
import importlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import layout
from ep05_panels import CFG, REFS, R, NG, NEG, WB, LOOK, GEAR
from ep06_panels import STAFF, HR
sys.path.insert(0, os.path.join(HERE, "..", "tools", "kaggle"))
from build_panels import best_size

FIX_NEG = ("ink splatter, ink stains, ink drips, black blots, splashes, paint splatter, speed lines, focus lines, motion lines, "
           "black brush strokes, abstract background, text, letters, kanji, onomatopoeia, sound effects, speech bubble, comic panels")
TARGETS = {
    3: (["ep03_panels_redo", "ep03_panels"], ["2-1", "10-5", "11-1", "11-3", "14-3", "15-1", "15-3"]),
    4: (["ep04_panels"], ["2-1", "5-2", "5-3", "6-4", "11-3", "14-4", "16-1", "16-3", "17-1"]),
    5: (["ep05_panels"], ["5-2", "12-3", "16-1", "16-6", "18-1", "19-2"]),
    7: (["ep07_panels"], ["13-1", "13-4"]),
}
PANELS = {}
EXTRA = {}
for ep, (mods, keys) in TARGETS.items():
    ms = [importlib.import_module(m) for m in mods]
    spec_n = importlib.util.spec_from_file_location("n", os.path.join(HERE, f"ep{ep:02d}_name.py"))
    name = importlib.util.module_from_spec(spec_n); spec_n.loader.exec_module(name)
    for k in keys:
        p, i = map(int, k.split("-"))
        sp = next(m.PANELS[(p, i)] for m in ms if (p, i) in m.PANELS)
        b = layout.page_panels(name, p)[i - 1]["bbox"]; w, h = best_size(b[2] - b[0], b[3] - b[1])
        j = {**sp, "w": w, "h": h, "seeds": [4, 5, 6], "neg": f"{sp.get('neg', NEG)}, {FIX_NEG}"}
        if ep == 3 and "ip_scale" in j: j["ip_scale"] = 0.25
        EXTRA[f"e{ep}_p{p:02d}_{i}"] = j

# 第1話2ページ: 冒険から帰る4人(装備あり・笑い合う)と、背を向けて笑い合う4人
def hero(who, p, gear=True, scale=0.4):
    g = f", {GEAR[who]}" if gear else ""
    return {**R(who, scale), "seeds": [1, 2], "prompt": f"{LOOK[who]}{g}, {p}, {WB}", "neg": f"{NEG}, {FIX_NEG}", "w": 832, "h": 1216}
for who in ("shiro", "aimi", "ryusei", "tamaki"):
    EXTRA[f"c_{who}_return"] = hero(who, "full body, walking, laughing cheerfully, in high spirits")
    EXTRA[f"c_{who}_laughback"] = hero(who, "full body, from behind, laughing, walking away, looking at a friend beside", gear=False)

# 見本の絵(第6・7話の描き直しで使う)
for nm, look in (("hr", HR), ("staff", STAFF)):
    EXTRA[f"ref_{nm}"] = {"seeds": [1, 2, 3, 4], "prompt": f"{look}, full body, standing, front view, neutral expression, character design, {WB}",
                          "neg": f"{NEG}, {FIX_NEG}", "w": 832, "h": 1216}
