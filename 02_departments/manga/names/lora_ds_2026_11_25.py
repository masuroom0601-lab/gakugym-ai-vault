# さいつよ・ヒサ・D助のLoRA用の学習データと、勇者サークル4人の普段着の見本の絵(2026-11-25)
# - さいつよは、第4〜7話で古い見た目(黒髪寄り・サイドポニー)の指定が混ざっていた。第1話の決定(format.md)の見た目にそろえる
# - 白背景・全身/上半身・いろいろな表情と向き。墨の飛び散りと描き文字を強く禁止する(学習で覚えさせないため)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ep05_panels import CFG, REFS, R, NEG, LOOK
from ep01_panels_v3 import SAI, DSUKE
from ep02_panels_redo import HISA

CLEAN = ("ink splatter, ink stains, ink drips, black blots, splashes, paint splatter, speed lines, motion lines, "
         "black brush strokes, text, letters, kanji, onomatopoeia, sound effects, speech bubble, comic panels, multiple views")
WB = "simple background, white background"
CHAR = {
    "sai": (SAI, "sai4", 0.5),
    "hisa": (HISA, "hisa", 0.5),
    "dsuke": (DSUKE, "dsuke", 0.45),
}
POSES = [
    "full body, standing, front view, smile, looking at viewer",
    "full body, standing, three quarter view, gentle smile",
    "full body, walking, from side",
    "upper body, front view, smile, looking at viewer",
    "upper body, three quarter view, laughing, open mouth",
    "upper body, from side, looking ahead, calm",
    "upper body, surprised, open mouth",
    "upper body, thinking, hand on chin",
    "upper body, sad, looking down",
    "portrait, face close-up, smile",
    "cowboy shot, waving one hand, cheerful",
    "full body, sitting on a chair, relaxed",
]
PANELS = {}
EXTRA = {}
for who, (look, ref, sc) in CHAR.items():
    for i, p in enumerate(POSES, 1):
        h = 1216 if "full body" in p or "cowboy" in p else 1024
        w = 832 if h == 1216 else 1024
        EXTRA[f"ds_{who}_{i:02d}"] = {**R(ref, sc), "seeds": [11, 12, 13], "w": w, "h": h,
                                      "prompt": f"{look}, {p}, {WB}", "neg": f"{NEG}, {CLEAN}"}

# 勇者サークル4人の普段着(キャンパス・面接の場面用)。髪型と顔は見本の絵から、服だけ変える
CASUAL = {
    "shiro": "1boy, solo, male focus, handsome, blond hair swept back, arrogant smirk, white shirt, black slacks, silver necklace",
    "aimi": "1girl, solo, petite, light hair, twintails, mischievous grin, oversized pastel hoodie, short skirt, no hat",
    "ryusei": "1boy, solo, male focus, glasses, straight black hair, expressionless, plain dark sweater, slacks",
    "tamaki": "1girl, solo, long straight black hair, calm smile, long white cardigan, long skirt, cross necklace",
}
for who, look in CASUAL.items():
    EXTRA[f"casual_{who}"] = {**R(who, 0.35), "seeds": [1, 2, 3, 4], "w": 832, "h": 1216,
                              "prompt": f"{look}, college student, casual clothes, full body, standing, front view, {WB}",
                              "neg": f"{NEG}, {CLEAN}, armor, cape, sword, staff, weapon, witch hat, robe, fantasy costume, gold trim"}
