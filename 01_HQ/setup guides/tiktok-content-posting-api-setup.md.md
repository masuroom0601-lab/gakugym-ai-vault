---
title: TikTok公式API連携手順書(分析データ取得+Content Posting API)
status: 分析データ取得は未着手、投稿(Content Posting API)も未着手
---

## 2026-10-21追記: 分析データ取得が優先タスクになった
益田さんより、Instagramの「エルグラム」と同様にTikTok側(`massu_gakugym`)の
フォロワー伸び率・プロフィール文・動画ごとの再生数も自分で分析できるようにしたい、
との依頼があった。TikTokには公式のDisplay APIがあり、`user.info.basic` /
`user.info.stats` / `user.info.profile` / `video.list` スコープを使えば、
**アプリ監査(App Audit)を通さなくても、開発者自身(テスターとして登録した
`massu_gakugym`アカウント)の情報は読み取れる**(監査が必要なのは「不特定多数への
公開投稿」であり、「自分のアカウントの読み取り」には監査は不要)。

つまり、下記の手順6で取得するOAuthトークン1つで、
**(A) 分析データの取得**(今すぐ使える)と**(B) 投稿(Content Posting API)**
(監査が通るまでは非公開投稿のみ)の両方をまとめて準備できる。
手順6のスコープ文字列に分析用スコープを追加したので、**まずは手順を最後まで
一通り実施し、GitHub Secretsに登録してほしい**。登録が終われば、
`.github/workflows/tiktok-weekly-analytics-fetch.yml`が毎週日曜04:50 JST頃に
自動で`04_analytics/manual-input/<週の月曜日>.md`のTikTok欄(フォロワー数・
動画ごとの再生数)を更新するようになる(詳細は本ファイル下部「分析データの取得」節)。

## 先に知っておいてほしい重要な制約(着手前に必読)
TikTok for Developersでアプリを新規作成した直後は「**未監査(unaudited)**」状態で、
Content Posting API経由で投稿した動画は**投稿者本人にしか見えない(非公開)モード**でしか
公開できません。学ジムの公式アカウントとして一般公開するには、TikTok側の
**アプリ監査(App Audit)**を通す必要があり、これには数日〜数週間かかることがあります。
つまり「トークンさえ取れればすぐ自動投稿できる」わけではないので、
**この手順は早めに着手し、監査待ちの間は自動生成した動画を益田さんが手動投稿する**
運用を継続してください(instagram_tiktok/department.md準拠)。

## 前提条件
- TikTokの公式(ビジネス)アカウントを保有していること
- 電話番号・メールアドレスでのTikTok for Developersアカウント登録

## 手順

1. **TikTok for Developers** にアクセスし、アカウント登録
   https://developers.tiktok.com/

2. 「Manage apps」→「Create an app」で新規アプリを作成
   - アプリ名(例: gakugym-automation)を入力
   - カテゴリ等の必須項目を入力

3. アプリのダッシュボードで、Productsから **「Content Posting API」** を追加
   - 併せて「Login Kit」も有効化する(OAuth認証に必要)

4. 「Login Kit」の設定画面で、リダイレクトURI(認証後に戻ってくるURL)を登録する
   - ローカルで一度だけ認証コードを受け取るための簡易ページ、または
     `https://localhost/callback` 等、自分で受け取れるURLを設定

5. 対象のTikTokアカウントを、アプリの「テスターとして追加」する
   (審査前は登録したテスターアカウントでのみ動作確認できる)

6. OAuth認可フローを実行し、認可コードを取得する。ブラウザで下記URLの`<>`部分を埋めてアクセス:
   ```
   https://www.tiktok.com/v2/auth/authorize/?client_key=<Client Key>&scope=user.info.basic,user.info.stats,user.info.profile,video.list,video.publish&response_type=code&redirect_uri=<設定したリダイレクトURI>&state=<任意の文字列>
   ```
   (**2026-10-21更新**: 分析データ取得用に`user.info.stats`・`user.info.profile`・
   `video.list`を追加した。アプリのダッシュボードで該当スコープが有効化されていないと
   認可画面に出てこないので、手順3で「Content Posting API」を追加した際、
   併せて「Login Kit」側のスコープ一覧にこれらが含まれているか確認すること)
   認可後、リダイレクト先のURLに `code=` パラメータが付与されるのでコピーする

