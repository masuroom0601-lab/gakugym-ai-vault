#!/bin/bash
# GPTで描いたページに、文字を入れ直して names/epNN/gpt/ と pages/ に置く。各ページの仕上げの設定と文字の位置はここが正本
cd /home/user/gakugym-ai-vault/02_departments/manga/gpt_redraw
put() { mkdir -p ../names/ep0$1/gpt; cp $3 ../names/ep0$1/gpt/p$2.png; cp $3 ../names/ep0$1/pages/p$2.png; }
F="python3 finish_page.py"
GAMMA=0.7 $F ep01_p01_raw_clean.png ep01_p01_final.png 'box|828|30|ガクチカ。それは大学生にとって、就活の運命を決定づける重要な要素だ|22|9' 'box|28|30|バイト、サークル、留学、資格、研究——学生たちはキャンパスライフを謳歌しながらも、着々と、企業にアピールできる経験を積んでいく|20|11' >/dev/null && put 1 01 ep01_p01_final.png
BLACK=95 $F ep01_p11_raw.png ep01_p11_final.png 'balloon|770|745|やめてください!|30|4' >/dev/null && put 1 11 ep01_p11_final.png
$F ep01_p12_raw.png ep01_p12_final.png 'balloon|930|820|いいじゃん、ちょっとお茶するだけだって|28|8' 'balloon|95|840|お断りだって言ってるでしょ!|30|7' >/dev/null && put 1 12 ep01_p12_final.png
BLACK=95 $F ep01_p18_gpt_raw.png ep01_p18_final.png 'think|40|250|……今になって、震えがきた|26|8' 'balloon|290|700|だ、大丈夫!?|32|8' >/dev/null && put 1 18 ep01_p18_final.png
BLACK=120 GAMMA=0.6 $F ep01_p23_raw_b.png ep01_p23_final.png 'balloon|95|620|え、あ、はい……?|28|6' 'balloon|935|545|イヅルくん、今から時間ある?|28|7' 'balloon|920|1185|会ってほしい人たちがいるの!|30|7' >/dev/null && put 1 23 ep01_p23_final.png
BLACK=70 GAMMA=0.75 $F ep02_p20_raw.webp ep02_p20_final.png 'balloon|665|790|……で、次の冒険の作戦は? 誰が立てるんだよ|22|11' 'box|30|1070|一方その頃、勇者サークルでは——ある“穴”が、静かに広がり始めていた|22|10' >/dev/null && put 2 20 ep02_p20_final.png
GAMMA=0.75 $F ep03_p03_raw_fix.png ep03_p03_final.png 'balloon|930|185|勇者サークルさん。冒険許可書を見せてください|22|8' 'balloon|880|480|許可書? いつも顔パスだっただろ|22|6' 'balloon|920|875|いいえ。毎回、イヅルさんが前の週に申請してくれていましたよ|22|9' 'balloon|420|1112|ところでイヅルさんは本日どちらに?|22|6' >/dev/null && put 3 03 ep03_p03_final.png
GAMMA=0.75 $F ep03_p04_raw2.webp ep03_p04_final.png 'balloon|925|440|当日の申請だと、入れるのは第1層までですね|24|9' 'balloon|592|900|……チッ。第1層なんか、一瞬だ|22|6' 'box|35|1062|冒険許可書の申請も、これまでは誰かが黙ってやっていた|22|10' >/dev/null && put 3 04 ep03_p04_final.png
GAMMA=0.5 BLACK=50 $F ep04_p17_raw.webp ep04_p17_final.png 'think|45|590|……どいつもこいつも、CAPS、CAPSって|24|9' 'box|662|1038|あの冒険から、半年。勇者サークルに入部した新入生は、まだ一人もいない|22|11' >/dev/null && put 4 17 ep04_p17_final.png
GAMMA=0.6 BLACK=60 $F ep05_p04_raw.webp ep05_p04_final.png 'box|28|24|去年の春|24|8' 'think|405|505|頭の中に浮かんだアイデアを、ここでなら形にできる——そう思った|20|10' 'balloon|440|930|せいぜい、役に立てよ|24|6' >/dev/null && put 5 04 ep05_p04_final.png
GAMMA=0.6 BLACK=72 $F ep05_p05_raw.webp ep05_p05_final.png 'box|950|24|去年|24|8' 'balloon|860|790|戦えないくせに|26|4' 'balloon|500|1110|お前のくだらない妄想に付き合わされるのには、もううんざりだ|22|10' >/dev/null && python3 phone_screen.py ep05_p05_raw.webp ep05_p05_final.png 620 380 930 680 post && put 5 05 ep05_p05_final.png
GAMMA=0.5 BLACK=40 $F ep05_p11_raw.webp ep05_p11_final.png 'box|800|24|同じころ 勇者サークル|22|12' 'box|30|24|一方、その頃——勇者サークルは、落ちぶれる一方だった|22|9' >/dev/null && python3 fix_ep05_p11.py && put 5 11 ep05_p11_final.png
GAMMA=0.55 BLACK=50 $F ep05_p12_raw4.webp ep05_p12_final.png 'box|945|24|北の迷宮 第2層の手前|22|12' 'balloon|468|640|……ねえ、ここ、どこ?|20|6' 'balloon|955|880|薬も、もう残っていませんね|20|7' 'balloon|380|865|……今日は、ここまでだ。戻るぞ|22|7' 'box|28|1108|去年の今ごろは、第3層まで進んでいた。今年は半年たっても、まだ第2層にすら届いていない|20|12' >/dev/null && put 5 12 ep05_p12_final.png
GAMMA=0.6 BLACK=60 $F ep05_p14_raw.webp ep05_p14_final.png 'balloon|445|190|去年までは、毎回ちゃんと作戦があっただろ。どうやってたんだよ|22|11' 'oval|820|548|……地図も、作戦も、補給も、許可書も、公式SNSも。全部イヅルにやらせていたからな|16|10' 'box|954|732|去年|22|8' 'balloon|920|935|先輩、次の冒険の作戦、10個考えてきました!|17|8' 'balloon|165|1250|はいはい、使えそうなのがあったら、俺が使ってやるよ|20|9' >/dev/null && put 5 14 ep05_p14_final.png
GAMMA=0.6 BLACK=60 $F ep05_p20_raw.webp ep05_p20_final.png 'box|945|385|去年 北の迷宮 第3層|20|10' 'think|25|800|俺が見ていなかっただけで——ずっと、あいつが支えてたのか|20|10' 'balloon|105|1370|……だったら、取り返せばいい|24|7' >/dev/null && put 5 20 ep05_p20_final.png
GAMMA=0.6 BLACK=60 $F ep05_p21_raw.webp ep05_p21_final.png 'oval|440|200|あいつさえ戻れば、第4層だって行ける。魔王討伐の記録だって、塗りかえられる|19|9' 'oval|915|565|イヅルを、勇者サークルに連れ戻す|20|6' 'balloon|528|875|えっ、今さら!? 自分で追い出したのに!?|18|7' 'oval|92|950|……あら。ずいぶん都合のいいお話ですね。でも、わたくしは賛成です|15|12' 'oval|850|1310|……賛成だ。あいつは使える。便利な道具は、手元に置いておくべきだ|19|9' >/dev/null && put 5 21 ep05_p21_final.png
GAMMA=0.4 BLACK=30 $F ep05_p22_raw.webp ep05_p22_final.png 'oval|128|752|待ってろよ、イヅル。どれだけあがこうと、お前は俺らの都合のいいコマだ|18|9' 'box|862|945|かつての悪夢が、すぐそこまで迫っていることを、イヅルはまだ知らなかった|20|12' >/dev/null && GAMMA=0.55 BLACK=25 $F ep05_p22_raw.webp /tmp/p22dark.png 'box|862|945|かつての悪夢が、すぐそこまで迫っていることを、イヅルはまだ知らなかった|20|12' >/dev/null && python3 merge_ep05_p22.py /tmp/p22dark.png && put 5 22 ep05_p22_final.png
echo "GPTのページ 文字を入れ直し済み"
