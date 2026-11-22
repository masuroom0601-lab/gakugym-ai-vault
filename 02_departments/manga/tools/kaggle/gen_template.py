# Kaggle上で実行される生成スクリプト(build_kernel.pyが見本画像と依頼内容を埋め込んで作る)
# 画像生成AI: Animagine XL 4.0 + IP-Adapter(見本画像の顔・服装を引き継ぐ)
import base64, io, json, os, subprocess, sys, time, traceback
os.makedirs("/kaggle/working/out", exist_ok=True)
LOG = open("/kaggle/working/out/progress.txt", "a")
def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True); LOG.write(msg + "\n"); LOG.flush()
try:
    import diffusers  # Kaggleに入っていれば入れ直さない(torch等を壊さないため)
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "diffusers"], check=True)
from PIL import Image
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
from transformers import CLIPVisionModelWithProjection

try:
    import torch
    log('torch', torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-')
    JOBS = json.loads(r'''__JOBS__''')
    REF = Image.open(io.BytesIO(base64.b64decode("__REF__"))).convert("RGB")
    CFG = json.loads(r'''__CFG__''')
    OUT = "/kaggle/working/out"
    os.makedirs(OUT, exist_ok=True)

    t0 = time.time()
    encoder = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained("cagliostrolab/animagine-xl-4.0", image_encoder=encoder, torch_dtype=torch.float16, use_safetensors=True)
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus_sdxl_vit-h.safetensors")
    pipe.to("cuda")
    log("loaded", round(time.time() - t0), "s")

    for job in JOBS:
        pipe.set_ip_adapter_scale(job.get("ip_scale", CFG["ip_scale"]))
        for seed in job["seeds"]:
            t = time.time()
            img = pipe(
                prompt=", ".join(x for x in (job["prompt"], job.get("style", CFG["style"]), job.get("quality", CFG["quality"])) if x),
                negative_prompt=CFG["negative"] + (", " + job["neg"] if job.get("neg") else ""),
                ip_adapter_image=REF,
                width=job.get("w", 832), height=job.get("h", 1216),
                num_inference_steps=CFG["steps"], guidance_scale=job.get("cfg", CFG["cfg"]),
                generator=torch.Generator("cuda").manual_seed(seed),
            ).images[0]
            img.save(f'{OUT}/{job["name"]}_s{seed}.png')
            log("saved", job["name"], seed, round(time.time() - t, 1), "s")
    log("done", round(time.time() - t0), "s")
except Exception:
    log(traceback.format_exc())
    raise
