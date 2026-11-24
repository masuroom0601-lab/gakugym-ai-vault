"""第6話の集合ゴマの合成。作業フォルダで実行: python3 ep06_group.py [1-1 ...]"""
import sys; sys.path.insert(0, '/home/user/gakugym-ai-vault/02_departments/manga/names')
from group_common import finder, run
PICK = {'bg_career':'s1','bg_interview':'s2','c_aimi_casual':'s1','c_aimi_seat':'s1','c_hr_note':'s1','c_hr_sit':'s1','c_izuru_away':'s1','c_izuru_flyer':'s1',
        'c_izuru_stand':'s1','c_ryusei_casual':'s2','c_ryusei_seat':'s1','c_shiina_flyer':'s1','c_shiina_stand':'s1','c_shiina_step':'s1','c_shiro_cross':'s3',
        'c_shiro_reach':'s3','c_shiro_seat':'s2','c_shiro_wave':'s3','c_staff_note':'s2','c_staff_sit':'s1','c_tamaki_casual':'s2','c_tamaki_seat':'s1'}
P = finder('ep6out/out/', PICK)
BRAVE = lambda xs, foot, h: [(P('c_ryusei_casual'), xs[0], foot, h, False), (P('c_tamaki_casual'), xs[1], foot, h, False),
                             (P('c_aimi_casual'), xs[2], foot, h * .93, True), (P('c_shiro_wave'), xs[3], foot, h * 1.05, True)]
G = {
    (1, 1): (P('bg_career'), [(P('c_izuru_flyer'), .38, 1.0, .75, False), (P('c_shiina_flyer'), .64, 1.0, .72, True)]),
    (2, 2): (P('bg_career'), BRAVE((.14, .36, .62, .85), 1.02, .9)),
    (3, 3): (P('bg_career'), [(P('c_izuru_away'), .64, 1.02, .9, False), (P('c_shiro_reach'), .3, 1.02, .95, False)]),
    (7, 1): (P('bg_career'), [(P('c_izuru_stand'), .7, .98, .7, True), (P('c_shiina_step'), .36, 1.05, .95, False)]),
    (15, 1): (P('bg_career'), BRAVE((.56, .67, .78, .9), 1.0, .62) + [(P('c_shiina_stand'), .26, 1.0, .58, False), (P('c_izuru_stand'), .1, 1.0, .62, False)]),
    (17, 1): (P('bg_interview'), [(P('c_hr_sit'), .3, 1.1, .95, False), (P('c_staff_sit'), .72, 1.1, .92, True)]),
    (17, 2): (P('bg_interview'), [(P('c_ryusei_seat'), .14, 1.1, .95, False), (P('c_tamaki_seat'), .38, 1.1, .92, False),
                                  (P('c_aimi_seat'), .62, 1.1, .9, True), (P('c_shiro_seat'), .86, 1.1, .98, True)]),
    (22, 1): (P('bg_interview'), [(P('c_hr_note'), .3, 1.1, .95, False), (P('c_staff_note'), .72, 1.1, .92, True)]),
}
if __name__ == '__main__': run(6, G, 'ep6out/out/')
