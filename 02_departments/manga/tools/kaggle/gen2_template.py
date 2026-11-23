# Kaggle上で実行: コマ画像の生成(Animagine XL 4.0 + キャラ専用LoRA + 見本画像IP-Adapter)
import base64, glob, io, json, os, subprocess, sys, time, traceback
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/progress.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); LOG.write(m + "\n"); LOG.flush()
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "peft"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", "torchao"])
    import torch
    from PIL import Image
    from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
    from transformers import CLIPVisionModelWithProjection
    JOBS = json.loads(r'''__JOBS__''')
    CFG = json.loads(r'''__CFG__''')
    # 見本の絵は、データセット masuppp/manga-refs に置いてある(プログラムに埋め込むと、Kaggleで順番待ちのまま動かなくなるため)
    REFS = {}
    for k in json.loads(r'''__REFS__'''):
        hit = glob.glob(f"/kaggle/input/**/ref_{k}.jpg", recursive=True)
        if hit: REFS[k] = Image.open(hit[0]).convert("RGB")
        else: print("見本が見つからない:", k, flush=True)
    blank = Image.new("RGB", (512, 512), "white")
    t0 = time.time()
    enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained("cagliostrolab/animagine-xl-4.0", image_encoder=enc, torch_dtype=torch.float16, use_safetensors=True)
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus_sdxl_vit-h.safetensors")
    loras = []
    for name in CFG["loras"]:
        path = glob.glob(f"/kaggle/input/**/{name}.safetensors", recursive=True)
        if path:
            pipe.load_lora_weights(path[0], adapter_name=name); loras.append(name)
    log("loras loaded", loras)
    pipe.to("cuda"); log("loaded", round(time.time() - t0), "s")
    for job in JOBS:
        use = job.get("loras", {})
        pipe.set_adapters(loras, [use.get(n, 0.0) for n in loras])
        ref = REFS.get(job.get("ref"), blank)
        pipe.set_ip_adapter_scale(job.get("ip_scale", 0.0) if job.get("ref") in REFS else 0.0)
        for seed in job["seeds"]:
            t = time.time()
            img = pipe(prompt=job["prompt"] + ", " + CFG["style"], negative_prompt=CFG["negative"] + (", " + job["neg"] if job.get("neg") else ""),
                       ip_adapter_image=ref, width=job["w"], height=job["h"], num_inference_steps=CFG["steps"],
                       guidance_scale=job.get("cfg", CFG["cfg"]), generator=torch.Generator("cuda").manual_seed(seed)).images[0]
            img.save(f'{OUT}/{job["name"]}_s{seed}.png'); log("saved", job["name"], seed, round(time.time() - t, 1))
    log("done", round(time.time() - t0), "s")
except Exception:
    log(traceback.format_exc()); raise
