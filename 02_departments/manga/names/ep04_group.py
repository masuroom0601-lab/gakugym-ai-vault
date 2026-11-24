"""第4話の集合ゴマの合成。作業フォルダで実行する: python3 ep04_group.py [1-1 3-2 ...](省略で全部)
E=第4話の作画(ep4out/out)、V=第1話の部品(v3bout/out)、E2=第2話の作画(ep2out/out)。部品のシードは PICK で選ぶ"""
import importlib.util, sys
T = '/home/user/gakugym-ai-vault/02_departments/manga/'
sys.path.insert(0, T + 'tools')
from group_composite import compose_group
import layout
E = 'ep4out/out/'; V = 'v3bout/out/'; E2 = 'ep2out/out/'
PICK = {'c_fa_peek':'s1','c_fb_peek':'s1','c_fc_peek':'s1','c_fa_look':'s2','c_fb_look':'s2','c_fc_look':'s1','c_fa_raise':'s1','c_fb_raise':'s1','c_fc_raise':'s2',
        'c_izuru_look':'s1','c_shiina_look':'s2','c_nabe':'s1','c_izuru_nod':'s1','c_shiina_nod':'s1','c_izuru_laugh':'s1','c_sai_laugh':'s2','c_fb_laugh':'s2',
        'c_kidb_sit':'s2','c_kidg_sit':'s1','c_parent_sit':'s1','c_dsuke_raise':'s2','bg_caps_door':'s2','bg_backstage':'s2','bg_hall_table':'s1'}
def P(n, base=E): return f"{base}{n}_{PICK.get(n, 's1')}.png"
spec = importlib.util.spec_from_file_location('n', T + 'names/ep04_name.py'); NAME = importlib.util.module_from_spec(spec); spec.loader.exec_module(NAME)
def aspect(pg, i):
    b = layout.page_panels(NAME, pg)[i - 1]['bbox']; return (b[2] - b[0]) / (b[3] - b[1])
ROOM = E2 + 'bg_room_day_s1.png'
G = {
    (1, 1): (ROOM, [(V + 'c_sweater_chair_s1.png', .5, .9, .5, False), (V + 'c_dsuke_look_s1.png', .14, 1.05, .95, False), (P('c_shiina_look'), .34, 1.05, .95, False),
                    (P('c_izuru_look'), .66, 1.05, .95, True), (V + 'c_hisa_look_s1.png', .87, 1.05, .93, True)]),
    (3, 2): (ROOM, [(P('c_nabe'), .5, .95, .35, False), (V + 'c_shiina_cheer_s1.png', .15, 1.15, 1.05, False), (V + 'c_dsuke_cheer_s1.png', .84, 1.15, 1.05, True),
                    (V + 'c_sai_cheer_s1.png', .32, 1.18, 1.0, False)]),
    (5, 1): (P('bg_caps_door'), [(P('c_fa_peek'), .3, 1.0, .8, False), (P('c_fb_peek'), .52, 1.0, .76, False), (P('c_fc_peek'), .72, 1.0, .68, True)]),
    (7, 3): (ROOM, [(P('c_fa_look'), .2, 1.1, 1.0, False), (P('c_fb_look'), .5, 1.1, .95, True), (P('c_fc_look'), .8, 1.1, .9, True)]),
    (11, 4): (P('bg_backstage'), [(P('c_izuru_nod'), .3, 1.1, 1.0, False), (P('c_shiina_nod'), .72, 1.1, .97, False)]),
    (12, 2): (P('bg_hall_table'), [(P('c_kidb_sit'), .2, 1.1, .8, False), (P('c_kidg_sit'), .48, 1.1, .78, True), (P('c_parent_sit'), .8, 1.1, 1.0, True)]),
    (13, 5): (P('bg_hall_table'), [(P('c_fb_laugh'), .2, 1.15, 1.05, False), (P('c_sai_laugh'), .5, 1.15, 1.05, False), (P('c_izuru_laugh'), .8, 1.15, 1.05, True)]),
    (15, 3): (ROOM, [(P('c_dsuke_raise'), .14, 1.05, .95, False), (P('c_fa_raise'), .38, 1.05, .9, False), (P('c_fb_raise'), .62, 1.05, .88, True), (P('c_fc_raise'), .86, 1.05, .8, True)]),
}
if __name__ == '__main__':
    want = sys.argv[1:]
    for (pg, i), (bg, items) in G.items():
        if want and f'{pg}-{i}' not in want: continue
        compose_group(bg, items, f'{E}p{pg:02d}_{i}_c.png', aspect=aspect(pg, i)); print(f'{pg}ページ {i}コマ目 合成済み')
