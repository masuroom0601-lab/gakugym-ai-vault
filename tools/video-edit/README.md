# 動画自動編集パイプライン(文字起こし → 字幕焼き込み)

音声/動画を渡すと、OpenAI Whisper APIで文字起こしし、Remotionで
日本語として自然な位置で改行された字幕を動画に焼き込む、という流れのための
一式です。実際の合成テンプレートは `tools/remotion-sample/src/Captions/` にあります。

## 構成

- `mcp.whisper.json.example` — `mcp-server-whisper` というMCPサーバーの設定テンプレート。
  Whisper文字起こしをClaude Codeのツールとして使えるようになる
  (ローカルモデルではなくOpenAIのWhisper APIを呼ぶ方式。モデルの事前ダウンロードは不要)。
  **あえて`.mcp.json`という名前にしていません** — リポジトリ直下の`.mcp.json`は
  このリポジトリの日次自動実行ワークフロー(analytics/hq-secretary等、GitHub Actions上の
  Claude Code Action)からも読み込まれてしまい、`OPENAI_API_KEY`未設定・`uv`未導入のCI環境で
  エラーになって既存の自動化を壊すため。使う人が明示的にコピーして有効化する運用にしています。
- `input/` / `output/` — 作業用フォルダ(gitignore対象。フォルダ自体だけ`.gitkeep`で維持)
- `tools/remotion-sample/src/Captions/` — 文字起こし結果を受け取り、
  [BudouX](https://github.com/google/budoux)で自然な位置に改行を入れて字幕として描画するコンポーネント

## セットアップ(1回だけ、ローカル環境やこのMCPを使いたいセッションで)

1. OpenAIのAPIキーを発行する(https://platform.openai.com/api-keys)
2. 環境変数として設定する(シェルの設定ファイルや`.env`など。**リポジトリには絶対に書かない**):
   ```bash
   export OPENAI_API_KEY=sk-xxxxx
   export AUDIO_FILES_PATH=/絶対パス/tools/video-edit/input
   ```
3. `tools/video-edit/mcp.whisper.json.example` をリポジトリ直下に `.mcp.json` としてコピーする:
   ```bash
   cp tools/video-edit/mcp.whisper.json.example .mcp.json
   ```
   (このファイルはgitignore対象にはしていないので、有効化したまま誤ってコミットしないよう注意。
   使い終わったら `rm .mcp.json` で元に戻すことを推奨)
4. Claude Codeを再起動すると `whisper` MCPサーバーが読み込まれる
   (`uvx` が必要。`uv`未導入の場合は https://docs.astral.sh/uv/ を参照)

## 使い方

1. `tools/video-edit/input/` に動画/音声ファイルを置く
2. Claude Codeに「この音声を文字起こしして」と頼む(whisper MCPツールが呼ばれる)
3. 文字起こし結果(`segments: [{text, start, end}]`)を
   `tools/remotion-sample/src/Captions/fromWhisperSegments.ts` でRemotionの`Caption[]`形式に変換
4. `CapsHighlight`(または他のコンポジション)の`captions`propに渡してレンダリングすると、
   字幕が焼き込まれた動画が出力される

字幕の見た目(フォントサイズ・位置・1行あたりの最大文字数など)は
`tools/remotion-sample/src/Captions/index.tsx` を編集して調整する。

## 注意

- この環境(サンドボックス)からは `api.openai.com` への接続がブロックされているため、
  ここでは実際にWhisper APIを呼び出せていません。ローカル環境やネットワーク制限のない
  環境での動作確認が必要です。
- 以前検討したローカルWhisperモデル(`openai-whisper` + `torch`)方式は、
  ダウンロード容量が大きく(5GB超)セッションごとに消えるこの環境と相性が悪いため、
  OpenAI API方式に切り替えました。
