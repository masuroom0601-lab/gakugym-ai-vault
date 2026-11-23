# 第2話 コマごとの作画指示。キーは (ページ, コマ番号)。コマ番号はネームの読み順(重ねゴマは最後)
# 集合ゴマ(1-3, 8-1, 16-1, 17-3, 20-3)は、EXTRA の部品と第1話の部品を tools/group_composite.py で合成する
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_panels_v3b import CFG, REFS, R
from ep01_panels import SHIRO, ISSHI as AIMI, YASU as RYUSEI, TSUBU as TAMAKI
CFG = dict(CFG)
REFS = dict(REFS); REFS.update({"ryusei": REFS["yasu"], "tamaki": REFS["tsubu"]})
SH = ("shiina_kc, 1girl, long hair, platinum blonde hair, white hair, one side up, black hair ribbon, black choker, "
      "white collared shirt, black necktie")
CLOSED = "fang, skin fang, black hair, brown hair, dark hair, open mouth, teeth"
IZ = "izuru_kc, 1boy, male focus, black messy hair, grey hoodie"
S = {"shiina_lora_v2": 0.85}; I = {"izuru_lora_v1": 0.9}; SI = {"shiina_lora_v2": 0.7, "izuru_lora_v1": 0.55}
DSUKE = "1boy, solo, male focus, small round sunglasses, spiky light hair, plain t-shirt, open jacket"
SAI = ("1girl, solo, young woman, light brown hair, long hair, wavy hair ends, ahoge, small red flower hair ornament, "
       "gentle smile, cream knit cardigan, white blouse")
