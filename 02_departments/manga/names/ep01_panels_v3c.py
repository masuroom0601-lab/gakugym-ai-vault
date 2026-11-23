# 第1話 第3稿・描き直し3回目: 校舎裏のチンピラ2人(合成用。白背景・墨はねなし)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_panels_v3b import CFG, REFS
CFG = dict(CFG); CFG["negative"] += ", ink splatter, splashes, motion lines, speed lines, dynamic background"
PANELS = {}
WB = "full body, standing, plain white background, simple background, clean lineart"
EXTRA = {
    "c_thug_a": {"seeds": [41, 42, 43, 44], "prompt": "1boy, solo, delinquent college student, dyed blond spiky hair, earrings, open shirt over a t-shirt, sneer, hands in pockets, leaning forward, " + WB + ", from side, facing right"},
    "c_thug_b": {"seeds": [41, 42, 43, 44], "prompt": "1boy, solo, tall delinquent college student, dyed hair with shaved sides, chain necklace, jacket, sneer, reaching out one hand, " + WB + ", from side, facing right"},
}
