---
title: YouTube Data API v3(Shorts投稿)連携手順書
status: 未着手
---

## 先に知っておいてほしい重要な制約(着手前に必読)
Googleの OAuth同意画面が「**テスト中(Testing)**」ステータスのままだと、
発行されるリフレッシュトークンが**7日で失効**します。7日ごとに手動で再認可するのは
自動化の意味がないため、実運用に乗せるには同意画面を「**本番公開(In production)**」に
する必要があります。`youtube.upload` は「機密性の高いスコープ(Sensitive scope)」に
分類され、本番公開には**Googleによる審査(OAuth確認)**が必要です。審査には通常、
プライバシーポリシーページのURL・アプリの説明・実際の認可フロー画面を撮影した
デモ動画等の提出が必要で、数日〜数週間かかることがあります
(プライバシーポリシーページは、Phase4で自社HPを作った後にそこへ設置する想定)。

**したがって、YouTube Shorts自動投稿は本ロードマップの中でも実現までのリードタイムが
最も長い部類です。早めに申請だけ着手し、承認が下りるまではInstagram/TikTok同様、
動画ファイルの自動生成までに留めて手動投稿してください。**

## 前提条件
- Googleアカウント(学ジム用のYouTubeチャンネルに紐づくもの)
- Google Cloud Consoleへのアクセス

## 手順

1. **Google Cloud Console** にアクセスし、新規プロジェクトを作成(例: gakugym-automation)
   https://console.cloud.google.com/

2. 「APIとサービス」→「ライブラリ」から **「YouTube Data API v3」** を検索して有効化する

3. 「APIとサービス」→「OAuth同意画面」を設定
   - User Type: 外部(External)
   - アプリ名・サポートメール・デベロッパー連絡先を入力
   - スコープに `https://www.googleapis.com/auth/youtube.upload` を追加
   - テストユーザーに、学ジムチャンネルを管理するGoogleアカウントを追加
     (この時点では「テスト中」ステータスのままでOK。動作確認を先に行う)

4. 「認証情報」→「認証情報を作成」→「OAuthクライアントID」
   - アプリケーションの種類: 「デスクトップアプリ」を選択(GitHub Actions上で
     コンソール的にトークン交換するため、リダイレクトURIの制約が緩いこちらが扱いやすい)
   - 作成後、クライアントIDとクライアントシークレットを控える

5. 初回のみ、ローカルまたは手元のブラウザでOAuth認可フローを実行し、
   リフレッシュトークンを取得する(Googleの `google-auth-oauthlib` 等のライブラリ、
   または手動でauthorization codeを取得してトークン交換APIを叩く形でよい):
   ```
   認可URL: https://accounts.google.com/o/oauth2/v2/auth?
     client_id=<Client ID>&redirect_uri=<設定したリダイレクトURI>
     &response_type=code&scope=https://www.googleapis.com/auth/youtube.upload
     &access_type=offline&prompt=consent
   ```
   ```
   POST https://oauth2.googleapis.com/token
   client_id=<Client ID>&client_secret=<Client Secret>
   &code=<認可コード>&grant_type=authorization_code&redirect_uri=<リダイレクトURI>
   ```
   レスポンスの `refresh_token` を控える
   (**同意画面が「テスト中」の間は、このrefresh_tokenが7日で失効する点に注意**)

6. GitHubの`gakugym-ai-vault`リポジトリの Settings → Secrets and variables → Actions で、以下を登録:
   - `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET`: 手順4の認証情報
   - `YOUTUBE_REFRESH_TOKEN`: 手順5のリフレッシュトークン

7. **OAuth同意画面を「本番公開」にするための審査を申請する**(実運用に必須)
   - プライバシーポリシーのURL(Phase4のHP完成後にそこへ設置。それまでは仮のページでも可)
   - アプリの実際の利用方法を示すデモ動画(認可フローの画面録画)
   - Googleの審査チームへ提出し、承認を待つ

## アップロードの仕組み(YouTube Data API v3)
1. `POST https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status`
   にリフレッシュトークンから発行したアクセストークンを付けてリクエスト
   - `snippet.title` / `snippet.description` / `snippet.tags` を指定
   - Shorts判定はYouTube側が動画の縦横比(9:16)・尺(60秒以内)から自動で行うため、
     アップロード時に「これはShortsです」と明示するパラメータは不要
     (説明文に `#Shorts` を含めることが推奨されている)
   - `status.privacyStatus` は最初は `private` または `unlisted` にして
     益田さんが最終確認してから `public` に切り替える運用を推奨
2. 動画本体はマルチパートまたはresumable uploadでアップロードする

## 注意点
- 1日あたりのAPIクォータ(デフォルト10,000ユニット、動画アップロードは1回1,600ユニット消費)
  があるため、1日1本程度の運用であれば問題にならない
- タイトル100文字、説明5,000文字などYouTube側の上限は緩いが、
  Instagram/TikTok部署のトーン・NGルールはそのまま踏襲すること
