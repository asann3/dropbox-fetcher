import datetime
import os

import dropbox
import requests
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DROPBOX_FOLDER = os.getenv('DROPBOX_FOLDER')
LOCAL_BASE_DIR = os.getenv('LOCAL_BASE_DIR')

def get_fiscal_year(date_obj):
    """日付から年度（4月始まり）を計算する"""
    if date_obj.month >= 4:
        return date_obj.year
    else:
        return date_obj.year - 1

def send_notification(message):
    """Webhookで通知を送る"""
    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={'content': message, 'text': message})
        except Exception as e:
            print(f"通知の送信に失敗しました: {e}")

def main():
    if not REFRESH_TOKEN:
        send_notification("🚨 エラー: .env ファイルから REFRESH_TOKEN が読み込めません。")
        return

    today = datetime.date.today()
    fiscal_year = get_fiscal_year(today)
    target_dir = os.path.join(LOCAL_BASE_DIR, 'doc', '進捗報告', f'進捗報告{fiscal_year}年度')

    # 保存先フォルダが存在しなければ作成
    os.makedirs(target_dir, exist_ok=True)

    dbx = dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=REFRESH_TOKEN
    )
    success_count = 0
    skipped_files = []
    skipped_folders = []
    processed_folders = set()

    try:
        result = dbx.files_list_folder(DROPBOX_FOLDER, recursive=True)
        while True:
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    prefix_len = len(DROPBOX_FOLDER)

                    relative_path = entry.path_display[prefix_len:].lstrip('/')

                    if '/' not in relative_path:
                        continue
                    local_path = os.path.join(target_dir, relative_path)

                    os.makedirs(os.path.dirname(local_path), exist_ok=True)

                    folder_path_lower = os.path.dirname(entry.path_lower)
                    if folder_path_lower != DROPBOX_FOLDER.lower():
                        processed_folders.add(folder_path_lower)

                    try:
                        dbx.files_download_to_file(local_path, entry.path_lower)

                        if os.path.exists(local_path) and os.path.getsize(local_path) == entry.size:
                            dbx.files_delete_v2(entry.path_lower)
                            success_count += 1
                        else:
                            skipped_files.append(entry.name)
                    except Exception as e:
                        skipped_files.append(f"{entry.name} (エラー: {e})")

            # 続きがあれば取得し、なければループを抜ける
            if not result.has_more:
                break
            result = dbx.files_list_folder_continue(result.cursor)
        # 処理後、空になったDropbox側の日付サブフォルダ(260414等)を削除
        for folder in sorted(processed_folders, key=lambda x: x.count('/'), reverse=True):
            try:
                dbx.files_delete_v2(folder)
            except Exception as e:
                # 削除できなかったフォルダはスキップリストに追加
                skipped_folders.append(f"{folder} (エラー: {e})")
        # 処理結果の通知
        if success_count > 0 or skipped_files or skipped_folders:
            report_msg = ""

            if success_count > 0:
                report_msg += f"【転送完了】\n"
                report_msg += f"保存先: {fiscal_year}年度進捗報告\n"
                report_msg += f"・成功: {success_count} 件\n"
            else:
                report_msg += f"🚨 【警告】エラーが発生しています\n"

            if skipped_files:
                report_msg += f"⚠️ スキップ・失敗: {len(skipped_files)} 件\n"
                for skip_file in skipped_files:
                    report_msg += f"  - {skip_file}\n"

            if skipped_folders:
                report_msg += f"⚠️ フォルダの削除保留: {len(skipped_folders)} 件\n"
                for skip_folder in skipped_folders:
                    report_msg += f"  - {skip_folder}\n"

            send_notification(report_msg)

    except dropbox.exceptions.ApiError as err:
        send_notification(f"Dropbox API エラー: {err}")
    except Exception as e:
        send_notification(f"システムエラー: {e}")
    #     print(f"システムエラー: {e}")

if __name__ == '__main__':
    main()