7. 取得した認可コードを、アクセストークン+リフレッシュトークンに交換する:
   ```
   POST https://open.tiktokapis.com/v2/oauth/token/
   Content-Type: application/x-www-form-urlencoded

   client_key=<Client Key>
   &client_secret=<Client Secret>
   &code=<手順6の認可コード>
   &grant_type=authorization_code
   &redirect_uri=<設定したリダイレクトURI>
   ```
   レスポンスの `access_token`(有効期限**24時間**)と `refresh_token`(有効期限**365日**)を控える

8. GitHubの`gakugym-ai-vault`リポジトリの Settings → Secrets and variables → Actions で、以下を登録:
   - `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET`: アプリの認証情報
   - `TIKTOK_REFRESH_TOKEN`: 手順7のリフレッシュトークン
     (access_tokenは24時間しか持たないため保存不要。実行のたびにrefresh_tokenから都度発行する)

## トークンの運用について(最重要)
- **アクセストークンは24時間で失効するため、GitHub Actions実行のたびに
  リフレッシュトークンを使って新しいアクセストークンを発行する**必要がある
  (Instagram/Threadsの「長期トークンを60日おきに手動更新」とは運用方式が異なる)
- リフレッシュトークン自体も365日で失効するため、年1回は手動での再認可(手順6〜7)が必要
  (統括担当のエスカレーション対象に追加すること)
- リフレッシュAPI:
  ```
  POST https://open.tiktokapis.com/v2/oauth/token/
  grant_type=refresh_token&client_key=<Client Key>&client_secret=<Client Secret>&refresh_token=<Refresh Token>
  ```

## 投稿の仕組み(Content Posting API)
1. `POST /v2/post/publish/video/init/` で投稿を初期化(動画情報・公開範囲を指定)
2. レスポンスで返る `upload_url` に、動画ファイルをチャンクアップロード
3. 未監査アプリの場合、`privacy_level` は `SELF_ONLY`(自分のみ閲覧可)固定になる
   (監査通過後に `PUBLIC_TO_EVERYONE` 等が選択可能になる)

## 注意点
- 動画のみサポート(2024年以降、写真投稿=Content Posting APIの「PHOTO」もあるが、
  学ジムの用途はリール動画の横展開のため、当面は動画投稿のみ実装する)
- キャプション文字数上限やハッシュタグの扱いは、Instagram/TikTok部署の
  department.mdのルールをそのまま踏襲する(TikTok固有の追加制約が判明次第、追記する)

## 分析データの取得(Display API、2026-10-21新設)
手順1〜8(スコープに`user.info.stats`等を含めたOAuth認可・GitHub Secrets登録)が
終わっていれば、追加の作業なしで以下が動く。

- `tools/tiktok_analytics/fetch.js`: `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET` /
  `TIKTOK_REFRESH_TOKEN` を使ってアクセストークンを都度発行し、
  - `GET /v2/user/info/`(`user.info.stats`・`user.info.profile`スコープ)で
    フォロワー数・いいね合計・動画本数・プロフィール文(bio_description)を取得
  - `POST /v2/video/list/`(`video.list`スコープ)で直近の動画(最大40件)の
    再生数・いいね数・コメント数・シェア数を取得し、今週投稿された分だけに絞り込む
  - `04_analytics/manual-input/<今週の月曜日>.md`の「フォロワー数」表のTikTok行と
    「Instagram/TikTok 投稿ごとのエンゲージメント」表に書き込む
  (Instagramの「エルグラム」と違い「保存」件数は公式APIで取得できないため、
  その列は「ー」のままになる)
- `.github/workflows/tiktok-weekly-analytics-fetch.yml`: 毎週日曜04:50 JST頃に
  上記スクリプトを実行し、変更があればコミット・プッシュする
  (claude.aiのRoutine/コネクタ連携は不要。GitHub Secretsのトークンだけで完結する
  ため、エルグラムの時に起きた「Routineが益田さんの画面に出てこない」問題は発生しない)
- GitHub Secretsにトークンを登録する前でも、このワークフローは「トークン未設定のため
  スキップしました」とログを出して正常終了するだけなので安全に有効化しておける
- 取得したデータは`02_departments/analytics/department.md`の「データ取得方法」に
  準じて`analytics-weekly-report.yml`に取り込まれる(Instagramと同じ経路)
