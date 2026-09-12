---
title: お問い合わせフォーム(Formspree+reCAPTCHA)設定手順書
status: 未着手
---

## 前提
`docs/contact.html` は静的HTMLのみで、フォーム送信を受け取るサーバーを
このリポジトリ自体は持っていません(GitHub Pagesは静的ホスティングのみ)。
そのため、無料の外部フォーム送信サービスと画像認証(CAPTCHA)を連携させます。

## 手順1: Formspreeでフォーム送信先を作る
1. https://formspree.io/ でアカウント作成(無料プランは月50件まで無料)
2. 「New Form」から新規フォームを作成し、通知を受け取りたいメールアドレスを設定
3. 発行された フォームID(`https://formspree.io/f/xxxxxxxx` の `xxxxxxxx` 部分)を控える
4. `docs/contact.html` 内の以下の行を書き換える:
   ```
   <form class="contact-form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
   ```
   `YOUR_FORM_ID` を手順3で控えたIDに差し替える

## 手順2: Google reCAPTCHA(画像認証)を設定する
1. https://www.google.com/recaptcha/admin にアクセスし、Googleアカウントでログイン
2. 「reCAPTCHA v2」の「チェックボックス」タイプを選択し、
   ドメイン欄に取得した独自ドメイン(まだ無ければ `<GitHubユーザー名>.github.io` でも可、
   後で独自ドメインを追加登録できる)を入力して登録
3. 発行された「サイトキー」を控える
4. `docs/contact.html` 内の以下のコメントアウトを解除し、
   `YOUR_RECAPTCHA_SITE_KEY` をサイトキーに差し替える:
   ```html
   <div class="g-recaptcha" data-sitekey="YOUR_RECAPTCHA_SITE_KEY"></div>
   <script src="https://www.google.com/recaptcha/api.js" async defer></script>
   ```
5. Formspree側の管理画面で「reCAPTCHA連携」をオンにし、
   手順3の「シークレットキー」を登録する(Formspreeがサーバー側で検証してくれる)

## 手順3: 動作確認
1. 実際にサイトからテスト送信し、Formspreeに登録したメールアドレスに
   通知が届くか確認する
2. 画像認証を突破しないと送信できないことも確認する

## 注意点
- Formspreeの無料プランの上限(月50件)を超えそうな場合は、
  他の無料フォームサービス(例: Googleフォームを埋め込む方式)への切り替えも検討する
  (その場合はフォーム項目のカスタマイズ性が下がる点に留意)
- フォームの必須項目(お名前・ふりがな・メール・お問い合わせ内容)は
  `docs/contact.html`側の `required` 属性で制御している。項目を増減する場合は
  Formspree側の管理画面でも受信メールのフォーマットが変わることがあるので確認すること
