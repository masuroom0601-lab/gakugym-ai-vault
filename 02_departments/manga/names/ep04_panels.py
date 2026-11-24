# 第4話 コマごとの作画指示(2026-11-24、ネーム初稿用)。キーは (ページ, コマ番号)。コマ番号はネームの読み順
# - 画面のコマ(1-2, 1-4, 2-4, 4-2, 4-3, 9-2, 12-1, 14-1, 14-5, 15-1)は tools/ui_panels.py で描く(B1)
# - 集合ゴマ(1-1, 3-2, 5-1, 7-3, 11-4, 12-2, 13-5, 15-3)は、EXTRA の部品と背景を names/ep04_group.py で重ねる(B2・B4)
#   第1話・第2話の部品(喜ぶD助・椎菜・さいつよ、イスの背のセーター)と、部室の背景は使い回す
# - シロは第3話の描き直しと同じ見本(背景なしの上半身)を使い、集中線を入れない
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep03_panels_redo import CFG, REFS, R, NG, NEG, WB, LOOK, s as shiro
from ep02_panels_redo import IZ, SH, I, S, CLOSED, DSUKE, SW_CHAIR, HISA

two = [1, 2]
ROOM = "small cozy club room, daytime, detailed background, indoors"
FA = "1boy, solo, male focus, freshman college student, short brown hair, energetic, hoodie"
FB = "1girl, solo, freshman college student, black hair in a low ponytail, glasses, serious, blouse"
FC = "1girl, solo, freshman college student, petite, short bob hair, shy, oversized cardigan"
KB = "1boy, solo, child, elementary school boy, short hair, t-shirt"
KG = "1girl, solo, child, elementary school girl, pigtails, t-shirt"
SAI = "1girl, solo, young woman, long wavy hair in a low side ponytail, droopy eyes, gentle smile, cardigan"

