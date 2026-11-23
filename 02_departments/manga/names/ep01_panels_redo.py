# 第1話 描き直し(1回目): 複数人のコマで人数やキャラが崩れたもの
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ep01_panels import CFG, REFS, SH, IZ, SHIRO, DSUKE, SAI, THUG, R
CFG = dict(CFG); CFG["negative"] = CFG["negative"] + ", crowd, many people"
SI = {"shiina_lora_v2": 0.75, "izuru_lora_v1": 0.55}
PANELS = {
    (3, 3): {"seeds": [11, 12, 13, 14], "prompt": "3 people, 2girls 1boy, standing side by side in a club room, petite girl with twintails and witch hat, tall boy with glasses holding a book, girl with long straight black hair and white cardigan, smirking, evening, cowboy shot", "neg": "4 people, 2boys"},
    (10, 1): {"seeds": [11, 12, 13, 14], "loras": {"shiina_lora_v2": 0.85}, "prompt": f"{SH}, 1girl 2boys, two delinquent boys with dyed hair cornering the girl against a wall, behind a school building, girl scared but glaring, evening, wide shot", "neg": "2girls"},
    (13, 1): {"seeds": [11, 12, 13, 14], "loras": {"izuru_lora_v1": 0.7}, "prompt": f"{IZ}, 2boys, a delinquent boy with dyed hair grabbing the collar of the boy in the grey hoodie, threatening, behind a school building, evening, cowboy shot", "neg": "girl, 3boys"},
    (16, 3): {"seeds": [11, 12, 13, 14], "loras": SI, "prompt": f"{SH}, 1girl 1boy, hetero, the girl holding the boy's hand with both hands, worried, faces close, the boy with black messy hair in a grey hoodie blushing, evening", "neg": "2girls, yuri"},
    (23, 2): {"seeds": [11, 12, 13, 14], **R("dsuke", 0.25), "prompt": "small club room, 3 people and 2 objects, a boy with small round sunglasses in a knit sweater, a young woman with long wavy hair, a boy with headphones around his neck, a clay pot and a haniwa figure on the table, all looking at viewer, wide shot", "neg": "4 people, 5 people"},
    (26, 2): {"seeds": [11, 12, 13, 14], **R("sai", 0.35), "loras": {"izuru_lora_v1": 0.6}, "prompt": f"{SAI}, 1girl 1boy, the young woman gently patting the head of a boy with black messy hair in a grey hoodie, the boy looking down, club room", "neg": "2girls"},
    (27, 1): {"seeds": [11, 12, 13, 14], "loras": {"shiina_lora_v2": 0.7}, "prompt": f"{SH}, small club room, 4 people, the girl explaining, a boy with small round sunglasses, a young woman with wavy hair, a boy with headphones listening, cowboy shot", "neg": "6 people"},
    (28, 2): {"seeds": [11, 12, 13, 14], "prompt": "small club room, 3 people and 2 objects, surprised faces, a boy with small round sunglasses in a knit sweater, a young woman with wavy hair, a boy with headphones, a clay pot and a haniwa on the table, shocked, wide shot", "neg": "4 people, 5 people"},
}
