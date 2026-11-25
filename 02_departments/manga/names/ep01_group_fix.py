"""第1話2ページの集合ゴマ(2026-11-25、「冒険から帰った夕方の帰り道」に変更)。作業フォルダで実行: python3 ep01_group_fix.py
2-2: 夕方の北の迷宮の門の前。武器を持って笑う4人と、後ろで大荷物を抱えるイヅル
2-4: イヅルに背を向けて笑い合う4人(後ろ姿)"""
import sys; sys.path.insert(0, '/home/user/gakugym-ai-vault/02_departments/manga/names')
from group_common import finder, run
PICK = {'c_aimi_return':'s1','c_aimi_laughback':'s1','c_ryusei_return':'s1','c_ryusei_laughback':'s2','c_shiro_return':'s1','c_shiro_laughback':'s2',
        'c_tamaki_return':'s2','c_tamaki_laughback':'s2','c_izuru_luggage':'s2','bg_gate_dusk':'s2'}
P = finder('fix1out/out/', PICK)
G = {
    (2, 2): (P('bg_gate_dusk'), [(P('c_izuru_luggage'), .93, 1.0, .6, True),
                                (P('c_ryusei_return'), .36, 1.04, .78, False), (P('c_tamaki_return'), .5, 1.04, .76, False),
                                (P('c_aimi_return'), .64, 1.04, .66, False), (P('c_shiro_return'), .78, 1.04, .84, True)]),
    (2, 4): (P('bg_gate_dusk'), [(P('c_ryusei_laughback'), .2, 1.08, 1.0, False), (P('c_tamaki_laughback'), .42, 1.08, .98, False),
                                (P('c_aimi_laughback'), .62, 1.08, .88, False), (P('c_shiro_laughback'), .82, 1.08, 1.04, False)]),
}
if __name__ == '__main__': run(1, G, 'fix1out/out/')