def x(prompt, neg="", **k): return {"seeds": two, "prompt": prompt, "neg": f"{NEG}, {neg}".rstrip(", "), **k}
def iz(prompt): return {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, {prompt}", "neg": f"{NEG}, 2boys, multiple boys, 1girl"}
def sh(prompt): return {"seeds": two, "loras": S, "prompt": f"{SH}, solo, {prompt}", "neg": f"{NEG}, 2girls, {CLOSED}"}
def hisa(prompt): return {"seeds": two, **R("hisa", 0.5), "prompt": f"{HISA}, {prompt}", "neg": f"{NEG}, black hair"}
def dsuke(prompt): return {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, {prompt}", "neg": NEG}
def sai(prompt): return {"seeds": two, **R("sai", 0.45), "prompt": f"{SAI}, {prompt}", "neg": NEG}
def sw(prompt): return {"seeds": two, **R("sweater", 0.6), "prompt": f"{SW_CHAIR}, symmetrical face, exactly two round eyes, {prompt}, small cozy club room, single image",
                        "neg": f"{NEG}, one eye, cyclops, two sweaters, humans, comic panels, multiple views, border"}
def aimi(prompt): return {"seeds": two, **R("aimi", 0.5), "prompt": f"{LOOK['aimi']}, {prompt}", "neg": NEG}
def part(d): return {**d, "w": 832, "h": 1216}
def bg(prompt): return {**x(f"no humans, {prompt}, eye level, wide shot"), "w": 1216, "h": 832}

PANELS = {
    # 1ページ 投稿
    (1, 3): sw("cheerful big smile"),
    (1, 5): iz(f"upper body, calm determined expression, looking ahead, {ROOM}, character on the left side"),
    # 2ページ 広がる動画
    (2, 1): x("1boy, solo, college student, upper body, laughing while looking at a smartphone, university cafeteria, detailed background"),
    (2, 2): x("1girl, solo, college student, upper body, excitedly showing her smartphone screen to the viewer, campus, detailed background, character on the right side"),
    (2, 3): x(f"1girl, solo, freshman college student, short hair, casual clothes, upper body, sitting on a campus bench, looking at a smartphone, murmuring, hopeful, character on the left side"),
    # 3ページ 部室に飛び込むヒサ
    (3, 1): hisa(f"cowboy shot, bursting through a door, holding up a smartphone high, excited, {ROOM}, character on the right side"),
    (3, 3): sw("warm gentle smile, moved"),
    # 4ページ イヅルの気づき
    (4, 1): iz(f"cowboy shot, looking around at friends with a gentle smile, warm, {ROOM}, character on the left side"),
    # 5ページ 新入生
    (5, 2): x(f"{FA}, upper body, nervous smile, scratching his head, standing at a club room door, {ROOM}, character on the right side"),
    (5, 3): x(f"{FA}, upper body, asking a question earnestly, from a different angle, {ROOM}, character on the left side"),
    # 6ページ 逆に聞くけど
    (6, 1): sw("big friendly smile, warm, close-up"),
    (6, 2): x(f"{FA}, upper body, surprised, wide eyes, {ROOM}"),
    (6, 3): x(f"{FB}, upper body, surprised, wide eyes, {ROOM}"),
    (6, 4): x(f"{FC}, upper body, surprised, wide eyes, {ROOM}"),
    # 7ページ 想像を形にする場所
    (7, 1): sw("confident proud smile"),
    (7, 2): sw("extreme close-up of the knitted face, kind smile"),
    # 8ページ やりたいこと
    (8, 1): x(f"{FA}, upper body, raising his hand energetically, excited grin, {ROOM}"),
    (8, 2): x(f"{FB}, upper body, hand on her chest, determined, {ROOM}"),
    (8, 3): x(f"{FC}, upper body, shy, speaking softly, blushing, looking down, {ROOM}, character on the left side"),
    (8, 4): sw("delighted wide smile"),
    (8, 5): iz(f"close-up, face, realization, eyes widening, moved, {ROOM}, character on the right side"),
    # 9ページ ホワイトボード
    (9, 1): dsuke(f"cowboy shot, from behind, writing on a whiteboard with a marker, {ROOM}, character on the right side"),
    # 10ページ フェス
    (10, 1): dsuke("cowboy shot, standing on a concert stage under a spotlight, holding a microphone, hosting, energetic, stage lights, detailed background, character on the right side"),
    (10, 2): x("concert hall audience seen from behind, many glowing penlights swaying in the dark, stage lights, night, wide shot", neg="faces"),
    # 11ページ フェスのダイジェスト
    (11, 1): x(f"{FA}, upper body, holding a clipboard timetable, guiding someone, backstage of a concert hall, busy"),
    (11, 2): hisa("upper body, adjusting knobs on a sound mixing console, focused, concert hall, dim lights"),
    (11, 3): sai("upper body, smiling warmly at a reception desk, event entrance, detailed background"),
    (11, 5): x(f"{FA}, upper body, teary eyes, moved, watching the stage from the wings, backstage, stage lights, character on the left side"),
    # 12ページ 理科実験教室
    (12, 3): iz("cowboy shot, explaining earnestly in front of a whiteboard with a simple static electricity diagram, community hall, character on the right side"),
    (12, 4): x(f"{KB}, upper body, yawning, bored, sitting at a table, community hall"),
    # 13ページ 空飛ぶくらげ
    (13, 1): x(f"{FB}, upper body, cheerfully holding up a thin plastic strip and a tissue, community hall, character on the right side"),
    (13, 2): x(f"{KG}, upper body, looking up in amazement, sparkling eyes, a thin plastic strip shaped like a jellyfish floating in the air above her, community hall, character on the left side"),
    (13, 3): x(f"{KB}, upper body, holding a spring toy telephone to his ear, laughing, community hall"),
    (13, 4): x(f"{KG}, upper body, raising both hands, excited, community hall"),
    # 14ページ CAPSナビ
    (14, 2): iz(f"upper body, typing on a laptop, focused, {ROOM}"),
    (14, 3): sh(f"upper body, drawing on a tablet with a stylus, closed mouth smile, {ROOM}"),
    (14, 4): hisa(f"upper body, testing an app on a smartphone, curious, {ROOM}"),
    (14, 6): x(f"{FC}, upper body, both hands over her mouth, overjoyed, teary, {ROOM}, character on the left side"),
    # 15ページ 想像リスト
    (15, 2): sw("bright smile, looking at the viewer"),
    # 16〜17ページ 勇者サークル
    (16, 1): x("no humans, messy club room, sofa, trophies on a shelf, a robe tossed over a chair, evening, detailed background, wide shot"),
    (16, 2): aimi("cowboy shot, lying on a sofa, watching a video on a smartphone, giggling, messy club room, detailed background, character on the right side"),
    (16, 3): shiro("close-up, face, shouting angrily, messy club room, detailed background, character on the left side"),
    (17, 1): shiro("upper body, putting a smartphone face down on a table, irritated, messy club room, detailed background, character on the right side"),
    (17, 2): shiro("close-up, looking down, gritting his teeth, shadowed eyes, messy club room"),
    (17, 3): x("no humans, an empty cardboard box labeled for club application forms sitting on a small table by a club room entrance, lonely, evening, detailed background", neg="letters"),
}

# 集合ゴマの部品(白背景で一人ずつ)と背景
EXTRA = {
    "c_izuru_look": part(iz(f"full body, leaning forward, looking down at a laptop screen, smile, {WB}")),
    "c_shiina_look": part(sh(f"full body, leaning forward, looking down at something, smile, {WB}")),
    "c_nabe": part(x(f"no humans, japanese donabe clay pot with lid, cute simple face on the pot, steam rising, {WB}")),
    "c_izuru_nod": part(iz(f"upper body, nodding with a smile, looking to the left, {WB}")),
    "c_shiina_nod": part(sh(f"upper body, nodding with a smile, looking to the right, {WB}")),
    "c_izuru_laugh": part(iz(f"upper body, laughing happily, {WB}")),
    "c_sai_laugh": part(sai(f"upper body, laughing happily, {WB}")),
    "c_fb_laugh": part(x(f"{FB}, upper body, laughing happily, {WB}")),
    "c_kidb_sit": part(x(f"{KB}, upper body, sitting, looking forward, {WB}")),
    "c_kidg_sit": part(x(f"{KG}, upper body, sitting, looking forward, {WB}")),
    "c_parent_sit": part(x(f"1woman, solo, mother, casual clothes, upper body, sitting, gentle smile, {WB}")),
    "c_dsuke_raise": part(dsuke(f"full body, raising one hand high, cheerful, {WB}")),
    "bg_caps_door": bg("small cozy club room seen from inside, an open door, daytime"),
    "bg_backstage": bg("backstage of a concert hall, curtains, stage lights glowing from the side, night"),
    "bg_hall_table": bg("community hall room with long tables, bright daytime, summer"),
}
for k, look in (("fa", FA), ("fb", FB), ("fc", FC)):
    EXTRA[f"c_{k}_peek"] = part(x(f"{look}, full body, standing nervously, peeking, shy, {WB}"))
    EXTRA[f"c_{k}_look"] = part(x(f"{look}, upper body, looking to the side, exchanging glances, {WB}"))
    EXTRA[f"c_{k}_raise"] = part(x(f"{look}, full body, raising a hand high, excited, {WB}"))
