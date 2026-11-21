# Kaggle上で実行される生成スクリプト(build_kernel.pyが見本画像と依頼内容を埋め込んで作る)
# 画像生成AI: Animagine XL 4.0 + IP-Adapter(見本画像の顔・服装を引き継ぐ)
import base64, io, json, os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "diffusers>=0.32", "transformers", "accelerate", "safetensors"], check=True)
import torch
from PIL import Image
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
from transformers import CLIPVisionModelWithProjection

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
print("loaded", round(time.time() - t0), "s", flush=True)

for job in JOBS:
    pipe.set_ip_adapter_scale(job.get("ip_scale", CFG["ip_scale"]))
    for seed in job["seeds"]:
        t = time.time()
        img = pipe(
            prompt=f'{job["prompt"]}, {CFG["style"]}, {CFG["quality"]}',
            negative_prompt=CFG["negative"],
            ip_adapter_image=REF,
            width=job.get("w", 832), height=job.get("h", 1216),
            num_inference_steps=CFG["steps"], guidance_scale=CFG["cfg"],
            generator=torch.Generator("cuda").manual_seed(seed),
        ).images[0]
        img.save(f'{OUT}/{job["name"]}_s{seed}.png')
        print("saved", job["name"], seed, round(time.time() - t, 1), "s", flush=True)
print("done", round(time.time() - t0), "s")
