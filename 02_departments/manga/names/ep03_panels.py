# 第3話 コマごとの作画指示(2026-11-24、ネーム第2稿「冒険サークル版」用)。キーは (ページ, コマ番号)。コマ番号はネームの読み順
# - 画面のコマ(4-1, 9-3, 10-2, 11-2, 13-1, 17-2, 18-3)は tools/ui_panels.py で描く(name_checklist B1)
# - 集合ゴマ(1-1, 3-4, 5-1, 6-1, 6-4, 7-4, 8-1, 9-1, 9-4, 12-1, 12-3, 13-4, 14-1, 17-1, 18-1)は、
#   EXTRA の部品(一人ずつ白背景)と背景を tools/group_composite.py で重ねる(B2・B4)
# - 勇者サークルの4人は、冒険の場面では第1話の見た目に武器を足す(format.md の設定)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep02_panels_redo import CFG, REFS, R, NG, SH, IZ, S, I, CLOSED, DSUKE, SW_CHAIR, SW_HANGER
from ep01_panels import SHIRO, ISSHI as AIMI, YASU as RYUSEI, TSUBU as TAMAKI

two = [1, 2]
WB = "simple background, white background"
NEG = f"{NG}, ink splatter, splashes, blood"
GEAR = {"shiro": "holding a sword, adventurer", "aimi": "holding a magic staff", "ryusei": "holding a thick spell book",
        "tamaki": "holding a holy staff"}
LOOK = {"shiro": SHIRO, "aimi": AIMI, "ryusei": RYUSEI, "tamaki": TAMAKI}
DUNGEON = "stone dungeon corridor, dim torchlight"
ROOM = "messy club room, sofa, trophies"

def b(who, prompt, gear=True, scale=0.5, **k):
    """勇者サークルの一人を描く(冒険の場面では武器を持たせる)"""
    g = f", {GEAR[who]}" if gear else ""
    return {"seeds": two, **R(who, scale), "prompt": f"{LOOK[who]}{g}, {prompt}", "neg": NEG, **k}
def extra(prompt, **k): return {"seeds": two, "prompt": prompt, "neg": NEG, **k}

