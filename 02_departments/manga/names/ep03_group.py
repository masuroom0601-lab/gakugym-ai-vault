"""第3話の集合ゴマの合成。使い方: python3 ep3group.py [1-1 3-4 ...] (省略で全部)
部品のシードは PICK で選ぶ(作画を見てから決める)"""
import sys
sys.path.insert(0, '/home/user/gakugym-ai-vault/02_departments/manga/tools')
from group_composite import compose_group, add_net
E = 'ep3out/out/'; V = 'v3bout/out/'; E2 = 'ep2out/out/'
PICK = {'c_shiro_stand':'s2','c_aimi_stand':'s2','c_ryusei_stand':'s1','c_tamaki_stand':'s2',
 'c_shiro_back':'s2','c_aimi_back':'s2','c_ryusei_back':'s2','c_tamaki_back':'s2',
 'c_shiro_sit':'s2','c_aimi_sit':'s1','c_ryusei_sit':'s1','c_tamaki_sit':'s2',
 'c_shiro_net':'s3','c_aimi_net':'s1','c_ryusei_net':'s1','c_tamaki_net':'s2',
 'c_shiro_walk':'s2','c_aimi_walk':'s1','c_ryusei_walk':'s2','c_tamaki_walk':'s2',
 'c_shiro_back_c':'s2','c_aimi_back_c':'s2','c_fresh_a':'s1','c_fresh_b':'s2','c_dsuke_mic':'s2',
 'c_izuru_camera':'s2','c_shiina_memo':'s2','c_hisa_sweater':'s2',
 'bg_gate':'s2','bg_gate_dusk':'s2','bg_corridor':'s2','bg_corridor_scar':'s1','bg_campus_path':'s1','bg_courtyard':'s1'}
def P(n, base=E):
    v = PICK.get(n, 's1')
    if v.startswith('r'): return f"ep3r/out/{n}_s{v[1:]}.png"  # 描き直し(r1〜r3)
    return f"{base}{n}_{v}.png"
def four(kind, xs, foot, h, flips=(False, False, False, False), order=("ryusei", "tamaki", "aimi", "shiro")):
    """4人を並べる。order は奥から手前の順"""
    return [(P(f"c_{w}_{kind}"), x, foot, h, f) for w, x, f in zip(order, xs, flips)]
G = {
    (1, 1): (P('bg_gate'), 1000/612, four('stand', (.18, .38, .6, .82), .98, .55, (False, False, True, True))),
    (3, 4): (P('bg_gate'), 880/331, four('stand', (.14, .38, .62, .86), 1.9, 1.7, (False, False, True, True))),
    (5, 1): (P('bg_corridor'), 1000/511, four('stand', (.4, .47, .54, .61), .9, .32)),
    (6, 1): (P('bg_corridor_scar'), 940/453, four('back', (.22, .41, .6, .79), 1.08, .75)),
    (6, 4): (P('bg_corridor'), 880/293, four('sit', (.2, .4, .6, .8), 1.0, .62)),
    (7, 4): (P('bg_corridor'), 940/453, four('net', (.2, .4, .6, .8), 1.02, .82, (False, True, False, True))),
    (8, 1): (P('bg_corridor'), 940/528, four('net', (.15, .38, .62, .85), 1.05, .9, (True, False, True, False))),
    (9, 1): (P('bg_gate_dusk'), 1000/612, four('tired', (.2, .4, .6, .8), 1.0, .62)),
    (9, 4): (P('bg_gate_dusk'), 1000/492, four('back', (.36, .46, .56, .66), 1.0, .5)),
    (12, 1): (P('bg_campus_path'), 940/587, [(P('c_fresh_a'), .3, 1.05, .95, False), (P('c_fresh_b'), .7, 1.05, .95, True)]),
    (12, 3): (P('bg_campus_path'), 880/467, [(P('c_aimi_back_c'), .38, 1.05, .9, False), (P('c_shiro_back_c'), .62, 1.08, 1.0, False)]),
    (13, 4): (P('bg_campus_path'), 880/517, [(P('c_aimi_back_c'), .45, .9, .45, False), (P('c_shiro_back_c'), .56, .92, .5, False)]),
    (14, 1): (E2 + 'bg_brave_room_s2.png', 941/406, four('stand', (.14, .38, .62, .86), 1.06, .95, (False, False, True, True))),
    (17, 1): (P('bg_courtyard'), 1000/506, [(P('c_hisa_sweater'), .12, 1.0, .8, False), (E2 + 'c_shiina_phone_s1.png', .34, 1.0, .82, False),
                                            (P('c_izuru_camera'), .62, 1.02, .85, True), (P('c_dsuke_mic'), .86, 1.02, .86, True)]),
    (18, 1): (E2 + 'bg_room_night_s1.png', 941/506, [(V + 'c_dsuke_cheer_s1.png', .15, 1.15, 1.05, False), (V + 'c_hisa_cheer_s1.png', .38, 1.15, 1.05, False),
                                                    (V + 'c_sai_cheer_s1.png', .62, 1.18, 1.05, True), (V + 'c_shiina_cheer_s1.png', .85, 1.18, 1.05, True)]),
}
if __name__ == '__main__':
    want = sys.argv[1:]
    for (pg, i), (bg, asp, items) in G.items():
        if want and f'{pg}-{i}' not in want: continue
        out = f'{E}p{pg:02d}_{i}_c.png'; compose_group(bg, items, out, aspect=asp)
        if (pg, i) == (7, 4): add_net(out, out, top=-0.05, bottom=0.75, seed=1)  # 落ちてきた網
        if (pg, i) == (8, 1): add_net(out, out, top=0.0, bottom=0.9, seed=2)
        print(f'{pg}ページ {i}コマ目 合成済み')
