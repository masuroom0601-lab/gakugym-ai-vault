# 第1話 コマごとの作画指示(プロンプト)。キーは (ページ, コマ番号)
STYLE = "monochrome, greyscale, manga, comic, screentone, ink, clean ink lines, hatching"
CFG = {
    "style": STYLE, "steps": 28, "cfg": 4.5,
    "loras": ["shiina_lora_v2", "izuru_lora_v1"],
    "negative": ("lowres, bad anatomy, bad hands, worst quality, low quality, shiny skin, glossy, airbrushed, 3d, realistic, "
                 "smooth shading, gradient, bloom, sparkle, photo, text, japanese text, english text, speech bubble, onomatopoeia, "
                 "sound effects, signature, watermark, border, frame, inset, multiple views, comic panels, chibi, cat, animal on head, "
                 "twintails, hairband, large breasts, nsfw"),
}
REFS = {}
S = {"shiina_lora_v2": 0.9}
I = {"izuru_lora_v1": 0.9}
SI = {"shiina_lora_v2": 0.7, "izuru_lora_v1": 0.7}
SH = "shiina_kc, 1girl, long hair, light hair, one side up, black hair ribbon, black choker, white collared shirt, black necktie"
IZ = "izuru_kc, 1boy, male focus, black messy hair, grey hoodie"
PANELS = {
    (17, 1): {"loras": SI, "prompt": f"{SH}, {IZ}, 1boy 1girl, sitting side by side on a bench, campus, evening, girl handing a can of juice to the boy, wide shot, from front"},
    (17, 2): {"loras": S, "prompt": f"{SH}, solo, upper body, gentle smile, sitting on a bench, evening, campus background, looking at viewer"},
    (17, 3): {"loras": I, "prompt": f"{IZ}, solo, upper body, embarrassed shy smile, holding a can of juice, evening, campus background"},
    (18, 1): {"loras": S, "prompt": f"{SH}, solo, upper body, impressed, eyes wide, sitting on a bench, evening"},
    (18, 2): {"loras": I, "prompt": f"{IZ}, solo, upper body, wry smile, scratching cheek, evening, bench"},
    (18, 3): {"loras": I, "prompt": f"{IZ}, solo, close-up, face, looking down, sad, evening"},
    (19, 1): {"loras": S, "prompt": f"{SH}, solo, standing up suddenly from a bench, determined, evening, motion lines"},
    (19, 2): {"loras": S, "prompt": f"{SH}, solo, standing, serious expression, looking at viewer, from below, evening sky, cowboy shot, hand on chest"},
    (19, 3): {"loras": I, "prompt": f"{IZ}, solo, close-up, eyes wide open, surprised, evening"},
}