PANELS = {
    # 1ページ 迷宮の入口
    (1, 2): b("shiro", "upper body, resting the sword on his shoulder, smug grin, stone gate in the background, morning, character on the left side"),
    (1, 3): b("aimi", "upper body, raising one hand cheerfully, stone gate in the background, morning"),
    (1, 4): extra("three college students seen from behind, small in frame, looking up at a huge old stone gate in a grassy field, morning, wide shot"),
    # 2ページ シロの宣言
    (2, 1): b("shiro", "cowboy shot, raising a sword high, puffing out his chest, giving a speech, backs of a few students small in the foreground, stone gate, character on the right side", scale=0.45),
    (2, 2): extra("1boy, solo, freshman college student, upper body, sparkling eyes, impressed, casual clothes, outdoors"),
    (2, 3): b("ryusei", "upper body, reading a book, not looking up, indifferent, outdoors", gear=False),
    (2, 4): b("tamaki", "upper body, gentle smile, outdoors"),
    # 3ページ 受付の職員
    (3, 1): extra("1man, solo, middle-aged university staff member with an armband, sitting at a small reception booth beside a stone gate, calling out, upper body"),
    (3, 2): b("shiro", "upper body, shrugging, arrogant, outdoors"),
    (3, 3): extra("1man, solo, middle-aged university staff member with an armband, shaking his head, polite, upper body, outdoors, character on the left side"),
    # 4ページ 当日の申請
    (4, 2): extra("1man, solo, middle-aged university staff member with an armband, reading a sheet of paper, upper body, outdoors"),
    (4, 3): b("shiro", "close-up, face, clicking his tongue, annoyed"),
    (4, 4): extra("1girl, solo, freshman college student, upper body, slightly disappointed, casual clothes, outdoors"),
    (4, 5): extra("no humans, a neat stack of blank paper forms on a reception desk beside a stone gate, close-up"),
    # 5ページ 第1層
    (5, 2): b("aimi", f"upper body, hugging her staff, looking back over her shoulder, {DUNGEON}"),
    (5, 3): b("ryusei", f"upper body, looking away, {DUNGEON}"),
    (5, 4): {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, flashback, at night in a club room, drawing routes and notes on a hand-drawn dungeon map at a desk, a notebook beside him, desk lamp, upper body, character on the right side",
             "neg": f"{NEG}, 2boys, multiple boys"},
    # 6ページ 迷子・空腹
    (6, 2): b("tamaki", f"upper body, hand on cheek, calm smile, {DUNGEON}"),
    (6, 3): b("shiro", f"upper body, annoyed, pointing ahead, {DUNGEON}"),
    (6, 5): b("aimi", f"upper body, holding her stomach, hungry, pouting, {DUNGEON}"),
    (6, 6): b("aimi", f"close-up, face, sudden realization, wide eyes, {DUNGEON}", gear=False),
    # 7ページ 魔物と罠
    (7, 1): extra(f"no humans, a small cute round slime monster with big eyes at the end of a {DUNGEON}, wide shot"),
    (7, 2): b("shiro", f"cowboy shot, charging forward with a sword, dynamic, motion lines, {DUNGEON}, character on the right side"),
    (7, 3): extra("close-up of a boot stepping on a stone floor tile that sinks slightly, dungeon floor, no face"),
    # 8ページ 網の中
    (8, 2): b("ryusei", "upper body, tangled in a sticky white net, sighing, dungeon, character on the left side", gear=False),
    (8, 3): b("tamaki", "upper body, looking into an empty pouch, calm smile, dungeon", gear=False),
    (8, 4): b("shiro", "close-up, face, shouting angrily, tangled in a sticky white net, dungeon", gear=False),
    # 9ページ 夕方の門
    (9, 2): extra("no humans, an empty grassy spot near a huge old stone gate at sunset, lonely, wide shot"),
    # 10ページ 部室でSNS
    (10, 1): b("aimi", f"upper body, wiping her messy sticky hair with a towel, looking at a smartphone, {ROOM}, night, character on the right side", gear=False),
    (10, 3): b("aimi", f"upper body, tilting her head, confused, holding a smartphone, {ROOM}", gear=False),
    (10, 4): b("ryusei", f"upper body, reading a book, answering without looking up, {ROOM}, character on the left side", gear=False),
    (10, 5): b("shiro", "close-up, face, gritting his teeth, frustrated", gear=False),
    # 11ページ シロの自撮り
    (11, 1): b("shiro", f"upper body, taking a selfie with a smartphone, cool pose, messy sticky hair, {ROOM}", gear=False),
    (11, 3): b("shiro", "close-up, face, frozen, staring at a smartphone, sweat drop", gear=False),
    # 12〜13ページ キャンパスの通路
    (12, 2): b("shiro", "upper body, stopping and looking back over his shoulder, surprised, campus walkway", gear=False),
    (13, 2): b("aimi", "upper body, wide eyes, surprised, holding a smartphone, campus walkway", gear=False),
    (13, 3): b("shiro", "upper body, scoffing, smirk, campus walkway, character on the left side", gear=False),
    # 14ページ 責任のなすりつけ合い
    (14, 2): b("aimi", f"upper body, glaring, angry, {ROOM}, night", gear=False),
    (14, 3): b("shiro", f"upper body, arguing back, angry, {ROOM}, night", gear=False),
    (14, 4): b("aimi", f"upper body, pointing to the side, accusing, {ROOM}, night", gear=False),
    (14, 5): b("tamaki", f"upper body, smiling coldly, {ROOM}, night", gear=False),
    (14, 6): b("ryusei", f"upper body, closing a book, bored, {ROOM}, night, character on the left side", gear=False),
    # 15ページ シロの逆上
    (15, 1): b("shiro", "close-up, looking down, eyes shadowed, dark", gear=False),
    (15, 2): b("shiro", f"upper body, standing up and slamming the desk with his fist, furious, focus lines, {ROOM}, night", gear=False),
    (15, 3): b("shiro", f"upper body, ranting, angry, {ROOM}, night, character on the right side", gear=False),
    (15, 4): b("aimi", "upper body, looking away, awkward", gear=False),
    (15, 5): b("tamaki", "upper body, looking away, cold smile", gear=False),
    (15, 6): b("ryusei", "upper body, clicking his tongue, going back to his book", gear=False),
    # 16ページ 窓辺のシロ
    (16, 1): b("shiro", "from behind, standing alone at a window in a dark club room at night, a dark silhouette of a dungeon tower outside the window, wide shot", gear=False),
    (16, 2): b("shiro", "close-up, profile, narrowing his eyes, by a window at night", gear=False),
    (16, 3): b("shiro", "face reflected in a dark window glass at night, irritated, distorted expression", gear=False),
    # 17ページ 1日密着の撮影
    (17, 3): {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, upper body, holding out a microphone, interviewing, smile, campus courtyard, daytime", "neg": NEG},
    (17, 4): extra("1girl, solo, college student, upper body, shy smile, wearing a vintage cardigan, being interviewed, campus courtyard, daytime"),
    (17, 5): {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, upper body, holding out a microphone, from the side, cheerful, campus courtyard, daytime", "neg": NEG},
    (17, 6): extra("1girl, solo, college student, upper body, counting on her fingers, cheerful, wearing a vintage cardigan, campus courtyard, daytime"),
    # 18ページ CAPSの部室と二つの窓
    (18, 2): {"seeds": two, **R("sweater", 0.6), "prompt": f"{SW_CHAIR}, symmetrical face, exactly two round eyes, delighted, close-up, small cozy club room",
              "neg": f"{NEG}, one eye, cyclops, two sweaters, humans"},
    (18, 4): extra("no humans, night, a university club building with one dark gloomy window, exterior, from outside"),
    (18, 5): extra("no humans, night, a university club building with one bright warm lit window, exterior, from outside"),
}

# 集合ゴマの部品(白背景で一人ずつ)と背景
EXTRA = {}
for who in ("shiro", "aimi", "ryusei", "tamaki"):
    EXTRA[f"c_{who}_stand"] = {**b(who, f"full body, standing, confident, {WB}"), "w": 832, "h": 1216}
    EXTRA[f"c_{who}_back"] = {**b(who, f"full body, from behind, standing, shoulders slumped, {WB}"), "w": 832, "h": 1216}
    EXTRA[f"c_{who}_sit"] = {**b(who, f"full body, sitting on the floor leaning back, exhausted, tired, {WB}"), "w": 832, "h": 1216}
    EXTRA[f"c_{who}_net"] = {**b(who, f"full body, tangled in a sticky white net, struggling, {WB}", gear=False), "w": 832, "h": 1216}
    EXTRA[f"c_{who}_walk"] = {**b(who, f"full body, staggering wearily, clothes and hair covered in sticky white goo, {WB}"), "w": 832, "h": 1216}
EXTRA.update({
    "c_shiro_back_c": {**b("shiro", f"full body, from behind, walking away, {WB}", gear=False), "w": 832, "h": 1216},
    "c_aimi_back_c": {**b("aimi", f"full body, from behind, walking away, {WB}", gear=False), "w": 832, "h": 1216},
    "c_fresh_a": {**extra(f"1girl, solo, freshman college student, short bob hair, walking, looking at a smartphone, smiling, casual clothes, full body, {WB}"), "w": 832, "h": 1216},
    "c_fresh_b": {**extra(f"1girl, solo, freshman college student, long hair, walking, talking happily, holding a smartphone, casual clothes, full body, {WB}"), "w": 832, "h": 1216},
    "c_dsuke_mic": {"seeds": two, **R("dsuke", 0.45), "prompt": f"{DSUKE}, full body, holding a microphone, interviewing, smile, {WB}", "neg": NEG, "w": 832, "h": 1216},
    "c_izuru_camera": {"seeds": two, "loras": I, "prompt": f"{IZ}, solo, full body, holding a video camera, filming, {WB}", "neg": f"{NEG}, 2boys", "w": 832, "h": 1216},
    "c_shiina_memo": {"seeds": two, "loras": S, "prompt": f"{SH}, solo, full body, holding a memo pad and a pen, closed mouth smile, {WB}", "neg": f"{NEG}, {CLOSED}", "w": 832, "h": 1216},
    "c_hisa_sweater": {"seeds": two, **R("hisa", 0.5), "prompt": f"1boy, solo, male focus, light brown hair, spiky hair, headphones around neck, bomber jacket, full body, carrying a coat hanger with a knitted sweater that has a face, grin, {WB}", "neg": f"{NEG}, black hair", "w": 832, "h": 1216},
    "bg_gate": {**extra("no humans, a huge old stone gate of a dungeon in a grassy field at the edge of a university campus, a blank wooden signboard beside the gate, a small reception booth, morning, wide shot"), "w": 1216, "h": 832},
    "bg_gate_dusk": {**extra("no humans, a huge old stone gate of a dungeon in a grassy field, sunset, long shadows, wide shot"), "w": 1216, "h": 832},
    "bg_corridor": {**extra(f"no humans, a long {DUNGEON} with branching paths, eye level, wide shot"), "w": 1216, "h": 832},
    "bg_corridor_scar": {**extra(f"no humans, {DUNGEON}, a distinctive scratch mark on the stone wall, eye level, wide shot"), "w": 1216, "h": 832},
    "bg_campus_path": {**extra("no humans, a university campus walkway with trees, daytime, eye level, wide shot"), "w": 1216, "h": 832},
    "bg_courtyard": {**extra("no humans, a university campus courtyard with benches and trees, sunny daytime, eye level, wide shot"), "w": 1216, "h": 832},
})
