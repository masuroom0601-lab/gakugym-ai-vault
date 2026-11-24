# 第3話 初版の描き直し(2026-11-24)
# - シロの見本の絵(designs_v2_ink/shiro_s1.jpg)の背景に墨の集中線が入っていて、シロのコマがすべて集中線の背景になった。
#   見本を上半身だけに切り出し、まわりを白く塗った shiro_crop.jpg に替える。見本の効きも少し弱め、集中線を禁止する
# - 網の罠(7-4, 8-1)の網は、AIに描かせず tools/ui_panels.py 側でなく合成のときに線で描き足す(ep03_group.py)
# - 9-1 の夕方の門は、疲れてネバネバの4人を描き直して合成する
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep03_panels import CFG, REFS, R, NG, NEG, WB, DUNGEON, ROOM, SW_CHAIR, LOOK, GEAR, extra

REFS = {**REFS, "shiro": "characters/designs_v2_ink/shiro_crop.jpg"}
three = [1, 2, 3]
NO_FX = "speed lines, motion lines, focus lines, abstract background, black brush strokes, ink smudges, flying debris, explosion"
NEG_S = f"{NEG}, {NO_FX}"

def s(prompt, gear=False, scale=0.4, fx=False):
    """シロ。場所が分かる背景を描かせ、集中線は入れない(fx=True のときだけ集中線を許す)"""
    g = f", {GEAR['shiro']}" if gear else ""
    neg = f"{NEG}, abstract background, black brush strokes, ink smudges" if fx else NEG_S
    return {"seeds": three, **R("shiro", scale), "prompt": f"{LOOK['shiro']}{g}, {prompt}", "neg": neg}
def x(prompt, **k): return {**extra(prompt, **k), "seeds": three}

GATE = "detailed background, grassy field, huge old stone gate, morning"
NIGHT_ROOM = f"detailed background, {ROOM}, night, indoors"
PANELS = {
    (1, 2): s(f"upper body, resting the sword on his shoulder, smug grin, {GATE}, character on the left side", gear=True),
    (2, 1): s(f"cowboy shot, raising a sword high, puffing out his chest, giving a speech, {GATE}, character on the right side", gear=True),
    (3, 1): x("1man, solo, middle-aged japanese man, university staff, armband on his sleeve, sitting inside a small plain reception booth, calling out, upper body, outdoors, stone gate in the background",
              neg=f"{NEG}, signboard, sign, label, kanji"),
    (3, 2): s(f"upper body, shrugging, arrogant, {GATE}"),
    (4, 2): x("1man, solo, middle-aged japanese man, university staff, armband on his sleeve, holding a sheet of paper with both hands and reading it, upper body, outdoors, stone gate in the background"),
    (4, 3): s(f"close-up, face, clicking his tongue, annoyed, {GATE}"),
    (6, 3): s(f"upper body, annoyed, pointing ahead, detailed background, {DUNGEON}", gear=True),
    (7, 2): s(f"cowboy shot, charging forward with a sword, detailed background, {DUNGEON}, character on the right side", gear=True),
    (8, 4): s(f"close-up, face, shouting angrily, white sticky threads of a net over his hair and face, detailed background, {DUNGEON}"),
    (10, 1): {"seeds": three, **R("aimi", 0.5), "prompt": f"{LOOK['aimi']}, upper body, wiping her messy hair with a towel, looking at a smartphone, {NIGHT_ROOM}, character on the right side",
              "neg": f"{NEG}, signboard, poster, calligraphy, kanji"},
    (10, 5): s(f"close-up, face, gritting his teeth, frustrated, {NIGHT_ROOM}"),
    (11, 1): s(f"upper body, holding up a smartphone to take a selfie, cool pose, messy sticky hair, {NIGHT_ROOM}"),
    (11, 3): s(f"close-up, face, frozen, staring at a smartphone, sweat drop, {NIGHT_ROOM}"),
    (12, 2): s("upper body, stopping and looking back over his shoulder, surprised, detailed background, university campus walkway with trees, daytime"),
    (13, 3): s("upper body, scoffing, smirk, detailed background, university campus walkway with trees, daytime, character on the left side"),
    (14, 3): s(f"upper body, arguing back, angry, {NIGHT_ROOM}"),
    (15, 1): s(f"close-up, looking down, eyes shadowed, gloomy, {NIGHT_ROOM}"),
    (15, 2): s(f"upper body, standing up and slamming the desk with his fist, furious, focus lines, {NIGHT_ROOM}", fx=True),
    (15, 3): s(f"upper body, ranting, angry, {NIGHT_ROOM}, character on the right side"),
    (16, 1): s("from behind, standing alone at a large window in a dark club room at night, a dark silhouette of a stone tower far outside the window, moonlight, wide shot, detailed background, indoors"),
    (16, 2): s("close-up, profile, narrowing his eyes, standing by a window at night, dark room, moonlight, indoors"),
    (16, 3): s("his face reflected in a dark window glass at night, irritated, distorted expression, window frame, indoors"),
    (18, 2): {"seeds": three, **R("sweater", 0.6), "prompt": f"{SW_CHAIR}, symmetrical face, exactly two round eyes, delighted, close-up, small cozy club room, single image",
              "neg": f"{NEG}, one eye, cyclops, two sweaters, humans, comic panels, multiple views, border"},
}

EXTRA = {}
for pose in ("stand", "back", "sit", "walk"):
    p = {"stand": "full body, standing, confident", "back": "full body, from behind, standing, shoulders slumped",
         "sit": "full body, sitting on the floor leaning back, exhausted", "walk": "full body, walking"}[pose]
    EXTRA[f"c_shiro_{pose}"] = {**s(f"{p}, {WB}", gear=pose != "walk", scale=0.35), "w": 832, "h": 1216}
EXTRA["c_shiro_back_c"] = {**s(f"full body, from behind, walking away, {WB}", scale=0.35), "w": 832, "h": 1216}
TIRED = "full body, exhausted, hunched over, dragging his feet, messy hair, white sticky slime dripping from hair and clothes"
for who in ("shiro", "aimi", "ryusei", "tamaki"):
    t = TIRED.replace("his", "her") if who in ("aimi", "tamaki") else TIRED
    if who == "shiro":
        EXTRA["c_shiro_tired"] = {**s(f"{t}, {WB}", gear=True, scale=0.35), "w": 832, "h": 1216}
    else:
        ref = who
        EXTRA[f"c_{who}_tired"] = {"seeds": three, **R(ref, 0.5), "prompt": f"{LOOK[who]}, {GEAR[who]}, {t}, {WB}", "neg": NEG, "w": 832, "h": 1216}
