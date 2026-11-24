# 第2話 描き直しの2回目(2026-11-24)。1回目で直らなかったコマ
# 2-3 は二人を別々に白背景で描き、間をあけて合成する。7-3 は縦長だとコマ割りが出るので、少し横に広い形で描いて切り抜く
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep02_panels_redo import CFG, REFS, R, NG, iz, sh, DSUKE, ROOM, SPACE, CLOSED, three
WB = "simple background, white background"
PANELS = {
    (7, 3): {**iz("upper body, sitting at a desk with a laptop, nodding, determined smile, looking to the side, evening", "lying on desk, sleeping, head down"), "w": 832, "h": 1216},
    (17, 1): {"seeds": three, **R("dsuke", 0.4), "prompt": f"{DSUKE}, upper body, face, smile, holding up a coat hanger with a knitted sweater with a face on it next to his face, {ROOM}, {SPACE}",
              "neg": f"{NG}, head out of frame, cropped head, close-up of torso"},
}
EXTRA = {
    "c_shiina_sit": {**sh(f"sitting on a chair, upper body, turning to the right, happy, closed mouth smile, {WB}"), "w": 832, "h": 1216},
    "c_izuru_sit": {**iz(f"sitting on a chair, upper body, turning to the left, shy smile, blush, {WB}"), "w": 832, "h": 1216},
}
