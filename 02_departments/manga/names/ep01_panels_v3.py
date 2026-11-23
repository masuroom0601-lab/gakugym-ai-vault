# 第1話 第3稿(33ページ)で新しく描くコマの作画指示。キーは第3稿の (ページ, コマ番号)
# 使い回すコマは ep01_reuse_v3.py。共通の設定と見本は ep01_panels.py から読み込む
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_panels import CFG, REFS, IZ, SHIRO, ISSHI as AIMI, HISA, THUG, EV, R
CFG = dict(CFG)
REFS = dict(REFS)
REFS.update({"aimi": REFS["isshi"], "sai4": "characters/designs_v4/sai_bust_s1.jpg",
             "sweater": "characters/designs_v4/sweater_s1.jpg", "nabe2": "characters/designs_v4/nabe_s1.jpg"})
# 椎菜: 髪の色をそろえ、八重歯をなくす
SH = ("shiina_kc, 1girl, long hair, platinum blonde hair, white hair, one side up, black hair ribbon, black choker, "
      "white collared shirt, black necktie")
SHNEG = "fang, skin fang, black hair, brown hair, dark hair"
S = {"shiina_lora_v2": 0.9}; I = {"izuru_lora_v1": 0.9}; SI = {"shiina_lora_v2": 0.7, "izuru_lora_v1": 0.55}
DSUKE = "1boy, solo, male focus, small round sunglasses, spiky light hair, plain t-shirt, open jacket"
SAI = ("1girl, solo, young woman, light brown hair, long hair, wavy hair ends, ahoge, small red flower hair ornament, "
       "gentle smile, cream knit cardigan, white blouse")
