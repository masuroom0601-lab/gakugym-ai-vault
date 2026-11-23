# 第2話の原稿で使ったシード(コマ番号: シード、"c"は集合ゴマの合成)
P={1:{1:'s1',2:'s1',3:'c',4:'s1',5:'s2',6:'s2'},2:{1:'s1',2:'s1',3:'s2',4:'s1'},3:{1:'s1',2:'s2',3:'s2',4:'s2',5:'s2',6:'s2',7:'s2'},
4:{1:'s1',2:'s1',3:'s1',4:'s1',5:'s2'},5:{1:'s1',2:'s1',3:'s2',4:'s1'},6:{1:'s1',2:'s2',3:'s1',4:'s1',5:'s1',6:'s2'},
7:{1:'s1',2:'s2',3:'s2',4:'s1'},8:{1:'c',2:'s1'},9:{1:'s2',2:'s2',3:'s2',4:'s1'},10:{1:'s1',2:'s1',3:'s2',4:'s1',5:'s1'},
11:{1:'s1',2:'s1',3:'s2'},12:{1:'s1',2:'s2',3:'s2',4:'s1'},13:{1:'s1',2:'s1',3:'s1',4:'s2'},14:{1:'s1',2:'s1',3:'s1',4:'s1'},
15:{1:'s1',2:'s2',3:'s1'},16:{1:'c',2:'s2',3:'s1',4:'s1'},17:{1:'s1',2:'s1',3:'c',4:'s1'},18:{1:'s2',2:'s2',3:'s1'},
19:{1:'s1',2:'s2',3:'s1',4:'s1'},20:{1:'s2',2:'s2',3:'c',4:'s2'}}

# 集合ゴマの合成(作業フォルダで実行したもの。E=第2話の作画、V=第1話の部品)
# import sys; sys.path.insert(0,'/home/user/gakugym-ai-vault/02_departments/manga/tools')
# from group_composite import compose_group
# E='ep2out/out/'; V='v3bout/out/'
# G={
#  (1,3):(E+'bg_room_day_s1.png',1000/574,[(V+'c_sweater_chair_s1.png',.36,.92,.62,False),(V+'c_dsuke_look_s1.png',.13,1.02,.9,False),(V+'c_hisa_look_s1.png',.86,1.02,.88,True),(V+'c_sai_look_s1.png',.62,1.05,.95,True)]),
#  (8,1):(E+'bg_room_night_s1.png',940/555,[(V+'c_sweater_chair_s1.png',.5,.88,.55,False),(V+'c_dsuke_look_s1.png',.15,1.05,.95,False),(V+'c_shiina_wall_s1.png',.35,1.1,1.0,False),(V+'c_sai_look_s1.png',.68,1.08,.98,True),(V+'c_hisa_look_s1.png',.88,1.05,.92,True)]),
#  (16,1):(E+'bg_room_day_s1.png',1000/695,[(E+'c_dsuke_phone_s2.png',.12,.95,.8,False),(E+'c_shiina_phone_s1.png',.3,.97,.82,False),(E+'c_sai_phone_s2.png',.7,.97,.82,True),(E+'c_hisa_phone_s2.png',.88,.95,.8,True),(E+'c_izuru_burst_s1.png',.5,1.1,1.0,False)]),
#  (17,3):(E+'bg_room_day_s1.png',462/278,[(V+'c_dsuke_cheer_s1.png',.13,1.35,1.25,False),(V+'c_shiina_cheer_s1.png',.37,1.38,1.25,False),(V+'c_sai_cheer_s1.png',.63,1.38,1.25,True),(V+'c_hisa_cheer_s1.png',.87,1.35,1.25,True)]),
#  (20,3):(E+'bg_brave_room_s2.png',463/318,[(E+'c_aimi_away_s2.png',.2,1.8,1.7,False),(E+'c_ryusei_away_s1.png',.5,1.75,1.75,False),(E+'c_tamaki_away_s2.png',.8,1.8,1.7,True)]),
# }
# for (pg,i),(bg,asp,items) in G.items():
#     if len(sys.argv)>1 and f'{pg}-{i}' not in sys.argv[1:]: continue
#     compose_group(bg,items,E+f'p{pg:02d}_{i}_c.png',aspect=asp); print(f'{pg}ページ {i}コマ目 合成済み')
