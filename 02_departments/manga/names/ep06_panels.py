# 第6話 コマごとの作画指示(2026-11-24、ネーム初稿用)。キーは (ページ, コマ番号)。コマ番号はネームの読み順
# - 集合ゴマ(1-1, 2-2, 3-3, 7-1, 15-1, 17-1, 17-2, 22-1)は names/ep06_group.py で重ねる
# - 勇者サークルの4人は、キャンパスではふだんの服(武器なし)。シロは第3話の描き直しと同じ見本で、集中線を入れない
# - 新しい人物: キャリアセンターの職員(落ち着いた女性)/企業の人事(スーツの男性)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep03_panels_redo import CFG, REFS, R, NG, NEG, WB, LOOK, s as shiro
from ep04_panels import x, iz, sh, part, bg
from ep05_panels import b, ry, ta, ai

OUT = "in front of a modern university career center building, campus, daytime, detailed background"
ROOMI = "small interview room with a desk, office, daytime, detailed background, indoors"
FB_ = "flashback, soft focus, messy club room"
STAFF = "1woman, solo, calm university career center staff member, short neat hair, cardigan, lanyard"
HR = "1man, solo, male focus, corporate recruiter, business suit, name badge, neat short hair"
def st(p): return x(f"{STAFF}, {p}")
def hr(p): return x(f"{HR}, {p}")
def sitting(p): return f"sitting on a chair, {p}, {ROOMI}"

PANELS = {
    (1, 2): sh(f"upper body, holding a stack of flyers, happy, {OUT}, character on the right side"),
    (1, 3): iz(f"upper body, holding a stack of flyers, smiling, {OUT}, character on the left side"),
    (2, 1): iz(f"upper body, looking back over his shoulder, startled, {OUT}, character on the right side"),
    (2, 3): x(f"no humans, a single paper flyer fluttering down to the pavement, {OUT}"),
    (2, 4): iz(f"close-up, face, wide eyes, shocked, {OUT}"),
    (3, 1): shiro(f"cowboy shot, approaching with a smirk, {OUT}, character on the right side"),
    (3, 2): iz(f"upper body, turning away, avoiding eye contact, {OUT}, character on the left side"),
    (4, 1): shiro(f"upper body, condescending smile, looking down, {OUT}, character on the right side"),
    (4, 2): shiro(f"close-up of his mouth and chin, fake smile, {OUT}"),
    (4, 3): ai(f"upper body, arms crossed, mocking grin, {OUT}, character on the left side"),
    (4, 4): iz(f"upper body, looking down, shoulders trembling, holding back anger, {OUT}"),
    (5, 1): shiro(f"cowboy shot, pointing at himself with his thumb, arrogant, {OUT}, character on the right side"),
    (5, 2): shiro(f"upper body, matter-of-fact, arrogant, {OUT}, character on the left side"),
    (5, 3): ta(f"upper body, hands together in front of her chest, sweet smile, {OUT}, character on the right side"),
    (6, 1): iz(f"extreme close-up of his eyes, trembling pupils, {OUT}"),
    (6, 2): ai(f"{FB_}, upper body, pointing and laughing mockingly"),
    (6, 3): ry(f"{FB_}, upper body, reading a book, not looking up, cold"),
    (6, 4): shiro(f"{FB_}, upper body, coldly declaring, cruel, detailed background"),
    (6, 5): iz(f"upper body, gritting his teeth, frustrated, {OUT}, character on the left side"),
    (7, 2): ai(f"upper body, frowning, annoyed, {OUT}, character on the right side"),
    (7, 3): shiro(f"upper body, scoffing, {OUT}, character on the left side"),
    (8, 1): sh(f"upper body, staring straight ahead, firm, serious, {OUT}, character on the right side"),
    (8, 2): sh(f"close-up, face, strong determined eyes, serious, {OUT}"),
    (8, 3): sh(f"upper body, firm, serious, not backing down, {OUT}, character on the left side"),
    (9, 1): shiro(f"upper body, shrugging, dismissive, {OUT}, character on the right side"),
    (9, 2): sh(f"upper body, shaking her head, serious, {OUT}, character on the left side"),
    (9, 3): ry(f"upper body, pushing up his glasses, cold, {OUT}"),
    (9, 4): ta(f"upper body, smiling with cold eyes, {OUT}"),
    (10, 1): shiro(f"close-up, face, smile disappearing, cold, {OUT}"),
    (10, 2): shiro(f"upper body, shouting furiously, enraged, {OUT}"),
    (11, 1): shiro(f"upper body, flicking a paper flyer with his finger, contempt, {OUT}, character on the right side"),
    (11, 2): shiro(f"upper body, sneering, looking down, {OUT}, character on the left side"),
    (11, 3): ai(f"upper body, laughing loudly, holding her stomach, {OUT}, character on the right side"),
    (12, 1): iz(f"close-up, face looking down, eyes shadowed, quiet anger, {OUT}"),
    (12, 2): shiro(f"upper body, raising an eyebrow, {OUT}"),
    (12, 3): iz(f"upper body, glaring straight ahead, serious anger, determined, intense eyes, {OUT}"),
    (13, 1): shiro(f"upper body, flinching then twisted grin, {OUT}, character on the right side"),
    (13, 2): x("no humans, a modern university career center building seen from below, blank signboard above the entrance, daytime, detailed background", neg="letters"),
    (13, 3): shiro(f"cowboy shot, pointing forward, challenging, {OUT}, character on the left side"),
    (13, 4): iz(f"upper body, surprised, {OUT}, character on the right side"),
    (14, 1): shiro(f"upper body, declaring conditions, arrogant, {OUT}, character on the right side"),
    (14, 2): sh(f"upper body, firm expression, {OUT}"),
    (14, 3): shiro(f"upper body, scoffing, confident, {OUT}"),
    (14, 4): iz(f"upper body, anxious, uncertain, {OUT}, character on the left side"),
    (14, 5): sh(f"upper body, gently holding someone's sleeve, small nod, encouraging, {OUT}"),
    (14, 6): iz(f"close-up, face, resolved, determined, {OUT}"),
    (15, 2): x("close-up of six people's shoes walking toward a building entrance, pavement, no faces", neg="faces"),
    (16, 1): st("upper body, leaning out from a reception counter, calm, university office, detailed background, character on the right side"),
    (16, 2): hr("cowboy shot, peeking out from a meeting space, friendly smile, office, detailed background, character on the left side"),
    (16, 3): st("upper body, gentle smile, university office, detailed background, character on the right side"),
    (17, 3): iz(sitting("upper body, sitting up straight, nervous")),
    (17, 4): sh(sitting("upper body, sitting in the corner, hands clasped on her lap, worried")),
    (18, 1): hr(sitting("upper body, friendly, starting an interview, character on the right side")),
    (18, 2): shiro(sitting("cowboy shot, puffing out his chest, confident, character on the left side")),
    (18, 3): hr(sitting("upper body, nodding and taking notes, character on the right side")),
    (19, 1): hr(sitting("upper body, calm, asking a question, character on the right side")),
    (19, 2): shiro(sitting("close-up, face, forced smile, twitching")),
    (19, 3): shiro(sitting("upper body, eyes darting, flustered, character on the left side")),
    (19, 4): hr(sitting("upper body, pen stopped, listening")),
    (19, 5): shiro(sitting("close-up, face, frozen, sweat drop")),
    (20, 1): st(sitting("upper body, looking at documents")),
    (20, 2): ai(sitting("upper body, raising her hand cheerfully")),
    (20, 3): ai(sitting("upper body, proud, talking, character on the left side")),
    (20, 4): st(sitting("upper body, listening quietly, character on the right side")),
    (20, 5): ai(sitting("upper body, at a loss for words, awkward")),
    (20, 6): st(sitting("upper body, tilting her head, asking")),
    (20, 7): ai(sitting("close-up, face, eyes darting nervously, sweat")),
    (21, 1): ta(sitting("upper body, elegant smile, answering, character on the left side")),
    (21, 2): hr(sitting("upper body, calm, asking, character on the right side")),
    (21, 3): ta(sitting("close-up, face, smile slightly freezing")),
    (21, 4): ry(sitting("upper body, answering flatly, character on the left side")),
    (21, 5): st(sitting("upper body, asking calmly")),
    (21, 6): ry(sitting("close-up, face, silent, eyes darting behind glasses")),
    (22, 2): hr(sitting("upper body, looking down at notes, thinking, serious, character on the right side")),
    (22, 3): shiro(sitting("close-up, gritting his teeth, glaring sideways")),
    (23, 1): iz(sitting("upper body, hands on his knees, shoulders trembling slightly, nervous")),
    (23, 2): sh(sitting("upper body, hands clasped in front of her chest, praying, character on the left side")),
    (23, 3): iz(sitting("upper body, glancing to the side")),
    (23, 4): sh(sitting("upper body, small fist pump, encouraging smile")),
    (23, 5): iz(sitting("upper body, calm, relaxed, confident, character on the right side")),
    (24, 1): hr(sitting("upper body, looking up, character on the right side")),
    (24, 2): iz(sitting("upper body, looking straight ahead, determined, clear eyes")),
}

