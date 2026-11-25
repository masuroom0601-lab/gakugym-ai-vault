"""集合ゴマの合成の共通部分(第5話以降)。作業フォルダで使う。
部品は、新しい話の作画→前の話の描き直し→前の話の作画、の順に探す(前の話の部品を使い回すため)"""
import importlib.util, os, sys
T = '/home/user/gakugym-ai-vault/02_departments/manga/'
sys.path.insert(0, T + 'tools')
from group_composite import compose_group, add_net
import layout
DIRS = ['ep7out/out/', 'ep6out/out/', 'ep5out/out/', 'ep4out/out/', 'ep3r/out/', 'ep3out/out/', 'ep2out/out/', 'v3bout/out/']
def finder(first, pick, extra=()):
    """extra: 先に探すフォルダ(第6・7話の普段着の描き直し fix3out など)"""
    dirs = list(extra) + [first] + [d for d in DIRS if d != first]
    def P(n):
        s = pick.get(n, 's1')
        for d in dirs:
            for seed in (s, 's1', 's2', 's3'):
                p = f'{d}{n}_{seed}.png'
                if os.path.exists(p): return p
        raise FileNotFoundError(n)
    return P
def name_module(ep):
    spec = importlib.util.spec_from_file_location('n', T + f'names/ep{ep:02d}_name.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def run(ep, G, out_dir, post=None):
    m = name_module(ep); want = sys.argv[1:]
    for (pg, i), (bg, items) in G.items():
        if want and f'{pg}-{i}' not in want: continue
        b = layout.page_panels(m, pg)[i - 1]['bbox']; out = f'{out_dir}p{pg:02d}_{i}_c.png'
        compose_group(bg, items, out, aspect=(b[2] - b[0]) / (b[3] - b[1]))
        if post and (pg, i) in post: post[(pg, i)](out)
        print(f'{pg}ページ {i}コマ目 合成済み')
