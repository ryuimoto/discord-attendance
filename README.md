# Discord打刻 → Googleスプレッドシート

Discordの勤怠メッセージをGoogleスプレッドシートへ自動記録する最小構成です。

## 構成
- `bot/` : Discord Bot (Python)
- `gas/` : Google Apps Script (Webアプリ)

## 事前準備
### Discord Bot
1. Discord Developer PortalでBotを作成
2. `MESSAGE CONTENT INTENT` を有効化
3. Botをサーバーへ招待

### スプレッドシート
- シート名: `勤怠ログ`
- 列定義: 仕様書の通り

## GASセットアップ
1. スプレッドシートを開き、拡張機能 → Apps Script
2. `gas/Code.gs` を貼り付け
3. スクリプトプロパティに `SHARED_SECRET` を登録
4. デプロイ → 新しいデプロイ → 種類: ウェブアプリ
   - 実行ユーザー: 自分
   - アクセス: 全員
5. デプロイURLを取得

## Botセットアップ
1. `bot/.env.example` を `bot/.env` にコピー
2. `bot/.env` を編集
3. 依存インストール

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r bot/requirements.txt
```

4. 実行

```bash
python bot/main.py
```

## クラウド実行
- Cloud Run / EC2 / VM等に常駐実行する前提です。
- 今回は最小構成なので、プロセスマネージャやDockerは未導入です。

# discord-attendance
