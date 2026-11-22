"""生成した絵を「印刷された漫画」の質感に変換する仕上げ処理。

AIイラストらしさの多くは、なめらかな灰色のグラデーションとツヤのある陰影から来る。
本物の漫画原稿は「黒インクの線」「ベタ(真っ黒)」「スクリーントーン(網点)」「白」の
4つだけでできているので、絵をこの4要素に置き換える。

使い方:
    python3 02_departments/manga/tools/manga_finish.py 入力.png 出力.png [--lpi 6] [--line 0.98]
"""
import argparse

import cv2
import numpy as np


def xdog(gray, sigma=0.8, k=1.6, p=20.0, eps=0.0, phi=10.0):
    """ペン入れ風の線を取り出す(XDoG: 漫画の線画抽出によく使われる手法)。"""
    g = gray.astype(np.float32) / 255.0
    g1 = cv2.GaussianBlur(g, (0, 0), sigma)
    g2 = cv2.GaussianBlur(g, (0, 0), sigma * k)
    d = (1 + p) * g1 - p * g2
    out = np.where(d >= eps, 1.0, 1.0 + np.tanh(phi * (d - eps)))
    return np.clip(out, 0, 1)


def halftone(gray, cell=6, angle=45):
    """灰色の部分を、45度に並んだ網点(スクリーントーン)に置き換える。"""
    h, w = gray.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.deg2rad(angle)
    u = (xx * np.cos(t) + yy * np.sin(t)) / cell
    v = (-xx * np.sin(t) + yy * np.cos(t)) / cell
    du = (u - np.floor(u) - 0.5)
    dv = (v - np.floor(v) - 0.5)
    dist = np.sqrt(du * du + dv * dv)  # 網点の中心からの距離(0〜0.7)
    darkness = 1.0 - gray.astype(np.float32) / 255.0
    radius = np.sqrt(darkness / np.pi)  # 暗いほど点が大きい
    return np.where(dist < radius, 0, 255).astype(np.uint8)


def finish(img, cell=5, line_thresh=0.97, black=45, white=175, tone_levels=(0.2, 0.45)):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    # 1. 線(ペン入れ)
    lines = xdog(gray)
    line_mask = lines < line_thresh
    # 2. 濃さを「白・トーン2段階・ベタ」に整理(グラデーションをなくす)
    smooth = cv2.bilateralFilter(gray, 9, 40, 9)
    level = np.full(gray.shape, 255, np.uint8)
    mid = (smooth < white) & (smooth >= black)
    # 明るめの灰色は薄いトーン、暗めは濃いトーン
    light = mid & (smooth >= (white + black) / 2)
    level[light] = int(255 * (1 - tone_levels[0]))
    level[mid & ~light] = int(255 * (1 - tone_levels[1]))
    level[smooth < black] = 0
    tone = halftone(level, cell=cell)
    tone[level == 255] = 255
    tone[level == 0] = 0
    # 3. 合成: 線を上に重ねる
    out = tone.copy()
    out[line_mask] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--cell", type=int, default=5, help="網点の間隔(px)。大きいほど粗いトーン")
    ap.add_argument("--line", type=float, default=0.97, help="線の拾いやすさ(0.9〜0.99)")
    a = ap.parse_args()
    img = cv2.imread(a.src)
    cv2.imwrite(a.dst, finish(img, cell=a.cell, line_thresh=a.line))
    print("saved", a.dst)


if __name__ == "__main__":
    main()
