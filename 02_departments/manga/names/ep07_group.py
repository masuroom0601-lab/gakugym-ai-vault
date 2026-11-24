"""第7話の集合ゴマの合成。作業フォルダで実行: python3 ep07_group.py [8-1 ...]"""
import sys; sys.path.insert(0, '/home/user/gakugym-ai-vault/02_departments/manga/names')
from group_common import finder, run
PICK = {}
P = finder('ep7out/out/', PICK)
G = {
    (8, 1): (P('bg_interview'), [(P('c_hr_nod'), .3, 1.1, .95, False), (P('c_staff_nod'), .72, 1.1, .92, True)]),
    (10, 3): (P('bg_interview'), [(P('c_ryusei_down'), .14, 1.0, .8, False), (P('c_tamaki_down'), .36, 1.0, .78, False),
                                  (P('c_aimi_down'), .62, 1.0, .72, True), (P('c_shiro_slump'), .86, 1.02, .8, True)]),
    (11, 1): (P('bg_sunset'), [(P('c_ryusei_leave'), .2, .98, .62, False), (P('c_tamaki_leave'), .4, .98, .6, False),
                               (P('c_aimi_leave'), .6, .98, .56, False), (P('c_shiro_leave'), .8, .98, .64, False)]),
    (16, 1): (P('bg_sunset'), [(P('c_izuru_calm'), .66, 1.02, .9, True), (P('c_shiro_hand'), .3, 1.02, .95, False)]),
    (17, 1): (P('bg_sunset'), [(P('c_shiro_hand'), .28, 1.05, 1.0, False), (P('c_izuru_lower'), .68, 1.1, 1.05, True)]),
    (19, 2): (P('bg_sunset'), [(P('c_ryusei_down'), .25, 1.0, .85, False), (P('c_tamaki_down'), .5, 1.0, .82, False), (P('c_aimi_down'), .75, 1.0, .78, True)]),
    (19, 3): (P('bg_sunset'), [(P('c_izuru_back'), .38, .98, .6, False), (P('c_shiina_back'), .6, .98, .56, False)]),
    (20, 1): (P('bg_path_sunset'), [(P('c_izuru_walk'), .38, 1.0, .75, False), (P('c_shiina_walk'), .64, 1.0, .72, True)]),
    (21, 1): (P('bg_caps_room'), [(P('c_hisa_cracker'), .2, 1.02, .9, False), (P('c_sai_cracker'), .5, 1.02, .88, False), (P('c_dsuke_cracker'), .8, 1.02, .92, True)]),
    (22, 2): (P('bg_caps_room'), [(P('c_izuru_patted'), .62, 1.1, 1.0, True), (P('c_sai_pat'), .3, 1.1, 1.05, False)]),
    (23, 3): (P('bg_caps_room'), [(P('c_dsuke_fist'), .14, 1.05, .95, False), (P('c_hisa_fist'), .38, 1.05, .92, False),
                                  (P('c_sai_fist'), .62, 1.05, .92, True), (P('c_shiina_fist'), .86, 1.05, .9, True)]),
    (25, 1): (P('bg_caps_room'), [(P('c_sweater_chair'), .5, .85, .45, False), (P('c_dsuke_smile'), .14, 1.05, .95, False),
                                  (P('c_newbie'), .38, 1.05, .88, False), (P('c_izuru_smile'), .62, 1.05, .95, True), (P('c_shiina_smile'), .86, 1.05, .92, True)]),
    (25, 2): (P('bg_caps_room'), [(P('c_nabe'), .45, .95, .32, False), (P('c_haniwa'), .6, .95, .35, False),
                                  (P('c_sai_smile'), .2, 1.1, 1.0, False), (P('c_hisa_smile'), .82, 1.1, 1.0, True)]),
}
if __name__ == '__main__': run(7, G, 'ep7out/out/')
