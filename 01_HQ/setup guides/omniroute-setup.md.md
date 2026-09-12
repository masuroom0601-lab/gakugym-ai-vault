---
title: Omniroute連携によるトークン使用量最適化 手順書
status: 未着手(要・益田さんのOmnirouteアカウント情報)
---

## 目的
GitHub Actions上のclaude-code-action、および手元のClaude Code CLIから送るリクエストを
Omniroute(LLMルーティング/プロキシサービス)経由にすることで、
「下書き生成のような軽い定型タスク」と「クリエイティブ制作・企画立案のような重いタスク」で
モデル・ルーティング先を出し分け、Claude Code Pro契約の範囲内でトークン消費を最小化する。

## 前提として必要なもの(益田さんが用意するもの)
- Omnirouteのアカウント、およびAPIキー
- OmnirouteのAPIエンドポイントURL(Anthropic API互換のプロキシURLを想定)
- Omniroute側で「Claude Code Pro経由のモデル」と「軽量モデル/低コストモデルへのフォールバック」を
  どうルーティングするか(部署ごとにモデルを分けたい場合はルール名も)

上記が無いと以降の手順を完了できないため、まずはOmniroute側の管理画面で
APIキーとエンドポイントURLを発行してください。

## 手順(GitHub Actions側)

1. GitHubリポジトリの Settings → Secrets and variables → Actions で、以下を登録する:
   - `OMNIROUTE_API_KEY`: Omnirouteで発行したAPIキー
   - `OMNIROUTE_BASE_URL`: OmnirouteのAPIエンドポイントURL(例: `https://api.omniroute.example.com`)

2. 各ワークフロー(.github/workflows/*.yml)の `anthropics/claude-code-action@v1` ステップに、
   環境変数として以下を追加する(claude_code_oauth_tokenと併用可能かはOmniroute側の
   ドキュメントで要確認。Anthropic API互換プロキシの場合は`ANTHROPIC_BASE_URL`を
   上書きする方式が一般的):
   ```yaml
   env:
     ANTHROPIC_BASE_URL: ${{ secrets.OMNIROUTE_BASE_URL }}
     ANTHROPIC_API_KEY: ${{ secrets.OMNIROUTE_API_KEY }}
   ```
   ※ `claude_code_oauth_token` と `ANTHROPIC_API_KEY` は同時に指定できない場合があるため、
   Omniroute経由に切り替える部署のワークフローから段階的に移行し、
   移行後は動作確認(workflow_dispatchで手動実行)を必ず行う。

## 手順(ローカルのClaude Code CLI側)

1. `~/.claude/settings.json` または環境変数で以下を設定する:
   ```
   ANTHROPIC_BASE_URL=https://api.omniroute.example.com
   ANTHROPIC_API_KEY=<Omnirouteで発行したAPIキー>
   ```
2. `claude` コマンドを実行し、モデル切り替えが正常に動作するか確認する。

## 部署ごとのモデル出し分け案(コスト最適化の考え方)
- 軽量・定型タスク(X/Threads下書き、LINE選定、日次集計): 低コストモデルにルーティング
- 品質が重要なタスク(note/Ameba長文記事、クリエイティブのコピー、企画・分析): 高性能モデルを維持
- Omniroute側でルーティングルールを分けられる場合、ワークフローごとに
  `OMNIROUTE_ROUTE` のようなラベル用の環境変数を渡し、Omniroute側でモデルを振り分ける
  (具体的なパラメータ名はOmnirouteの仕様に依存するため、導入時に確認・追記すること)

## 未確定事項(要・益田さんの追記)
- Omnirouteの正式なAPI仕様(エンドポイント形式、認証方式、Anthropic API互換の程度)
- claude-code-actionがOMNIROUTE経由の非公式エンドポイントを許容するかどうかの動作確認結果
- 上記が判明次第、本手順書を更新し、01_HQ/roadmap.md のPhase1チェックリストを更新すること
