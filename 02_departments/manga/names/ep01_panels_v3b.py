# 第1話 第3稿・描き直し2回目。椎菜の八重歯対策(口を閉じる)、反応の小ゴマ、集合ゴマの合成用の部品
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_panels_v3 import CFG, REFS, SH, SHNEG, S, I, IZ, DSUKE, SAI, HISA, SWEATER, SPACE, R
REFS = dict(REFS); REFS["thug"] = "characters/designs_v4/thug_ref.jpg"
CFG = dict(CFG); CFG["negative"] += ", ink splatter, splashes"
CLOSED = SHNEG + ", open mouth, teeth"
two = [31, 32]
WB = "full body, standing, simple background, white background"
PANELS = {
    (1, 3): {"seeds": two, "prompt": "1boy, solo, college student playing an acoustic guitar, sitting, smile, upper body, simple background"},
    (1, 5): {"seeds": two, "prompt": "1girl, solo, college student in a white lab coat and safety glasses, looking at a test tube, upper body, simple background"},
    (13, 4): {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, shouting with both hands around his mouth, upper body, simple background, sketchy rough lines"},
    (23, 2): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, upper body, leaning forward, curious, closed mouth, smile, evening, " + SPACE, "neg": CLOSED},
    (23, 3): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, upper body, bright smile, closed mouth, evening, " + SPACE, "neg": CLOSED},
    (25, 1): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, opening a door, cheerful, closed mouth smile, cowboy shot, " + SPACE, "neg": CLOSED},
    (32, 3): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, upper body, happy, closed mouth smile, pinching a grey hoodie sleeve, club room, " + SPACE, "neg": CLOSED},
    (30, 2): {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, upper body, shocked, surprised, open mouth, club room"},
    (30, 3): {"seeds": two, **R("sai4", 0.45), "prompt": f"{SAI}, upper body, surprised, hand over mouth, club room"},
    (30, 4): {"seeds": two, **R("hisa", 0.45), "prompt": f"{HISA}, upper body, shocked, surprised, club room"},
    (30, 5): {"seeds": two, **R("sweater", 0.55), "prompt": f"{SWEATER}, the face with wide surprised eyes and open mouth, close-up"},
    (31, 2): {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, upper body, warm smile, looking at viewer, club room"},
    (31, 3): {"seeds": two, **R("sai4", 0.45), "prompt": f"{SAI}, upper body, warm smile, looking at viewer, club room"},
    (31, 4): {"seeds": two, **R("hisa", 0.45), "prompt": f"{HISA}, upper body, big grin, looking at viewer, club room"},
    (31, 5): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, upper body, warm smile, closed mouth, looking at viewer, club room", "neg": CLOSED},
}
# 集合ゴマは、背景と一人ずつ描いたキャラを重ねて作る(tools/group_composite.py)
EXTRA = {
    "bg_clubroom": {"w": 1216, "h": 832, "prompt": "empty small cozy club room, no humans, bookshelves, a long table, chairs, posters on the wall, eye level, wide shot"},
    "bg_alley": {"w": 1216, "h": 832, "prompt": "behind a school building, narrow alley, concrete wall, pipes, no humans, evening, eye level, wide shot"},
    "c_dsuke_look": {**R("dsuke", 0.45), "prompt": f"{DSUKE}, {WB}, looking at viewer, friendly grin"},
    "c_dsuke_cheer": {**R("dsuke", 0.45), "prompt": f"{DSUKE}, {WB}, cheering with both arms raised, big smile"},
    "c_sai_look": {**R("sai4", 0.45), "prompt": f"{SAI}, long skirt, {WB}, looking at viewer, gentle smile"},
    "c_sai_cheer": {**R("sai4", 0.45), "prompt": f"{SAI}, long skirt, {WB}, clapping hands, happy smile"},
    "c_hisa_look": {**R("hisa", 0.45), "prompt": f"{HISA}, {WB}, looking at viewer, grin"},
    "c_hisa_cheer": {**R("hisa", 0.45), "prompt": f"{HISA}, {WB}, cheering with one fist raised, big grin"},
    "c_shiina_cheer": {"loras": S, "prompt": f"{SH}, solo, {WB}, cheering with both arms raised, closed mouth smile, black skirt", "neg": CLOSED},
    "c_shiina_wall": {"loras": S, "prompt": f"{SH}, solo, {WB}, back against a wall, scared but glaring, hands clutching a bag strap, black skirt, from side, facing left", "neg": SHNEG},
    "c_thug_a": {**R("thug", 0.5), "prompt": "1boy, solo, delinquent college student, dyed spiky hair, earrings, open shirt, sneer, leaning forward, hand in pocket, " + WB + ", from side, facing right"},
    "c_thug_b": {**R("thug", 0.35), "prompt": "1boy, solo, delinquent college student, shaved sides, dyed hair, chain necklace, tank top under jacket, sneer, reaching out one hand, " + WB + ", from side, facing right"},
    "c_sweater_chair": {**R("sweater", 0.55), "w": 1024, "h": 1024, "prompt": "no humans, a knitted sweater hanging on the back of a wooden chair, the sweater has a face on its chest, two eyes and a smiling mouth, full view, simple background, white background"},
}
