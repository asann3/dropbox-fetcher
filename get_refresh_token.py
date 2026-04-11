import os

import dropbox
from dotenv import load_dotenv

load_dotenv()


APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')

def main():
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')
    
    authorize_url = auth_flow.start()
    print("1. 以下のURLをブラウザで開いてください:")
    print(authorize_url)
    print("2. 「許可」をクリックし、表示されたアクセスコードをコピーしてください。")
    
    print("3. ここにアクセスコードを貼り付けてEnterを押してください: ")
    auth_code = input("> ").strip()
    
    try:
        oauth_result = auth_flow.finish(auth_code)
        print("以下の情報を .env に追記してください。")
        print(f"DROPBOX_REFRESH_TOKEN={oauth_result.refresh_token}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    main()
