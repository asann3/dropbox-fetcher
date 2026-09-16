# dropbox-fetcher

## セットアップ

```bash
cp .env.example .env
uv sync
```

`.env` の `WEBHOOK_URL` に通知先のWebhook URLを埋める。

## APP_KEY / APP_SECRET の取得方法

1. https://www.dropbox.com/developers/apps にアクセス
2. 「Create app」から新規アプリを作成
   - アクセス範囲は Full Dropbox（ユーザーのDropbox全体へのアクセス）を選択する
     - App folder はアプリ専用に新規作成される単一フォルダのみのアクセスとなり、既存の任意フォルダを指定する本アプリの用途には合わない
3. アプリの Permissions タブで以下の2つを有効にする
   - files.content.write
   - files.content.read
   - どちらかを有効にすると files.metadata.read も自動的に有効になる
4. 「Settings」タブに App key / App secret が表示されるので `.env` の `APP_KEY` / `APP_SECRET` に転記する

## REFRESH_TOKEN の取得方法

`APP_KEY` / `APP_SECRET` を `.env` に設定した状態で以下を実行する。

```bash
uv run get_refresh_token.py
```

表示されるURLをブラウザで開いて許可し、発行されたアクセスコードをターミナルに貼り付けると `REFRESH_TOKEN=...` が出力されるので、`.env` に追記する。

## DROPBOX_FOLDER の指定方法

`https://www.dropbox.com/home` 以降のパスを `.env` の `DROPBOX_FOLDER` に指定する（例: `/Lab/進捗報告`）。

## LOCAL_BASE_DIR の指定方法

保存先は `<LOCAL_BASE_DIR>/doc/進捗報告/進捗報告{年度}年度/` に自動的に決まる（`{年度}` は実行日から自動計算されるため指定不要）。
`.env` の `LOCAL_BASE_DIR` には、`/doc` より手前のディレクトリの絶対パスを指定する（例: `/path/to/mount`）。

以下を実行するとfetchが開始される。

```bash
uv run main.py
```
