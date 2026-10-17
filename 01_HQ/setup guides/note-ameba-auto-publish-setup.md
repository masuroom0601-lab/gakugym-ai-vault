---
title: note/Ameba自動投稿 設定手順書(GitHub Actions secrets)
status: 未着手(益田さんの作業が必要)
---

## 背景
2026-10-17、益田さんのご依頼で、note/Amebaブログへの投稿を手動コピペから
自動化する仕組みを構築した(詳細: `02_departments/note_ameba/department.md`)。
note/Amebaとも投稿用の公式APIが存在しないため、Playwrightでブラウザ操作
(ログイン→記事作成→本文貼り付け→公開)を代行する方式にしている。

**重要な注意**: これは非公式のブラウザ自動操作であり、各サービスの利用規約上の
グレーゾーンである可能性がある。また、CAPTCHA表示やサイト側のUI変更で
失敗する可能性が十分にある(失敗しても下書きは消えず手動投稿にフォールバックできる
設計にしてあるが、「必ず動く」ことは保証できない)。

## 前提
- note.comのアカウント(ログイン用メールアドレス・パスワード)
- AmebaIDのアカウント(ログインID・パスワード・ブログID)
- このGitHubリポジトリ(`masuroom0601-lab/gakugym-ai-vault`)の
  Settings → Secrets and variables → Actions を開ける権限

## 手順

1. GitHubリポジトリの **Settings → Secrets and variables → Actions → Secrets** を開く

2. 以下のsecretsを追加する(「New repository secret」から1つずつ):

   | Name | 値 |
   |---|---|
   | `NOTE_EMAIL` | note.comのログイン用メールアドレス |
   | `NOTE_PASSWORD` | note.comのログインパスワード |
   | `AMEBA_ID` | AmebaIDのログインID |
   | `AMEBA_PASSWORD` | AmebaIDのログインパスワード |
   | `AMEBA_BLOG_ID` | ameblo.jp/<ここ> のブログID部分(例: ameblo.jp/gakugym なら `gakugym`) |

   note/Amebaのどちらか一方だけ先に設定することも可能(未設定の方はスキップされ、
   自動投稿エラーにはならない)。

3. 初回は必ず手動実行で動作確認する:
   - GitHubリポジトリの **Actions** タブ → 左メニューから
     **note-ameba-auto-publish** を選択
   - 「Run workflow」ボタンから手動実行(workflow_dispatch)
   - 実行ログを確認し、note.com/Amebaそれぞれで実際に記事が正しく
     投稿されたか(タイトル・本文・体裁)を**人の目で必ず確認する**
   - 問題があれば `02_departments/analytics` チームへの報告ではなく、
     このセッション(Claude Code)に実行ログを貼って相談してください

4. 動作確認が取れたら、通常運用として以下のタイミングで自動実行される:
   - `02_departments/note_ameba/drafts/` への変更がmainにpushされた時
   - 毎日06:20 JST相当のフォールバック

## 承認の仕方(運用開始後)
下書きファイル(`02_departments/note_ameba/drafts/task-<date>-note-001.md`)の
frontmatterにある `status:` を `approved` に変更してコミット・pushするだけで、
次回のワークフロー実行時に自動投稿される。status を変更しなければ従来通り
自動投稿されないので、「この回は手動で投稿したい」場合はstatusを
`approved`にしなければよい。

## うまくいかない場合
- ログが「CAPTCHA/認証画面が検出されました」となる場合: 自動化では突破できない。
  該当回は手動でコピペ投稿し、頻発するようならこのセッションに相談してください
  (自動化を諦めて手動運用に戻す判断もあり得ます)
- ログインに失敗する場合: secretsの値(特にコピペ時の余分な空白・改行)を確認してください
- 投稿はされたが体裁が崩れている場合: note.comのエディタの仕様上、見出し・太字などの
  装飾は現状のスクリプトでは再現されない既知の制約です。都度手直しが必要な場合、
  自動化の費用対効果を再検討しましょう
