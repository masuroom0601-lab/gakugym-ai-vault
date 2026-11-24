# 第5話 コマごとの作画指示(2026-11-24、ネーム初稿用)。キーは (ページ, コマ番号)。コマ番号はネームの読み順
# - 画面のコマ(6-2 手を重ねる, 7-3 ネタ帳, 7-4 撮影メモ, 11-4 公式SNS, 12-2 手描きの地図, 16-2〜16-5 話題の作品, 19-1 OBのメッセージ)は tools/ui_panels.py で描く(B1・B5)
# - 集合ゴマ(1-1, 4-1, 10-1, 12-1, 12-6, 13-1, 18-5, 20-2)は names/ep05_group.py で重ねる。第1〜4話の部品と背景を使い回す
# - シロは第3話の描き直しと同じ見本(背景なしの上半身)を使い、集中線を入れない
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep03_panels_redo import CFG, REFS, R, NG, NEG, WB, LOOK, GEAR, s as shiro
from ep04_panels import FA, FB, SAI, x, iz, sh, hisa, dsuke, sai, sw, part, bg

two = [1, 2]
ROOM_N = "small cozy club room, night, warm light, detailed background, indoors"
BRAVE = "messy club room, sofa, trophies, night, detailed background, indoors"
DUNGEON = "dark stone dungeon corridor, dim torchlight, detailed background"
FLASH = "flashback, soft focus"
def b(who, prompt, gear=False):
    g = f", {GEAR[who]}" if gear else ""
    return {"seeds": two, **R(who, 0.5), "prompt": f"{LOOK[who]}{g}, {prompt}", "neg": NEG}
def ry(p): return b("ryusei", p)
def ta(p, gear=False): return b("tamaki", p, gear)
def ai(p, gear=False): return b("aimi", p, gear)

