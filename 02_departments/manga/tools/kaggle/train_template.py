# Kaggle上で実行: キャラクター専用LoRAの学習(diffusers公式のSDXL LoRA学習スクリプトを使用)
import glob, json, os, shutil, subprocess, sys, time, traceback
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/progress.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); LOG.write(m + "\n"); LOG.flush()
def run(cmd):
    log("$", " ".join(cmd)[:300])
    p = subprocess.run(cmd, capture_output=True, text=True)
    log(p.stdout[-3000:]); log(p.stderr[-3000:])
    if p.returncode: raise RuntimeError(f"failed: {cmd[0]} {p.returncode}")

CFG = json.loads(r'''__CFG__''')
try:
    import torch, diffusers
    log("torch", torch.__version__, "diffusers", diffusers.__version__, torch.cuda.get_device_name(0))
    run([sys.executable, "-m", "pip", "install", "-q", "peft", "bitsandbytes", "datasets"])
    ver = diffusers.__version__.split(".dev")[0]
    script = "/kaggle/working/train_lora_sdxl.py"
    tag = f"v{ver}"
    run(["wget", "-q", "-O", script, f"https://raw.githubusercontent.com/huggingface/diffusers/{tag}/examples/text_to_image/train_text_to_image_lora_sdxl.py"])
    # 学習データ: Kaggleデータセットから作業フォルダにコピーし、metadata.jsonlを作る
    src = glob.glob(f"/kaggle/input/{CFG['dataset']}*")[0]
    data = "/kaggle/working/data"; os.makedirs(data, exist_ok=True)
    with open(f"{data}/metadata.jsonl", "w") as f:
        for img in sorted(glob.glob(f"{src}/**/*.jpg", recursive=True)):
            name = os.path.basename(img); shutil.copy(img, f"{data}/{name}")
            cap = open(img[:-4] + ".txt").read().strip()
            f.write(json.dumps({"file_name": name, "text": cap}, ensure_ascii=False) + "\n")
    log("images", len(glob.glob(f"{data}/*.jpg")))
    t0 = time.time()
    run(["accelerate", "launch", "--mixed_precision=fp16", script,
         "--pretrained_model_name_or_path=cagliostrolab/animagine-xl-4.0",
         "--pretrained_vae_model_name_or_path=madebyollin/sdxl-vae-fp16-fix",
         f"--train_data_dir={data}", "--caption_column=text", "--image_column=image",
         f"--resolution={CFG['resolution']}", "--random_flip" if CFG.get("flip") else "--center_crop",
         "--train_batch_size=1", f"--max_train_steps={CFG['steps']}", "--gradient_accumulation_steps=1",
         "--gradient_checkpointing", "--use_8bit_adam", "--mixed_precision=fp16",
         f"--learning_rate={CFG['lr']}", "--lr_scheduler=constant", "--lr_warmup_steps=0",
         f"--rank={CFG['rank']}", "--seed=42", "--checkpointing_steps=100000",
         f"--output_dir={OUT}/lora"])
    log("trained", round(time.time() - t0), "s")
    # 学習結果の確認用に、数枚生成する
    from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
    pipe = StableDiffusionXLPipeline.from_pretrained("cagliostrolab/animagine-xl-4.0", torch_dtype=torch.float16)
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.load_lora_weights(f"{OUT}/lora", weight_name="pytorch_lora_weights.safetensors")
    pipe.to("cuda")
    for i, p in enumerate(CFG["tests"]):
        for seed in (1, 2):
            img = pipe(prompt=p + ", " + CFG["style"], negative_prompt=CFG["negative"], width=832, height=1216,
                       num_inference_steps=28, guidance_scale=4.5, generator=torch.Generator("cuda").manual_seed(seed)).images[0]
            img.save(f"{OUT}/test{i}_s{seed}.png"); log("test", i, seed)
    log("done", round(time.time() - t0), "s")
except Exception:
    log(traceback.format_exc()); raise
