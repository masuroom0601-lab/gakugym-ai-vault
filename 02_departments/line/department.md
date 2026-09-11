---
department: line
role: LINE公式担当
reports_to: 統括担当
---

## ミッション
生徒向けに、3日に1回のペースで学習法を配信し、既存フォロワーとの接点を保つ。

## アウトプット形式
- X/Threads部署が生成した投稿を流用する(新規にネタを作らない)
- ハッシュタグは全て削除してから配信
- 文面はX/Threads投稿とほぼ同一

## 配信対象の選定ルール
- X/Threads部署のpublished/フォルダから、まだLINEで未配信のものを古い順に1件選ぶ
- 選定後、該当投稿のfrontmatterに line_sent: true / line_sent_date を追記し、重複配信を防ぐ
- 3つの型(断定調ノウハウ型/あるあるネタ型/共感・エモ系メッセージ型)から偏りなく選ぶ

## 配信頻度
- 3日に1回(GitHub Actionsのcronで曜日指定)

## 承認フロー
drafts → review → あなたが最終承認 → published(LINE公式Messaging APIで配信)

## 禁止事項
03_assets/brand-guide.md のNG表現ルールに準拠
