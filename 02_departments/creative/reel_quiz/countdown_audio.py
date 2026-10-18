"""英検クイズリール用のカウントダウン効果音(時計のカチカチ+時間切れのチーン)を作る(2026-10-18新設)。

外部の音源ファイルは使わず、毎回その場で合成する(著作権の心配がない)。
  0〜10秒:  0.5秒ごとに「カチ」「コチ」(高い音と低い音を交互)。残り3秒からは少し大きく
  10秒:     「チーン」(時間切れ)
  エンド画面: 無音
使い方: python3 countdown_audio.py out.wav [全体の秒数]
"""
import math, random, struct, sys, wave

SR = 44100

def render(total=13.0, count=10):
    n = int(total * SR)
    buf = [0.0] * n
    rnd = random.Random(7)  # 毎回同じ音になるよう乱数を固定

    def add(start, samples):
        s = int(start * SR)
        for i, v in enumerate(samples):
            if s + i < n: buf[s + i] += v

    def tick(freq, gain):
        # 木を叩いたような短いクリック音(約40ms): 減衰するサイン波+少しのノイズ
        out = []
        for i in range(int(0.04 * SR)):
            t = i / SR
            env = math.exp(-t * 140)
            out.append(gain * env * (0.75 * math.sin(2 * math.pi * freq * t) + 0.25 * (rnd.random() * 2 - 1)))
        return out

    def bell(gain):
        # 「チーン」: 倍音を重ねたベル音(約1.6秒で消える)
        out = []
        for i in range(int(1.6 * SR)):
            t = i / SR
            v = (math.sin(2 * math.pi * 1320 * t) * math.exp(-t * 2.5)
                 + 0.5 * math.sin(2 * math.pi * 2640 * t) * math.exp(-t * 4)
                 + 0.25 * math.sin(2 * math.pi * 3960 * t) * math.exp(-t * 6))
            out.append(gain * min(1.0, t * 400) * v / 1.75)
        return out

    for k in range(count * 2):
        t = k * 0.5
        last3 = t >= count - 3
        add(t, tick(2200 if k % 2 == 0 else 1600, 0.55 if last3 else 0.38))
    add(count, bell(0.6))
    return buf

def write(path, buf):
    peak = max(1e-9, max(abs(v) for v in buf))
    scale = min(1.0, 0.9 / peak)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v * scale)) * 32767)) for v in buf))

if __name__ == "__main__":
    write(sys.argv[1], render(float(sys.argv[2]) if len(sys.argv) > 2 else 13.0))