SWEATER = "no humans, a knitted sweater hanging on the back of a chair, the sweater has a face on its chest, two eyes and a mouth knitted into it"
NABE = "no humans, japanese donabe clay pot with a lid on a table, the pot has two big round eyes and a small mouth below the lid, steam"
HANIWA = "no humans, haniwa clay figure on a table, round hollow eyes and mouth, raising one short arm, simple"
SPACE = "character on the left side of the frame, empty space on the right side"
two = [21, 22]; four = [21, 22, 23, 24]
PANELS = {
    # 1ページ: ガクチカの説明
    (1, 1): {"seeds": two, "prompt": "university campus in spring, cherry blossoms, many college students walking, wide shot, from above, lively, " + SPACE},
    (1, 2): {"seeds": two, "prompt": "1girl, solo, college student working part-time at a cafe, apron, carrying a tray, upper body, smile"},
    (1, 3): {"seeds": two, "prompt": "1boy, solo, college student playing an electric guitar, club room, upper body"},
    (1, 4): {"seeds": two, "prompt": "1girl, solo, college student pulling a suitcase at an airport, upper body, smile"},
    (1, 5): {"seeds": two, "prompt": "1boy, solo, college student in a lab coat holding a test tube, laboratory, upper body"},
    # 3〜8ページ: 追放
    (3, 1): {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, close-up, profile, lonely faint smile, evening light"},
    (6, 2): {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, writing many ideas on a whiteboard full of notes, club room, night, from behind"},
    (6, 3): {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, handing documents at a university office reception counter, bowing slightly, daytime"},
    (7, 3): {"seeds": two, **R("shiro"), "prompt": f"{SHIRO}, upper body, looking away, annoyed, disgusted, club room, " + SPACE},
    (7, 4): {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, upper body, speechless, shocked, trembling, club room"},
    (8, 2): {"seeds": two, **R("aimi"), "prompt": f"{AIMI}, upper body, dangling a key on her finger, mocking grin, club room, " + SPACE},
    # 12〜15ページ: 救出
    (12, 1): {"seeds": four, "loras": {"shiina_lora_v2": 0.8}, "prompt": f"{SH}, 1girl 2boys, two delinquent college boys with dyed hair and earrings standing in front of the girl, "
              "the girl backed against a wall, both boys clearly visible, behind a school building, evening, wide shot", "neg": "2girls, " + SHNEG},
    (13, 4): {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, shouting for help with hands around mouth, sketchy rough lines, imagination"},
    (15, 1): {"seeds": four, "loras": {"izuru_lora_v1": 0.7}, "prompt": f"{IZ}, 2boys, a delinquent boy with dyed hair grabbing the boy in the grey hoodie by the collar with one hand, "
              "pulling him close, fist clenched on the hood, face to face, threatening, behind a school building, evening, cowboy shot", "neg": "girl, 3boys"},
    # 椎菜のコマ(髪の色・八重歯の修正)
    (17, 3): {"seeds": two, "loras": SI, "prompt": f"{SH}, 1girl 1boy, standing in a quiet alley behind a school building, the boy with black messy hair in a grey hoodie, full body, evening, wide shot", "neg": "2girls, " + SHNEG},
    (19, 1): {"seeds": two, "loras": SI, "prompt": f"{SH}, 1girl 1boy, sitting side by side on a campus bench, the girl handing a can of juice to the boy with black messy hair in a grey hoodie, evening, wide shot", "neg": "2girls, " + SHNEG},
    (21, 1): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, standing up suddenly from a bench, determined, evening, cowboy shot, " + SPACE, "neg": SHNEG},
    (22, 2): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, bright smile, closed mouth, upper body, evening", "neg": SHNEG + ", open mouth"},
    (23, 2): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, upper body, leaning forward, asking, smile, evening, " + SPACE, "neg": SHNEG},
    (23, 3): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, upper body, cheerful smile, evening, " + SPACE, "neg": SHNEG},
    (24, 1): {"seeds": two, "loras": SI, "prompt": f"{SH}, 1girl 1boy, the girl running ahead pulling the hand of the boy with black messy hair in a grey hoodie, sunset campus, full body, wide shot", "neg": "2girls, " + SHNEG},
    (25, 1): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, opening a door energetically, cheerful smile, cowboy shot, " + SPACE, "neg": SHNEG},
    (29, 1): {"seeds": two, "loras": {"shiina_lora_v2": 0.75}, "prompt": f"{SH}, small club room, the girl explaining with gestures, a boy with small round sunglasses and a boy with headphones listening, cowboy shot", "neg": "2girls, crowd, " + SHNEG},
    (32, 3): {"seeds": two, "loras": S, "prompt": f"{SH}, solo, upper body, happy smile, pinching a grey hoodie sleeve, club room, " + SPACE, "neg": SHNEG},
    # CAPSの部室(セーターは服だけ・鍋さんに目・新しいさいつよ)
    (25, 2): {"seeds": four, **R("sweater", 0.2), "prompt": "small cozy club room, wide shot, a boy with small round sunglasses, a young woman with light brown long hair and a red flower hair ornament, a boy with headphones around his neck, "
              "a knitted sweater with a face hanging on a chair, a clay pot with eyes and a haniwa figure on the table, all looking at viewer", "neg": "crowd, 5 people"},
    (26, 1): {"seeds": two, **R("dsuke", 0.4), "prompt": f"{DSUKE}, upper body, friendly grin, club room, " + SPACE},
    (26, 2): {"seeds": four, **R("sweater", 0.55), "prompt": f"{SWEATER}, the face opening its eyes wide, speaking, cheerful, club room, close-up, " + SPACE},
    (26, 4): {"seeds": two, **R("dsuke", 0.4), "prompt": f"{DSUKE}, upper body, pointing with his thumb at a sweater hanging on a chair, grin, club room"},
    (27, 1): {"seeds": four, **R("nabe2", 0.55), "prompt": f"{NABE}, the lid rattling, friendly, club room, close-up, " + SPACE},
    (27, 2): {"seeds": two, **R("haniwa", 0.5), "prompt": f"{HANIWA}, club room, close-up, " + SPACE},
    (28, 1): {"seeds": four, **R("sai4", 0.5), "prompt": f"{SAI}, upper body, offering a cup of tea, kind smile, club room, " + SPACE},
    (28, 2): {"seeds": four, **R("sai4", 0.4), "loras": {"izuru_lora_v1": 0.6}, "prompt": f"{SAI}, 1girl 1boy, the young woman gently patting the head of a boy with black messy hair in a grey hoodie, the boy looking down, club room", "neg": "2girls"},
    (29, 2): {"seeds": two, **R("sweater", 0.55), "prompt": f"{SWEATER}, thinking, serious expression, club room, close-up, " + SPACE},
    (29, 3): {"seeds": two, **R("sweater", 0.55), "prompt": f"{SWEATER}, extreme close-up of the face on the sweater, serious eyes, " + SPACE},
    (30, 2): {"seeds": four, "prompt": "small club room, wide shot, surprised faces, a boy with small round sunglasses, a young woman with light brown long hair, a boy with headphones, a knitted sweater with a face on a chair, a clay pot with eyes on the table, shocked", "neg": "crowd, 5 people"},
    (30, 5): {"seeds": two, **R("dsuke", 0.4), "prompt": f"{DSUKE}, upper body, explaining passionately, club room, " + SPACE},
    (31, 1): {"seeds": two, **R("sweater", 0.55), "prompt": "no humans, a knitted sweater with a face on its chest hanging on a coat hanger held up by a hand, looking straight at viewer, earnest, club room, " + SPACE},
    (31, 2): {"seeds": two, "prompt": "small club room, pov, a boy with small round sunglasses, a young woman with light brown long hair, a boy with headphones, a girl with long platinum blonde hair and black ribbon, all smiling warmly at viewer, a knitted sweater with a face on a chair", "neg": "crowd"},
    (32, 2): {"seeds": four, "loras": {"shiina_lora_v2": 0.6}, "prompt": f"{SH}, small club room, everyone welcoming, cheering with raised arms, a boy with small round sunglasses, a young woman with light brown long hair, a boy with headphones, "
              "a knitted sweater with a face on a chair, a clay pot with eyes and a haniwa figure on the table, wide shot, festive", "neg": "crowd, " + SHNEG},
}