HISA = "1boy, solo, male focus, short hair, cheerful grin, headphones around neck, bomber jacket"
SW_CHAIR = "no humans, a knitted sweater hanging on the back of a chair, the sweater has a face on its chest, two eyes and a mouth knitted into it"
SW_HANGER = "no humans, a knitted sweater on a coat hanger, the sweater has a face on its chest, two eyes and a mouth knitted into it"
NABE = "no humans, japanese donabe clay pot with a lid on a table, the pot has two big round eyes and a small mouth below the lid, steam"
HANIWA = "no humans, haniwa clay figure on a table, round hollow eyes and mouth, short arms, simple"
SPACE = "character on the left side of the frame, empty space on the right side"
ROOM = "small cozy club room"
two = [1, 2]
def sh(prompt, **k): return {"seeds": two, "loras": S, "prompt": f"{SH}, solo, {prompt}", "neg": CLOSED, **k}
def iz(prompt, **k): return {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, {prompt}", **k}
def sw(prompt, hanger=False, **k): return {"seeds": two, **R("sweater", 0.55), "prompt": f"{SW_HANGER if hanger else SW_CHAIR}, {prompt}", **k}
PANELS = {
    (1, 1): iz(f"cowboy shot, standing in front of a door, holding a laptop, taking a deep breath, corridor, {SPACE}"),
    (1, 2): {"seeds": two, "prompt": "close-up of a hand on a door knob, no face, corridor"},
    (1, 4): sw(f"smiling, waving a sleeve, {ROOM}, close-up, {SPACE}"),
    (1, 5): {"seeds": two, **R("sai4", 0.5), "prompt": f"{SAI}, upper body, pouring tea, looking back over her shoulder, smile, {ROOM}, {SPACE}"},
    (1, 6): {"seeds": two, **R("nabe2", 0.6), "prompt": f"{NABE}, close-up, happy, {ROOM}, {SPACE}"},
    (2, 1): sh(f"cowboy shot, sitting at a desk by the window, looking up, happy surprised, closed mouth smile, {ROOM}, simple background", breakout=None),
    (2, 2): {"seeds": two, "loras": {"shiina_lora_v2": 0.5}, "prompt": "close-up of a girl's hand patting an empty chair seat, white shirt sleeve, no face"},
    (2, 3): {"seeds": two, "loras": SI, "prompt": f"{SH}, 1girl 1boy, sitting side by side at a desk, the boy with black messy hair in a grey hoodie sitting down, the girl smiling, {ROOM}", "neg": "2girls, " + CLOSED},
    (2, 4): iz(f"upper body, shy smile, looking around the room, {ROOM}, {SPACE}"),
    (3, 1): {"seeds": two, **R("dsuke", 0.35), "prompt": f"{DSUKE}, hanging a knitted sweater with a face on a coat hanger next to a whiteboard, whiteboard with writing, {ROOM}, wide shot, {SPACE}"},
    (3, 2): {"seeds": two, **R("hisa", 0.5), "prompt": f"{HISA}, upper body, wry smile, scratching his head, {ROOM}, {SPACE}"},
    (3, 3): {"seeds": two, **R("sai4", 0.5), "prompt": f"{SAI}, upper body, hand on cheek, troubled smile, {ROOM}, {SPACE}"},
    (3, 4): sw(f"eyes sparkling, determined, close-up, {SPACE}", hanger=True),
    (3, 5): iz(f"upper body, sitting up straight, startled, {ROOM}, {SPACE}"),
    (3, 6): sw(f"earnest, close-up, {SPACE}", hanger=True),
    (3, 7): iz("close-up, face, stiff, nervous, sweat drop"),
    (4, 1): iz("extreme close-up, eyes, dark, trembling pupils"),
    (4, 2): {"seeds": two, **R("shiro"), "prompt": f"{SHIRO}, throwing a document into a trash can without looking, contempt, club room, dark, flashback, {SPACE}"},
    (4, 3): {"seeds": two, **R("aimi"), "prompt": f"{AIMI}, upper body, mocking laugh, pointing, club room, dark, flashback, {SPACE}"},
    (4, 4): {"seeds": two, "prompt": "close-up of a trembling hand clenched on a knee, grey hoodie sleeve, dark"},
    (4, 5): iz(f"upper body, looking down, shadowed eyes, gloomy, {SPACE}"),
    (5, 1): sh(f"upper body, leaning in, looking at viewer, gentle closed mouth smile, reassuring, {ROOM}, {SPACE}"),
    (5, 2): iz(f"upper body, looking up, surprised, {ROOM}"),
    (5, 3): sh(f"upper body, warm closed mouth smile, {ROOM}"),
    (5, 4): iz("cowboy shot, clenching a fist, raising his head, determined, simple background, " + SPACE),
    (6, 1): iz(f"close-up, eyes closed, thinking hard, {SPACE}"),
    (6, 2): {"seeds": two, "prompt": "smartphone screen showing a social media post with illustrations, sketchy rough lines, imagination, no humans"},
    (6, 3): {"seeds": two, "prompt": "1girl, solo, worried freshman college student, close-up, sketchy rough lines, imagination"},
    (6, 4): {"seeds": two, "prompt": "university campus in spring, cherry blossoms, no humans, sketchy rough lines, imagination"},
    (6, 5): iz("younger, holding his head in confusion in front of a laptop with a messy timetable on the screen, flashback, upper body, " + SPACE),
    (6, 6): iz(f"cowboy shot, opening his eyes, turning to speak, determined smile, {ROOM}, {SPACE}"),
    (7, 1): iz(f"working on a laptop at a desk, evening light through the window, {ROOM}, wide shot"),
    (7, 2): sh(f"upper body, leaning in to look at a laptop screen, delighted, closed mouth smile, {ROOM}, {SPACE}"),
    (7, 3): iz(f"upper body, nodding, smile, {ROOM}"),
    (7, 4): {"seeds": two, "prompt": "close-up of a laptop screen showing a cute hand-drawn infographic design with simple diagrams, no humans"},
    (8, 2): iz("cowboy shot, holding a laptop out toward viewer, eyes tightly shut, nervous, sweat, simple background, " + SPACE),
    (9, 1): {"seeds": two, "prompt": f"{ROOM} at night, silent, still, no humans, wide shot"},
    (9, 2): iz("close-up, slowly opening one eye, nervous"),
    (9, 3): sw(f"teary eyes, trembling, close-up, {SPACE}"),
    (9, 4): sw("crying tears of joy, shouting with mouth wide open, sleeves raised, dramatic, close-up, speed lines"),
    (10, 1): {"seeds": two, **R("dsuke", 0.35), "prompt": f"{DSUKE}, pointing at a laptop screen, a knitted sweater with a face hanging on a chair beside him talking passionately, {ROOM}, {SPACE}"},
    (10, 2): sw(f"speaking calmly, warm eyes, close-up, {SPACE}"),
    (10, 3): {"seeds": two, **R("hisa", 0.5), "prompt": f"{HISA}, upper body, leaning forward, excited, {ROOM}, {SPACE}"},
    (10, 4): {"seeds": two, **R("haniwa", 0.55), "prompt": f"{HANIWA}, raising one short arm, nodding, close-up, {SPACE}"},
    (10, 5): iz("close-up, eyes, tears welling up, moved"),
    (11, 1): sw(f"cheerful, raising a sleeve, close-up, {SPACE}", hanger=True),
    (11, 2): {"seeds": two, "prompt": "close-up of a trembling finger hovering over a smartphone screen post button, no face"},
    (11, 3): {"seeds": two, "loras": SI, "prompt": f"{SH}, 1girl 1boy, the girl gently placing her index finger on the boy's finger on a smartphone, faces close, the boy with black messy hair in a grey hoodie blushing, {ROOM}, {SPACE}", "neg": "2girls, " + CLOSED},
    (12, 1): {"seeds": two, "prompt": "close-up of a smartphone screen showing a social media post with zero likes, no humans"},
    (12, 2): {"seeds": two, **R("hisa", 0.5), "prompt": f"{HISA}, upper body, awkward forced smile, {ROOM}"},
    (12, 3): {"seeds": two, "loras": SI, "prompt": f"{SH}, 1girl 1boy, walking side by side on a campus path at night, street lights, the boy with black messy hair in a grey hoodie, from behind, wide shot, {SPACE}", "neg": "2girls, " + CLOSED},
    (12, 4): sh("upper body, soft closed mouth smile, night, street light"),
    (13, 1): iz("sitting at a desk in a small apartment room at night, desk lamp, wide shot, " + SPACE),
    (13, 2): {"seeds": two, "prompt": "close-up of a smartphone on a desk showing zero likes, night, no humans"},
    (13, 3): {"seeds": two, "prompt": "close-up of a hand writing a numbered list of ideas in a notebook with a pen, desk lamp, night"},
    (13, 4): iz("upper body, holding a pen, looking ahead with determination, night, desk lamp, simple background, " + SPACE),
    (14, 1): iz(f"waking up in bed in the morning, sunlight, small apartment room, wide shot, {SPACE}"),
    (14, 2): {"seeds": two, "prompt": "close-up of a smartphone screen full of notifications, morning light, no humans"},
    (14, 3): iz(f"upper body, sleepy, messy bed hair, morning, {SPACE}"),
    (14, 4): iz(f"close-up, staring at a smartphone, eyes wide open, shocked, {SPACE}"),
    (15, 1): {"seeds": two, "prompt": "close-up of a smartphone screen showing rapidly increasing view counts and graphs, no humans"},
    (15, 2): {"seeds": two, "prompt": "close-up of a smartphone screen showing many comments under a post, no humans"},
    (15, 3): iz("jumping up on a bed in surprise, shouting, holding a smartphone, dynamic pose, morning, simple background"),
    (16, 2): {"seeds": two, **R("hisa", 0.5), "prompt": f"{HISA}, upper body, holding up a smartphone, excited grin, {ROOM}, {SPACE}"},
    (16, 3): {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, upper body, smirk, holding a smartphone, {ROOM}, {SPACE}"},
    (16, 4): {"seeds": two, **R("sai4", 0.5), "prompt": f"{SAI}, upper body, showing a laptop screen, happy, {ROOM}, {SPACE}"},
    (17, 1): {"seeds": two, **R("dsuke", 0.35), "loras": {"izuru_lora_v1": 0.55}, "prompt": f"{DSUKE}, holding up a coat hanger with a knitted sweater with a face on it, in front of a boy with black messy hair in a grey hoodie, {ROOM}, {SPACE}"},
    (17, 2): {"seeds": two, "prompt": "close-up of a smartphone screen showing a popular social media post with many likes, no humans"},
    (17 ,4): iz("close-up, face, deeply moved, teary smile"),
    (18, 1): {"seeds": two, "loras": SI, "prompt": f"{SH}, 1girl 1boy, high five, the girl running up happily, the boy with black messy hair in a grey hoodie, {ROOM}, dynamic, simple background", "neg": "2girls, " + CLOSED},
    (18, 2): {"seeds": two, **R("hisa", 0.5), "prompt": f"{HISA}, upper body, excited, fist pump, {ROOM}, {SPACE}"},
    (18, 3): {"seeds": two, **R("haniwa", 0.55), "prompt": f"{HANIWA}, clapping its short arms, happy, close-up"},
    (19, 1): {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, sitting up from a sofa, grin, {ROOM}, {SPACE}"},
    (19, 2): sw(f"excited, sparkling eyes, close-up, {SPACE}", hanger=True),
    (19, 3): iz(f"upper body, murmuring, thinking, {ROOM}, {SPACE}"),
    (19, 4): iz("upper body, eyes shining with excitement, smile, rough storyboard sketches floating around him, simple background"),
    (20, 1): {"seeds": two, "prompt": "dark messy club room, a blank document on a table, no humans, evening, gloomy, wide shot"},
    (20, 2): {"seeds": two, **R("shiro"), "prompt": f"{SHIRO}, upper body, irritated, scowling, dark club room, {SPACE}"},
    (20, 4): {"seeds": two, "prompt": "close-up of a blank planning document on a table, dark window in the background, no humans, gloomy"},
}
for v in PANELS.values(): v.pop("breakout", None)
# 集合ゴマの部品(第1話の部品 c_dsuke_look など も使う)
WB = "full body, standing, simple background, white background"
EXTRA = {
    "bg_room_night": {"w": 1216, "h": 832, "prompt": f"empty {ROOM} at night, no humans, bookshelves, a long table, chairs, ceiling light on, eye level, wide shot"},
    "bg_room_day": {"w": 1216, "h": 832, "prompt": f"empty {ROOM}, daytime, no humans, bookshelves, a sofa, a long table, window, eye level, wide shot"},
    "bg_brave_room": {"w": 1216, "h": 832, "prompt": "empty dark luxurious club room, no humans, sofa, trophies, evening, gloomy, eye level, wide shot"},
    "c_izuru_burst": {"loras": I, "prompt": f"{IZ}, solo, {WB}, running, out of breath, holding a smartphone, from front"},
    "c_shiina_phone": {"loras": S, "prompt": f"{SH}, solo, {WB}, holding a smartphone, happy, closed mouth smile, black skirt", "neg": CLOSED},
    "c_dsuke_phone": {**R("dsuke", 0.45), "prompt": f"{DSUKE}, {WB}, holding a smartphone, grin"},
    "c_sai_phone": {**R("sai4", 0.45), "prompt": f"{SAI}, long skirt, {WB}, holding a smartphone, happy"},
    "c_hisa_phone": {**R("hisa", 0.45), "prompt": f"{HISA}, {WB}, raising a smartphone, excited"},
    "c_aimi_away": {**R("aimi", 0.5), "prompt": f"{AIMI}, {WB}, looking away, sulking"},
    "c_ryusei_away": {**R("ryusei", 0.5), "prompt": f"{RYUSEI}, {WB}, looking away, arms crossed"},
    "c_tamaki_away": {**R("tamaki", 0.5), "prompt": f"{TAMAKI}, {WB}, looking away, cold expression"},
}
