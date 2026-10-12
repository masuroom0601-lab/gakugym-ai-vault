# Fish Audio TTS

[Fish Audio](https://fish.audio) の音声合成(TTS) APIを叩いて、テキストからナレーション音声(mp3)を生成するだけの小さなCLIです。
Remotion動画にナレーションを乗せたい場合、ここで生成した音声ファイルを
`tools/remotion-sample/public/` 配下に置いて `<Audio src={staticFile(...)} />` で読み込む想定です。

## 使い方

```bash
cd tools/fish-audio
export FISH_AUDIO_API_KEY=xxxxx   # fish.audio/app/api-keys で発行したキー。.envやシェル変数で渡す。リポジトリには絶対に書かない。
node tts.js "読み上げたいテキスト" out.mp3

# 特定のボイス(reference_id)を使う場合
node tts.js "読み上げたいテキスト" out.mp3 <reference_id>
```

- Node.js 18+ (組み込みの`fetch`を使用、追加の依存なし)
- `reference_id` はFish Audio上で作成した音声モデルのID。省略時はデフォルトボイス。

## 注意

- **このリポジトリのネットワーク制限のあるサンドボックス環境では `api.fish.audio` への接続がブロックされているため未検証です。** ローカルPCやネットワーク制限のないCIで実行してください。
- APIキーはコミットしないこと。漏れた場合はFish Audioのダッシュボードで再発行してください。
