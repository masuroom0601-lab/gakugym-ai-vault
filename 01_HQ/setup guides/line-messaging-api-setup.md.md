---
title: LINE Messaging API(公式アカウント配信)連携手順書
status: 未着手
---

## 先に知っておいてほしい重要な制約(着手前に必読)
LINE公式アカウントの無料プラン(コミュニケーションプラン)は、**月間の無料メッセージ数に上限**
があります(目安200通/月。最新の上限・料金は開設時にLINE Official Account Managerで
必ず確認してください)。**この上限は「配信1回」ではなく「配信×友だち数」でカウントされる**
ため、たとえば友だちが100人いる状態で1回配信すると、その時点で月間上限の半分を消費します。
3日に1回(月10回程度)配信する今の設計だと、友だちが**20人を超えたあたりから無料枠を
使い切る可能性**が出てきます。

そのため、このリポジトリの配信スクリプト(`tools/line/broadcast.js`)には、
**今月すでに何通分を消費したかを`04_analytics/line-message-usage.json`で追跡し、
月間上限を超えそうな配信は自動的に見送る安全装置**を組み込んであります
(見送られた場合はdraftファイルにコメントが追記され、配信は行われません)。
上限に達したら、翌月まで待つか、有料プランへの切り替えを検討してください
(有料プランは「追加予算はかけない」という運用方針に影響するため、切り替える場合は
その判断自体を益田さんが行ってください)。

## 前提条件
- LINE公式アカウントを開設済みであること(まだの場合は https://www.lycbiz.com/jp/service/line-official-account/ から)

## 手順

1. **LINE Developers コンソール** にアクセスし、LINEアカウントでログイン
   https://developers.line.biz/console/

2. 既存のLINE公式アカウントに対応する「プロバイダー」を選択(無ければ新規作成)

3. 「新規チャネル作成」→ **「Messaging API」** を選択し、
   開設済みのLINE公式アカウントと連携する形でチャネルを作成

4. 作成したチャネルの「Messaging API設定」タブを開く
   - 下部の「チャネルアクセストークン(長期)」の「発行」ボタンをクリックし、トークンを発行する
     (**この長期トークンには有効期限がなく、明示的に再発行するまで使い続けられる**。
     Instagram/Threads/TikTok/YouTubeのような定期更新は不要)
   - 「Webhookの利用」はオフのままでよい(今回は配信のみで、受信は使わない)
   - 「応答メッセージ」「あいさつメッセージ」は、LINE Official Account Manager側の
     設定に干渉しないよう、必要に応じてオフにしておく

5. GitHubの`gakugym-ai-vault`リポジトリの Settings → Secrets and variables → Actions で、
   以下を登録:
   - `LINE_CHANNEL_ACCESS_TOKEN`: 手順4で発行した長期トークン

6. (任意)月間メッセージ上限を既定の200から変更したい場合は、Secrets or Variablesに
   `LINE_MONTHLY_QUOTA` を追加で登録する(数値のみ)。

## 配信の仕組み
- `tools/line/broadcast.js` が `02_departments/line/drafts/` 内で
  frontmatterの `status: approved` になっているファイルを見つけると、
  「## 配信本文」見出し直後のコードブロックの中身をそのままLINEの
  ブロードキャストAPI(`POST https://api.line.me/v2/bot/message/broadcast`)で
  全友だちに配信する
- 配信に成功すると、ファイルは自動的に `published/` フォルダへ移動され、
  frontmatterに `status: published` と配信日時が記録される
- 配信に失敗した場合(トークン誤り、月間上限超過等)は、ファイルは `drafts/` に残り、
  「## 配信担当コメント」に理由が追記される(再承認や設定見直しが必要なサイン)

## 誤配信防止の仕組み
- **`status: approved` になっているファイルだけが配信対象**。校正担当が
  `status: review` にしても、益田さんが明示的に `approved` に変更しない限り配信されない
- 配信は取り消せないため、承認は必ず本文を読んでから行うこと
  (brand-guide.md「6. AI生成コンテンツの扱い」に基づく必須ステップ)

## トラブルシューティング
- 配信されない場合、まず `LINE_CHANNEL_ACCESS_TOKEN` がGitHub Secretsに
  正しく登録されているか確認する
- 友だち数の取得(月間上限判定に使用)に失敗した場合は安全側の仮定値で判定するため、
  想定より早く「上限超過につき見送り」と表示されることがある。その場合は
  LINE Official Account Managerで実際の友だち数・当月消費数を確認すること
