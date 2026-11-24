"""第5話の集合ゴマの合成。作業フォルダで実行: python3 ep05_group.py [1-1 ...]"""
import sys; sys.path.insert(0, '/home/user/gakugym-ai-vault/02_departments/manga/names')
from group_common import finder, run
PICK = {}
P = finder('ep5out/out/', PICK)
four = lambda kind, xs, foot, h, fl=(False, False, True, True): [(P(f'c_{w}_{kind}'), x, foot, h, f) for w, x, f in zip(('ryusei', 'tamaki', 'aimi', 'shiro'), xs, fl)]
G = {
    (1, 1): (P('bg_room_night'), [(P('c_nabe'), .5, .92, .3, False), (P('c_hisa_cheer'), .14, 1.15, 1.0, False), (P('c_fa_party'), .36, 1.05, .9, False),
                                  (P('c_fb_party'), .64, 1.05, .88, True), (P('c_sai_cheer'), .86, 1.15, 1.0, True)]),
    (4, 1): (P('bg_gate'), [(P('c_aimi_stand'), .34, .98, .6, False), (P('c_shiro_stand'), .66, 1.0, .68, True)]),
    (10, 1): (P('bg_room_night'), [(P('c_shiina_cheer'), .15, 1.15, 1.0, False), (P('c_dsuke_cheer'), .85, 1.15, 1.0, True), (P('c_hisa_cheer'), .68, 1.15, .95, True),
                                   (P('c_izuru_laugh'), .4, 1.1, 1.05, False)]),
    (12, 1): (P('bg_corridor'), four('tired', (.2, .4, .6, .8), 1.0, .7)),
    (12, 6): (P('bg_corridor'), four('back', (.4, .47, .54, .61), .9, .35, (False,) * 4)),
    (13, 1): (P('bg_brave_night'), [(P('c_ryusei_room'), .14, 1.02, .92, False), (P('c_tamaki_room'), .34, 1.02, .9, False),
                                    (P('c_aimi_room'), .84, 1.02, .85, True), (P('c_shiro_sofa'), .6, 1.0, .8, False)]),
    (18, 5): (P('bg_brave_night'), [(P('c_ryusei_argue'), .14, 1.02, .9, False), (P('c_tamaki_argue'), .38, 1.02, .9, False),
                                    (P('c_aimi_argue'), .62, 1.02, .85, True), (P('c_shiro_argue'), .86, 1.02, .95, True)]),
    (20, 2): (P('bg_corridor_scar'), [(P('c_izuru_luggage'), .5, 1.0, .7, False), (P('c_aimi_victory'), .2, 1.05, .9, False), (P('c_shiro_victory'), .8, 1.05, 1.0, True)]),
}
if __name__ == '__main__': run(5, G, 'ep5out/out/')
