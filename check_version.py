import google.generativeai as genai
import os
from dotenv import load_dotenv

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("エラー: APIキーが見つかりません。")
else:
    genai.configure(api_key=api_key)
    
    # "gemini-flash-latest" という名札の中身を呼び出す
    model = genai.GenerativeModel('gemini-flash-latest')

    print("--- モデルへの尋問を開始します ---")
    try:
        # ストレートに聞いてみる
        response = model.generate_content("あなたのモデルバージョンはGemini 1.5ですか？それとも2.0ですか？短く答えてください。")
        print(f"モデルの回答: {response.text}")
        
        # 念のためモデル名も表示（SDKが認識している名前）
        print(f"指定したモデル名: {model.model_name}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")