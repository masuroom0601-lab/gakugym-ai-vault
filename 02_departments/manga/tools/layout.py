"""ネームのコマ割りから、各コマの形(多角形)を計算する。ネームの表示・原稿の合成・作画サイズの計算で共通に使う。

ネームの書き方(names/epXX_name.py):
    PAGES = {ページ: [段, 段, ...]}            段は上から順
    段   = (高さの比率, [コマ, コマ, ...])       コマは右から左の順(漫画の読み順)
         = (高さの比率, [コマ...], {"tilt": 0.05})
           tilt: この段の「下の境目」を斜めにする。正なら右下がり、負なら左下がり(ページの高さに対する割合)
    コマ = (幅の比率, ショット, 絵の内容, [セリフ...])
         = (幅の比率, ショット, 絵の内容, [セリフ...], {オプション})
           slant: このコマの「左の境目」を斜めにする。正なら上が左へ、下が右へ傾く(ページの幅に対する割合)
           bleed: 裁ち切り。"t" "b" "l" "r" の組み合わせで、ページの端まで絵を広げる(例: "tr")
           noframe: True で枠線を描かない(背景に溶け込むコマ)
           breakout: True で、キャラクターが枠からはみ出す(切り抜いたキャラを枠の上に重ねる)
    INSETS = {ページ: [(左, 上, 右, 下, ショット, 絵の内容, [セリフ], {オプション}), ...]}
           大きいコマの上に重ねる小さいコマ。位置はページに対する割合(0〜1)
"""
W, H, M, G = 1000, 1414, 60, 14


def _isect(a, b):
    (x1, y1), (x2, y2) = a; (x3, y3), (x4, y4) = b
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < 1e-9: return ((x1 + x3) / 2, (y1 + y3) / 2)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def _shift(line, dist, toward):
    """直線を、点 toward の側へ dist だけ平行移動する"""
    (x1, y1), (x2, y2) = line
    nx, ny = -(y2 - y1), (x2 - x1); L = (nx * nx + ny * ny) ** 0.5 or 1; nx, ny = nx / L, ny / L
    if (toward[0] - x1) * nx + (toward[1] - y1) * ny < 0: nx, ny = -nx, -ny
    return ((x1 + nx * dist, y1 + ny * dist), (x2 + nx * dist, y2 + ny * dist))


def _split(item, n):
    return (tuple(item[:n]), item[n] if len(item) > n else {})


def panels(rows, insets=()):
    """読み順に、各コマの情報を返す: {"poly": [(x,y)...], "bbox":(x0,y0,x1,y1), "inner":(x0,y0,x1,y1),
    "data": (幅, ショット, 内容, セリフ), "opts": {...}, "frame": bool, "inset": bool}"""
    out = []
    nrow = len(rows)
    usable_h = H - 2 * M - G * (nrow - 1)
    # 段の境目(すき間の中心)の直線
    hs = [int(usable_h * r[0]) for r in rows]
    ys = [M]; y = M
    for h in hs[:-1]:
        y += h + G; ys.append(y)
    bounds = []  # 段 k と k+1 の境目
    for k in range(nrow - 1):
        yb = ys[k + 1] - G / 2; t = (rows[k][2] if len(rows[k]) > 2 else {}).get("tilt", 0) * H
        bounds.append(((0, yb - t / 2), (W, yb + t / 2)))
    for k, row in enumerate(rows):
        rh, plist = row[0], row[1]
        ytop, ybot = ys[k], ys[k] + hs[k]
        top = bounds[k - 1] if k > 0 else ((0, M), (W, M))
        bot = bounds[k] if k < nrow - 1 else ((0, H - M), (W, H - M))
        usable_w = W - 2 * M - G * (len(plist) - 1)
        xr = W - M; ymid = (ytop + ybot) / 2
        xs = []
        for p in plist:
            w = int(usable_w * p[0]); xs.append((xr - w, xr)); xr = xr - w - G
        for j, p in enumerate(plist):
            data, opts = _split(p, 4)
            x0, x1 = xs[j]
            bleed = opts.get("bleed", "")
            # 左右の境目
            if j == len(plist) - 1:
                lx = 0 if "l" in bleed else M; left = ((lx, 0), (lx, H)); lshared = False
            else:
                xb = x0 - G / 2; s = opts.get("slant", 0) * W
                left = ((xb + s / 2, ytop), (xb - s / 2, ybot)); lshared = True
            if j == 0:
                rx = W if "r" in bleed else W - M; right = ((rx, 0), (rx, H)); rshared = False
            else:
                xb = x1 + G / 2; s = _split(plist[j - 1], 4)[1].get("slant", 0) * W
                right = ((xb + s / 2, ytop), (xb - s / 2, ybot)); rshared = True
            tl, bl = top, bot
            if "t" in bleed and k == 0: tl = ((0, 0), (W, 0))
            if "b" in bleed and k == nrow - 1: bl = ((0, H), (W, H))
            c = ((x0 + x1) / 2, ymid)
            if k > 0 and tl is top: tl = _shift(tl, G / 2, c)
            if k < nrow - 1 and bl is bot: bl = _shift(bl, G / 2, c)
            if lshared: left = _shift(left, G / 2, c)
            if rshared: right = _shift(right, G / 2, c)
            poly = [_isect(tl, right), _isect(right, bl), _isect(bl, left), _isect(left, tl)]
            out.append(_info(poly, data, opts, False))
    for it in insets:
        x0, y0, x1, y1 = it[0] * W, it[1] * H, it[2] * W, it[3] * H
        data = (0,) + tuple(it[4:7]); opts = it[7] if len(it) > 7 else {}
        out.append(_info([(x1, y0), (x1, y1), (x0, y1), (x0, y0)], data, opts, True))
    return out


def _info(poly, data, opts, inset):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    bbox = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))
    (trx, tr_y), (brx, br_y), (blx, bl_y), (tlx, tl_y) = poly
    inner = (int(max(tlx, blx)), int(max(tl_y, tr_y)), int(min(trx, brx)), int(min(bl_y, br_y)))
    return {"poly": [(float(x), float(y)) for x, y in poly], "bbox": bbox, "inner": inner,
            "data": data, "opts": opts, "frame": not opts.get("noframe"), "inset": inset}


def page_panels(mod, page):
    return panels(mod.PAGES[page], getattr(mod, "INSETS", {}).get(page, ()))


def frame_edges(poly):
    """枠線を描く辺(ページの端に接する辺=裁ち切りの辺は描かない)"""
    out = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        on_edge = (abs(a[0]) < 1 and abs(b[0]) < 1) or (abs(a[0] - W) < 1 and abs(b[0] - W) < 1) or \
                  (abs(a[1]) < 1 and abs(b[1]) < 1) or (abs(a[1] - H) < 1 and abs(b[1] - H) < 1)
        if not on_edge: out.append((a, b))
    return out
