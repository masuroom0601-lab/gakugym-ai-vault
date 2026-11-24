# 第2話 初版への指摘を受けた描き直し(2026-11-24)
# 画面・通知・数字・コメント欄など文字が中心のコマ(6-2, 11-2の画面, 12-1, 13-2, 14-2, 15-1, 15-2, 17-2)は、
# AIでは崩れるため tools/ui_panels.py で描く。集合ゴマ(16-1, 17-3)は部品の合成をやり直す
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep02_panels import AIMI, CFG, REFS, R, SH, CLOSED, IZ, S, I, SI, DSUKE, SAI, SW_CHAIR, SW_HANGER, ROOM, SPACE

# どのコマにも入れる禁止語(意味のない文字、コマ割りのような絵、何人もの同じ人物)
NG = "text, letters, writing, speech bubble, sound effects, comic panels, multiple views, split screen, watermark"
HISA = "1boy, solo, male focus, light brown hair, spiky hair, short hair, cheerful grin, headphones around neck, bomber jacket"
three = [1, 2, 3]
def iz(prompt, neg="", seeds=three): return {"seeds": seeds, "loras": I, "prompt": f"{IZ}, solo, {prompt}", "neg": f"{NG}, 2boys, multiple boys, 1girl, {neg}"}
def sh(prompt, neg="", seeds=three): return {"seeds": seeds, "loras": S, "prompt": f"{SH}, solo, {prompt}", "neg": f"{NG}, 2girls, {CLOSED}, {neg}"}
def sw(prompt, hanger=False):
    return {"seeds": three, **R("sweater", 0.6), "prompt": f"{SW_HANGER if hanger else SW_CHAIR}, symmetrical face, exactly two round eyes, {prompt}",
            "neg": f"{NG}, one eye, cyclops, single eye, three eyes, extra eyes, two sweaters, humans"}
def hisa(prompt): return {"seeds": three, **R("hisa", 0.5), "prompt": f"{HISA}, {prompt}", "neg": f"{NG}, black hair, dark hair"}

PANELS = {
    # 1-4, 4-3 意味のない文字やコマ割りが混ざっていたので描き直す
    (1, 4): sw(f"smiling, waving a sleeve, {ROOM}, close-up, {SPACE}"),
    (4, 3): {"seeds": three, **R("aimi"), "prompt": f"{AIMI}, upper body, mocking laugh, pointing, club room, dark, flashback, {SPACE}", "neg": NG},
    # 1-2 ドアだと分かるように: 後ろ姿のイヅルが、窓とプレートのついた部室のドアに手をかける
    (1, 2): iz("from behind, standing in front of a closed wooden door, hand on the door knob, the door has a small window and a name plate, school hallway, cowboy shot"),
    # 2-3 二人の間に、イス一つ分くらいの距離をあける
    (2, 3): {"seeds": three, "loras": SI, "prompt": f"{SH}, 1girl 1boy, sitting side by side at a long table with a gap between them, a little apart, "
             f"the boy with black messy hair in a grey hoodie sitting down shyly, the girl smiling at him, {ROOM}, medium shot",
             "neg": f"{NG}, 2girls, hugging, cheek to cheek, touching, close together, {CLOSED}"},
    # 2-4 部屋を見回すイヅルだけを描く(浮いた人物や黒板が出ないように)
    (2, 4): iz(f"upper body, shy smile, blush, looking around, bookshelves in the background, {ROOM}, {SPACE}", "floating, ghost, blackboard, chalkboard"),
    # 6-3, 6-4 イヅルの想像: 不安な新入生と、新歓でにぎわう春のキャンパス
    (6, 3): {"seeds": three, "prompt": "1boy, solo, freshman college student, holding a thick course guide booklet, confused, worried, sweat drop, cherry blossom petals, upper body",
             "neg": f"{NG}, grey hoodie"},
    (6, 4): {"seeds": three, "prompt": "university campus gate in spring, cherry blossom trees, crowd of new students, club recruitment booths with signs, wide shot",
             "neg": NG},
    # 6-5 回想: 1年前、時間割の紙とパソコンの前で頭を抱えるイヅル
    (6, 5): iz(f"younger, sitting at a desk, holding his head with both hands, frustrated, a laptop and scattered timetable papers on the desk, upper body, {SPACE}"),
    # 7-3 縦長のコマに、うなずくイヅル一人(机に突っ伏さない)
    (7, 3): iz("upper body, sitting at a desk with a laptop, nodding, determined smile, looking to the side, evening", "lying on desk, sleeping, head down"),
    # 10-2, 11-1 セーターは目が二つ。一着だけ
    (10, 2): sw(f"speaking calmly, warm eyes, close-up, {ROOM}, {SPACE}"),
    (11, 1): sw(f"cheerful, raising a sleeve, close-up, {ROOM}, {SPACE}", hanger=True),
    # 10-3, 12-2 ヒサ(明るい茶色のツンツン頭)
    (10, 3): hisa(f"upper body, leaning forward, excited, sparkling eyes, {ROOM}, {SPACE}"),
    (12, 2): hisa(f"upper body, awkward forced smile, scratching his cheek, {ROOM}, {SPACE}"),
    # 15-3 ベッドの上で飛び上がるイヅル
    (15, 3): iz("full body, jumping up on a bed in shock, wide eyes, shouting, holding a smartphone in one hand, bedroom, morning sunlight through the window, dynamic pose", "falling, lying"),
    # 17-1 D助が、セーターをかけたハンガーを差し出す(頭まで全部入れる)
    (17, 1): {"seeds": three, **R("dsuke", 0.4), "prompt": f"{DSUKE}, cowboy shot, whole head in frame, holding out a coat hanger with a knitted sweater with a face on it toward the viewer, smile, {ROOM}, {SPACE}",
              "neg": f"{NG}, head out of frame, cropped head"},
    # 18-1 椎菜がイヅル(読者の目線)にハイタッチしに駆け寄る。椎菜一人だけ
    (18, 1): sh(f"cowboy shot, running toward the viewer, raising one hand for a high five, happy, closed mouth smile, {ROOM}, dynamic", "1boy, black hair girl"),
    # 18-4 ステータス表示の後ろの絵: ぼんやりした部室(紙吹雪)
    (18, 4): {"seeds": [1, 2], "prompt": f"blurry {ROOM} interior, bookshelves, confetti, soft light, out of focus, no humans", "neg": NG},
}
EXTRA = {
    # 11-2 震える指(白背景で描いて切り抜き、描いたスマホ画面の上に重ねる)
    "c_finger": {"w": 1024, "h": 1024, "seeds": three, "prompt": "close-up of a single hand, index finger extended pointing down, grey hoodie sleeve, simple white background, white background, no face",
                 "neg": f"{NG}, smartphone, extra fingers"},
}
