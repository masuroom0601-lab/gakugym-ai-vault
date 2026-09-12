---
title: Instagram API 連携手順書
status: 進行中(益田さんが「Instagramログインによる API設定」で作業中)
---

## 2025年更新: 新しい「Instagram API with Instagram Login」を使う
Metaは2024年7月に、**Facebookページとの連携が不要な新しいInstagram API**
(Instagramログインによる API設定/Instagram API with Instagram Login)を公開しました。
学ジムのユースケース(自分のInstagramビジネスアカウントへの自動投稿)には
こちらのほうがシンプルなので、**こちらを本手順の正式ルートとします**
(旧来のFacebookページ経由のGraph APIの手順は末尾に「旧手順(参考)」として残しています。
ハッシュタグ検索やインサイト取得など一部機能は旧来のFacebookログイン経由でないと
使えない場合があるため、必要になったらそちらを参照してください)。

## 前提条件
- Instagramアカウントが「ビジネス」または「クリエイター」アカウントになっていること
- Facebookページとの連携は**不要**(このAPIの利点)

## 手順(Instagramログインによる API設定)

1. **Meta for Developers** にアクセスし、Facebookアカウントでログイン
   https://developers.facebook.com/

2. 「アプリを作成」→ アプリ名(例: gakugym-automation-IG)を入力して作成

3. 作成したアプリのダッシュボードで、製品(Products)から**「Instagram」**を追加

4. 左メニューから「Instagramログインによる API設定」を開く
   (「Facebookログインによる API設定」の方ではないので注意。この2つは別物)

5. 「ユースケースをカスタマイズ」画面で、**必要なアクセス許可を追加する**。
   画面には複数の機能ブロック(メッセージ/コンテンツ公開/コメント管理 等)が
   並んでいるはずです。**学ジムの用途(自動投稿)では「コンテンツ公開」ブロックが
   本命**なので、そちらを開いて以下のスコープを有効にしてください:
   - `instagram_business_basic`(プロフィール情報の取得。ほぼ必須で自動的に含まれる)
   - `instagram_business_content_publish`(投稿機能。これが無いと投稿できない)
   - 「メッセージ」ブロック(`instagram_business_manage_messages`等)は
     DM自動応答等をやらない限り**不要**なので、追加しなくてよい

6. 自分自身のInstagramアカウントを「テスター」として追加する
   (アプリの「ユーザー」または「役割」設定画面から。個人利用の範囲であれば、
   これでMetaの正式審査=App Reviewなしで動作します)

7. OAuth認可フローを実行し、認可コードを取得する。ブラウザで下記URLの
   `<>`部分を埋めてアクセス:
   ```
   https://api.instagram.com/oauth/authorize?
     client_id=<Instagramアプリ ID>
     &redirect_uri=<設定したリダイレクトURI>
     &scope=instagram_business_basic,instagram_business_content_publish
     &response_type=code
     &state=<任意の文字列>
   ```
   テスターアカウントでログイン・許可すると、リダイレクト先URLに
   `code=` パラメータが付与されるのでコピーする

8. 認可コードを短期アクセストークンに交換する:
   ```
   POST https://api.instagram.com/oauth/access_token
   client_id=<Instagramアプリ ID>
   &client_secret=<Instagram app secret>
   &grant_type=authorization_code
   &redirect_uri=<リダイレクトURI>
   &code=<手順7の認可コード>
   ```
   レスポンスに `access_token` と `user_id` が含まれる
   (**この`user_id`が投稿先アカウントのID。Facebookページ経由の
   ビジネスアカウントID取得は不要**)

9. 短期トークンを**長期トークン(60日間有効)**に交換する:
   ```
   GET https://graph.instagram.com/access_token
     ?grant_type=ig_exchange_token
     &client_secret=<Instagram app secret>
     &access_token=<手順8の短期トークン>
   ```

10. GitHubの`gakugym-ai-vault`リポジトリの Settings → Secrets and variables → Actions で、
    以下2つを登録:
    - `INSTAGRAM_ACCESS_TOKEN`: 手順9の長期トークン
    - `INSTAGRAM_USER_ID`: 手順8の`user_id`

## 投稿の仕組み(参考。自動投稿ワークフロー実装時に使用)
1. メディアコンテナを作成:
   `POST https://graph.instagram.com/v21.0/{user_id}/media`
   パラメータ: `image_url`(公開URLの画像)、`caption`、`access_token`
2. 10秒程度待ってから公開:
   `POST https://graph.instagram.com/v21.0/{user_id}/media_publish`
   パラメータ: `creation_id`(手順1のレスポンスID)、`access_token`
3. キャプションは最大2,200文字、ハッシュタグは最大30個(ただしdepartment.mdの
   ルールでは最大5個に絞っている)

## 注意点
- 長期トークンは**60日**で失効する。50日を超えたら更新すること
  (hq_director/department.mdのエスカレーション対象に追加済み)
- 自分自身のアカウントに対してのみ使う場合、Meta社の正式審査(App Review)なしで動作する
  (アプリの管理者・開発者・テスターとして自分を登録していれば十分)
- 投稿は24時間あたり25件までの制限あり
- 動画・カルーセル(複数画像)投稿は`media`作成時のパラメータが異なる
  (`media_type=CAROUSEL`等。実装時に公式ドキュメントで最新仕様を確認すること)

## トークンの更新方法(60日ごとに必要)
手順9と同じ交換エンドポイントに、今持っている長期トークンを
`grant_type=ig_refresh_token`として渡すと、新しい60日間トークンが発行される:
```
GET https://graph.instagram.com/refresh_access_token
  ?grant_type=ig_refresh_token
  &access_token=<現在の長期トークン>
```

---

## 旧手順(参考): Facebookログインによる API設定(Facebookページ経由)
ハッシュタグ検索・一部のインサイト取得など、Instagramログイン版にまだ無い機能が
必要になった場合はこちら。Facebookページとの連携が必須。

1. Instagramビジネスアカウントを、Facebookページと連携させる
   (Instagramアプリの設定→アカウントの種類とツール→プロアカウントに切り替える/
   リンクされたアカウント から設定)
2. Meta for Developersでアプリを作成し、「Facebookログインによる API設定」を使う
3. 「ツール」→「Graph APIエクスプローラ」で、以下のアクセス許可を選択してトークン発行:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
   `pages_read_engagement`, `business_management`
4. 短期トークンを長期トークン(60日)に交換(`fb_exchange_token`)
5. FacebookページIDから`instagram_business_account.id`を取得
   (これが投稿先のInstagramビジネスアカウントID)
