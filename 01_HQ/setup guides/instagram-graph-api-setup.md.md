---
title: Instagram Graph API 連携手順書
status: 未着手
---

## 前提条件
- Instagramアカウントが「ビジネス」または「クリエイター」アカウントになっていること
- そのInstagramアカウントが、Facebookページと連携済みであること
  (未連携の場合: Instagramアプリの設定→アカウントの種類とツール→プロアカウントに切り替える/リンクされたアカウント から設定)

## 手順

1. **Meta for Developers にアクセス**し、Facebookアカウントでログイン
   https://developers.facebook.com/

2. 「アプリを作成」→ 用途は「その他」→ アプリタイプは「ビジネス」を選択し、アプリ名(例:gakugym-automation)を入力して作成

3. 作成したアプリのダッシュボードで、製品(Products)の中から**「Instagram」**を追加

4. 左メニューの「ツール」→「Graph APIエクスプローラ」を開く
   - 「Facebookアプリ」で今作ったアプリを選択
   - 「ユーザーまたはページ」→ ユーザートークンを選択
   - 「アクセス許可を追加」で以下をすべて選択:
     `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`
   - 「アクセストークンを生成」をクリックし、表示された**短期トークン**をコピー

4. 短期トークンを**長期トークン(60日間有効)**に交換する。ブラウザで下記URLの`<>`部分を埋めてアクセス:   (アプリID・App Secretはアプリの「設定→ベーシック」画面で確認できます)
   → 返ってきたJSONの`access_token`が長期トークン

5. **InstagramビジネスアカウントIDを取得**する。ブラウザで:   → 出てきたFacebookページの`id`を使って:   → `instagram_business_account.id` がInstagramビジネスアカウントID

6. GitHubの`gakugym-ai-vault`リポジトリの Settings → Secrets and variables → Actions で、以下2つを登録:
   - `INSTAGRAM_ACCESS_TOKEN`: 手順5の長期トークン
   - `INSTAGRAM_BUSINESS_ID`: 手順6のアカウントID

## 注意点
- 長期トークンは60日で失効するため、定期的な更新が必要(下記「更新方法」参照)
- 自分自身のアカウントに対してのみ使う場合、Meta社の正式な審査(App Review)なしでも動作します(アプリの管理者・開発者・テスターとして自分を登録していれば十分)
- 投稿は24時間あたり25件までの制限あり

## トークンの更新方法(60日ごとに必要)
手順5と同じ交換APIに、今持っている長期トークンをもう一度`fb_exchange_token`として渡すと、新しい60日間トークンが発行されます。