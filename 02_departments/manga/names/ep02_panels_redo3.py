# 第2話 第2版への指摘による描き直し(2026-11-24)
# 11-3 は二人を一枚に描くと髪型や位置が崩れるため、別々に白背景で描いて合成する
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep02_panels_redo import CFG, REFS, R, NG, iz, sh, three
WB = "simple background, white background"
PANELS = {
    # 4-4 ひざの上で握りしめる手。血に見える黒い飛び散りを入れない
    (4, 4): {"seeds": three, "prompt": "close-up of a clenched fist resting on a knee, grey hoodie sleeve, jeans, clean lines, simple shading, tense",
             "neg": f"{NG}, blood, ink splatter, splashes, stains, wound, dark liquid"},
}
EXTRA = {
    "c_shiina_lean": {**sh(f"upper body, leaning forward to the right, extending her index finger downward, gentle closed mouth smile, slight blush, {WB}"), "w": 832, "h": 1216},
    "c_izuru_phone": {**iz(f"upper body, short messy black hair, holding a smartphone with both hands in front of his chest, blushing, flustered, looking to the left, {WB}", "long hair, ponytail"), "w": 832, "h": 1216},
}
