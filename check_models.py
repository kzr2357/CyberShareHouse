import google.generativeai as genai
import os
from dotenv import load_dotenv

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("エラー: APIキーが見つかりません。.envファイルを確認してください。")
else:
    genai.configure(api_key=api_key)

    print("=== あなたが現在使用可能なモデル一覧 ===")
    try:
        # Googleのサーバーに「何が使える？」と聞く
        for m in genai.list_models():
            # 「会話（文章生成）」ができるモデルだけを表示
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        print("========================================")
    except Exception as e:
        print(f"一覧の取得に失敗しました: {e}")