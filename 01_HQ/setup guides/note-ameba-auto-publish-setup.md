---
title: note/Ameba自動投稿 設定手順書(GitHub Actions secrets)
note: 2026-10-18 自動投稿は廃止(手動投稿に戻した)。ただしsecretsの NOTE_SESSION / AMEBA_SESSION は週次インサイト分析(ビュー数の取得)で引き続き使う。ログイン状態が切れたら「ログイン状態の保存(方式A)」の手順で再保存する
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

5. (2026-10-17追加)週次インサイト分析も初回は手動実行で確認する:
   - Actions タブ → **note-ameba-weekly-insights** → 「Run workflow」
   - `04_analytics/note_ameba/raw/<日付>.json` に記事ごとの数値が入っているか確認する
     (`articles` が空で `raw_text` だけの場合は、管理画面の構成が想定と違うということ。
     ログを貼ってこのセッションに相談してください)
   - 以後は毎週日曜05:00 JSTに自動実行され、月曜の記事生成に改善指示が反映される

6. (任意)見出し画像用の写真を登録する:
   `03_assets/images/note_ameba/` に写真を置き、同フォルダの `catalog.yml` に
   キーワード付きで登録すると、記事内容に合う写真が背景に使われる
   (未登録でも、明るいベージュ地+タイトル文字の見出し画像が自動生成されるので投稿は止まらない)

## 【2026-10-17追加・必須】ログイン状態の保存(方式A)
GitHub Actionsからのログインは、noteはロボット判定(reCAPTCHA)、Amebaはログインサーバーの
アクセス拒否で通りませんでした。そこで、**益田さんのPCで一度だけ手でログインし、その
ログイン状態をsecretsに保存**します。自動処理はログイン画面を通らずにこの状態を使います。
(ログイン状態は数週間〜数か月で切れます。切れると自動投稿が「ログイン状態が切れている可能性」
というエラーで止まるので、その時はこの手順をもう一度行ってください)

### 準備(初回のみ、15分ほど)
1. Node.js(LTS版)をインストールする: https://nodejs.org/ja → 「LTS」をダウンロードしてインストール
2. GitHubのこのリポジトリのページで **Code → Download ZIP** を押し、ダウンロードしたZIPを展開する
3. ターミナルを開く
   - Mac: 「ターミナル」アプリ / Windows: 「PowerShell」
4. 展開したフォルダの中の `tools/note_ameba` に移動する
   (例: `cd ~/Downloads/gakugym-ai-vault-main/tools/note_ameba`)
5. 以下を順に実行する:
   ```
   npm ci
   npx playwright install chromium
   ```

### noteのログイン状態を保存
1. `node save-session.js note` を実行する → ブラウザが開く
2. 開いたブラウザで、いつも通りメールアドレス・パスワードでnoteにログインする
3. ログインできたらターミナルに戻って **Enter** を押す
4. `note-session.txt` というファイルができるので、メモ帳等で開いて中身を**すべて**コピー
5. GitHubの Settings → Secrets and variables → Actions → **New repository secret**
   - Name: `NOTE_SESSION` / Secret: コピーした中身 を貼り付けて保存
6. **`note-session.txt` を削除する**(ログイン済みの状態そのものなので、人に渡さない)

### Amebaのログイン状態を保存
1. `node save-session.js ameba` を実行 → ブラウザで右上の「ログイン」からAmebaにログイン
2. ターミナルで Enter → できた `ameba-session.txt` の中身を secrets の **`AMEBA_SESSION`** に保存
3. **`ameba-session.txt` を削除する**

### 保存後の確認
Actions タブ → **note-ameba-probe** → Run workflow(投稿はしない確認用)を実行し、
このセッション(Claude Code)に「保存した」と伝えてください。ログが正常か確認します。
※ Amebaは、ログイン状態があってもGitHub Actionsからのアクセス自体を拒否する可能性があります。
その場合は方式B(益田さんのPCで実行)を改めて相談します。

## 承認の仕方(運用開始後)
下書きファイル(`02_departments/note_ameba/drafts/task-<date>-note-001.md`)の
frontmatterにある `status:` を `approved` に変更してコミット・pushするだけで、
次回のワークフロー実行時に自動投稿される。status を変更しなければ従来通り
自動投稿されないので、「この回は手動で投稿したい」場合はstatusを
`approved`にしなければよい。

## 画像・ハッシュタグの確認・変更(2026-10-17追加)
- 投稿時に自動で選ばれる。承認前に結果を見たい場合は、ローカルで
  `cd tools/note_ameba && npm ci && node select.js ../../02_departments/note_ameba/drafts/<ファイル名>`
- 特定の記事でタグ・画像を固定したい場合は、承認時にfrontmatterへ
  `hashtags: [子育て, 声かけ]` / `header_image: 03_assets/images/note_ameba/xxx.png` を追記する
- 投稿後、frontmatterの `publish_warnings` に「見出し画像のアップロード欄が見つかりません」
  「ハッシュタグ入力欄が見つかりません」等が残っていたら、記事自体は投稿済みなので
  画像・タグだけ手動で設定し、このセッションに相談してください(画面の変更に追従します)

## うまくいかない場合
- ログが「CAPTCHA/認証画面が検出されました」となる場合: 自動化では突破できない。
  該当回は手動でコピペ投稿し、頻発するようならこのセッションに相談してください
  (自動化を諦めて手動運用に戻す判断もあり得ます)
- ログインに失敗する場合: secretsの値(特にコピペ時の余分な空白・改行)を確認してください
- 投稿はされたが体裁が崩れている場合: note.comのエディタの仕様上、見出し・太字などの
  装飾は現状のスクリプトでは再現されない既知の制約です。都度手直しが必要な場合、
  自動化の費用対効果を再検討しましょう
