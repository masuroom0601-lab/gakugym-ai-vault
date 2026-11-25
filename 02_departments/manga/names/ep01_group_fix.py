"""第1話2ページの集合ゴマ(2026-11-25、「冒険から帰った夕方の帰り道」に変更)。作業フォルダで実行: python3 ep01_group_fix.py
2-2: 夕方の北の迷宮の門の前。武器を持って笑う4人と、後ろで大荷物を抱えるイヅル
2-4: イヅルに背を向けて笑い合う4人(後ろ姿)"""
import sys; sys.path.insert(0, '/home/user/gakugym-ai-vault/02_departments/manga/names')
from group_common import finder, run
PICK = {}
P = finder('fix1out/out/', PICK)
G = {
    (2, 2): (P('bg_gate_dusk'), [(P('c_izuru_luggage'), .86, 1.0, .62, True),
                                (P('c_ryusei_return'), .12, 1.04, .82, False), (P('c_tamaki_return'), .31, 1.04, .8, False),
                                (P('c_aimi_return'), .5, 1.04, .7, False), (P('c_shiro_return'), .68, 1.04, .88, True)]),
    (2, 4): (P('bg_gate_dusk'), [(P('c_ryusei_laughback'), .2, 1.08, 1.0, False), (P('c_tamaki_laughback'), .42, 1.08, .98, False),
                                (P('c_aimi_laughback'), .62, 1.08, .88, False), (P('c_shiro_laughback'), .82, 1.08, 1.04, False)]),
}
if __name__ == '__main__': run(1, G, 'fix1out/out/')