PANELS = {
    # 1〜3ページ 歓迎会
    (1, 2): hisa(f"upper body, raising a paper cup, cheerful, {ROOM_N}, character on the right side"),
    (1, 3): sai(f"upper body, gentle smile, {ROOM_N}, character on the left side"),
    (2, 1): x(f"{FA}, upper body, leaning forward, curious question, {ROOM_N}, character on the right side"),
    (2, 2): iz(f"upper body, awkward smile, {ROOM_N}, character on the left side"),
    (2, 3): x(f"{FA}, upper body, shocked, {ROOM_N}"),
    (2, 4): x(f"{FB}, upper body, shocked, {ROOM_N}"),
    (2, 5): hisa(f"upper body, angry, raising a fist, {ROOM_N}"),
    (2, 6): iz(f"upper body, scratching his head, laughing, {ROOM_N}"),
    (3, 1): iz(f"upper body, looking down at a paper cup in his hands, quiet, thoughtful, {ROOM_N}, character on the left side"),
    (3, 2): iz(f"close-up of his eyes, looking up, resolved, {ROOM_N}"),
    (3, 3): iz(f"upper body, speaking quietly, serious, {ROOM_N}, character on the right side"),
    (3, 4): sh(f"upper body, gentle expression, looking at someone, {ROOM_N}, character on the left side"),
    # 4〜5ページ 回想(1年前)
    (4, 2): iz(f"{FLASH}, upper body, younger, sparkling eyes, looking up in admiration, outdoors, grassy field, morning, character on the right side"),
    (4, 3): iz(f"{FLASH}, upper body, holding out a paper form with both hands, nervous smile, messy club room"),
    (4, 4): shiro(f"{FLASH}, upper body, lounging on a sofa, smug grin, messy club room, detailed background"),
    (5, 1): iz(f"{FLASH}, upper body, at night, drawing on a hand-drawn dungeon map at a desk, desk lamp"),
    (5, 2): iz(f"{FLASH}, upper body, handing papers over a university office counter"),
    (5, 3): iz(f"{FLASH}, upper body, posting a photo with a smartphone, smiling"),
    (5, 4): iz(f"{FLASH}, cowboy shot, from behind, writing ideas on a whiteboard"),
    (5, 5): ry(f"{FLASH}, upper body, reading a book, not looking up, cold, {BRAVE}, character on the left side"),
    (5, 6): shiro(f"{FLASH}, upper body, looking down coldly, contempt, {BRAVE}, character on the right side"),
    # 6〜9ページ 打ち明け
    (6, 1): iz(f"upper body, troubled smile, self-deprecating, {ROOM_N}, character on the right side"),
    (6, 3): iz(f"close-up, face, wide eyes, surprised, slight blush, {ROOM_N}, character on the left side"),
    (7, 1): sh(f"upper body, looking straight at someone, earnest, {ROOM_N}, character on the right side"),
    (7, 2): iz(f"{FLASH}, upper body, thinking hard in a back alley at night, determined"),
    (7, 5): sh(f"upper body, warm gentle smile, {ROOM_N}, character on the left side"),
    (8, 1): sh(f"upper body, serious, earnest, leaning forward, {ROOM_N}, character on the right side"),
    (8, 2): sai(f"upper body, kind smile, {ROOM_N}, character on the left side"),
    (8, 3): sw("strong encouraging smile"),
    (8, 4): iz(f"close-up, face, teary eyes, moved, {ROOM_N}, character on the right side"),
    (9, 1): iz(f"upper body, shy smile, blushing, {ROOM_N}, character on the left side"),
    (9, 2): sai(f"cowboy shot, clapping her hands once, cheerful, {ROOM_N}, character on the right side"),
    (9, 3): x(f"{FA}, upper body, raising his hand energetically, grin, {ROOM_N}, character on the left side"),
    (10, 2): x("no humans, university campus at night, one club room window glowing warmly, exterior, wide shot"),
    # 11ページ 落ちぶれる勇者サークル
    (11, 1): x(f"no humans, {BRAVE}, a blank paper poster half peeling off the wall, wide shot"),
    (11, 2): shiro("upper body, frowning, being handed back a document at a university office counter, detailed background"),
    (11, 3): x("no humans, an empty grassy area in front of a huge old stone gate, nobody there, lonely, daytime, wide shot"),
    (11, 5): x("no humans, an empty cardboard box on a small table by a club room entrance, lonely, evening, detailed background", neg="letters"),
    (11, 6): x("no humans, university campus at night, one dark gloomy club room window, exterior, wide shot"),
    # 12ページ 迷宮で立ち往生
    (12, 3): ai(f"upper body, staring at a crumpled hand-drawn map, confused, {DUNGEON}", gear=True),
    (12, 4): ta(f"upper body, shaking an empty potion bottle, calm smile, {DUNGEON}"),
    (12, 5): shiro(f"upper body, turning his back, annoyed, {DUNGEON}", gear=True),
    # 13〜15ページ 作戦会議
    (13, 2): shiro(f"upper body, sitting on a sofa with legs crossed, irritated, {BRAVE}, character on the right side"),
    (13, 3): ai(f"upper body, scratching her cheek, looking away, {BRAVE}"),
    (13, 4): ta(f"upper body, smiling calmly, hands together, {BRAVE}"),
    (14, 1): shiro(f"upper body, raising his voice, frustrated, {BRAVE}, character on the left side"),
    (14, 2): ry(f"upper body, looking up from a book, cold, {BRAVE}, character on the right side"),
    (14, 3): iz(f"{FLASH}, upper body, turning around with a bright smile in front of a whiteboard full of notes, messy club room, character on the right side"),
    (14, 4): shiro(f"{FLASH}, upper body, looking at a smartphone, waving a hand dismissively, {BRAVE}, character on the left side"),
    (15, 1): ry(f"upper body, closing a book, matter-of-fact, {BRAVE}, character on the left side"),
    (15, 2): ry(f"upper body, pushing up his glasses, {BRAVE}, character on the right side"),
    (15, 3): shiro(f"close-up, silent, eyes shadowed, {BRAVE}"),
    # 16〜18ページ 話題の作品はイヅルのもの
    (16, 1): ai(f"upper body, lying on a sofa, looking at a smartphone, surprised, {BRAVE}, character on the right side"),
    (16, 6): ai(f"upper body, looking up from a smartphone, serious, {BRAVE}, character on the left side"),
    (17, 1): ta(f"upper body, hand on cheek, smiling calmly, {BRAVE}, character on the right side"),
    (17, 2): shiro(f"upper body, snatching a smartphone and glaring at the screen, {BRAVE}, character on the left side"),
    (17, 3): shiro("extreme close-up of his eyes lit by a smartphone screen, shocked, dark room"),
    (18, 1): ai(f"upper body, angry, pointing, accusing, {BRAVE}, character on the right side"),
    (18, 2): shiro(f"upper body, shouting back, angry, {BRAVE}, character on the left side"),
    (18, 3): ta(f"upper body, smiling coldly, {BRAVE}"),
    (18, 4): ry(f"upper body, reading a book, cold remark, {BRAVE}"),
    # 19〜22ページ シロの決意
    (19, 2): shiro(f"upper body, slamming a smartphone down on a table, furious, {BRAVE}"),
    (19, 3): shiro(f"close-up, face, gritting his teeth, rage, {BRAVE}"),
    (20, 1): shiro(f"cowboy shot, sitting slumped on a sofa, holding his head in his hands, {BRAVE}, character on the right side"),
    (20, 3): shiro(f"close-up, face, wide eyes, realization, {BRAVE}"),
    (20, 4): shiro(f"close-up, face, looking up, cold calculating eyes, sly, {BRAVE}, character on the left side"),
    (21, 1): shiro(f"cowboy shot, standing up, declaring, arrogant, {BRAVE}, character on the right side"),
    (21, 2): shiro(f"close-up, face, determined, scheming, {BRAVE}"),
    (21, 3): ai(f"upper body, shocked, exasperated, {BRAVE}"),
    (21, 4): ta(f"upper body, calm smile, slightly sinister, {BRAVE}"),
    (21, 5): ry(f"upper body, closing a book, cold, {BRAVE}, character on the left side"),
    (22, 1): shiro("cowboy shot, from behind, standing at a window in a dark club room at night, a lit window of another building far across the campus, detailed background, indoors"),
    (22, 2): shiro("his face reflected in a dark window glass at night, twisted grin, window frame, indoors"),
    (22, 3): x("no humans, dark night sky over a university campus, a black silhouette of a stone dungeon tower in the distance, ominous, wide shot"),
}

EXTRA = {
    "c_fa_party": part(x(f"{FA}, full body, holding a paper cup, laughing, {WB}")),
    "c_fb_party": part(x(f"{FB}, full body, holding a paper cup, smiling, {WB}")),
    "c_shiro_sofa": part(shiro(f"full body, sitting on a sofa with legs crossed, arrogant, {WB}", scale=0.35)),
    "c_shiro_victory": part(shiro(f"full body, raising a sword in victory, shouting with joy, {WB}", gear=True, scale=0.35)),
    "c_aimi_victory": part(b("aimi", f"full body, raising a magic staff in victory, cheering, {WB}", gear=True)),
    "c_izuru_luggage": part(iz(f"full body, carrying a huge backpack and a rolled map, smiling, {WB}")),
    "c_shiro_argue": part(shiro(f"full body, shouting angrily, pointing, {WB}", scale=0.35)),
    "bg_brave_night": bg("messy club room, sofa, trophies on a shelf, night, dim light"),
}
for who in ("aimi", "ryusei", "tamaki"):
    EXTRA[f"c_{who}_room"] = part(b(who, f"full body, standing, {WB}"))
    EXTRA[f"c_{who}_argue"] = part(b(who, f"full body, arguing, annoyed, {WB}"))