EXTRA = {
    "c_izuru_flyer": part(iz(f"full body, walking, holding a stack of flyers, smiling, {WB}")),
    "c_shiina_flyer": part(sh(f"full body, walking, holding a stack of flyers, happy, {WB}")),
    "c_shiro_wave": part(shiro(f"full body, standing, raising one hand casually, smirk, {WB}", scale=0.35)),
    "c_shiro_reach": part(shiro(f"full body, reaching out one arm forward, smirk, {WB}", scale=0.35)),
    "c_izuru_away": part(iz(f"full body, from behind, walking away, {WB}")),
    "c_shiina_step": part(sh(f"full body, stepping forward, arms at her sides, serious, {WB}")),
    "c_izuru_stand": part(iz(f"full body, standing, serious, {WB}")),
    "c_shiina_stand": part(sh(f"full body, standing, serious, {WB}")),
    "c_shiro_cross": part(shiro(f"full body, standing, arms crossed, arrogant, {WB}", scale=0.35)),
    "c_hr_sit": part(hr(f"upper body, sitting at a desk, {WB}")),
    "c_staff_sit": part(st(f"upper body, sitting at a desk, {WB}")),
    "c_hr_note": part(hr(f"upper body, sitting, looking down at notes, serious, {WB}")),
    "c_staff_note": part(st(f"upper body, sitting, looking down at notes, serious, {WB}")),
    "c_shiro_seat": part(shiro(f"upper body, sitting on a chair, confident, {WB}", scale=0.35)),
    "bg_career": bg("in front of a modern university career center building, campus, daytime"),
    "bg_interview": bg("small interview room with a desk and chairs, office, daytime"),
}
for who in ("aimi", "ryusei", "tamaki"):
    EXTRA[f"c_{who}_casual"] = part(b(who, f"full body, standing, arrogant, {WB}"))
    EXTRA[f"c_{who}_seat"] = part(b(who, f"upper body, sitting on a chair, {WB}"))
