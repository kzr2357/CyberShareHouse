import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("エラー: APIキーが見つかりません。")
    exit()

genai.configure(api_key=api_key)

# テストするモデル名の候補リスト（古いものから最新の実験版まで）
CANDIDATES = [
    # --- 本命（安定版・軽量） ---
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    
    # --- 対抗（安定版・高知能） ---
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    
    # --- 穴（旧世代・安定） ---
    "gemini-pro",
    "gemini-1.0-pro",
    
    # --- 最新・実験版（動くかもしれないが制限がきついかも） ---
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-flash-latest",
]

print("=== モデル生存確認テストを開始します ===")
print("※ 1つずつ通信テストを行うため、少し時間がかかります...")
print("-" * 50)

available_model = None

for model_name in CANDIDATES:
    print(f"Testing: {model_name} ... ", end="")
    try:
        # モデルを設定
        model = genai.GenerativeModel(model_name)
        
        # 実際に通信してみる（非常に短い言葉で）
        response = model.generate_content("Hello")
        
        # エラーが出なければ成功
        print("✅ 成功！ (利用可能)")
        print(f"   -> 返答: {response.text.strip()}")
        
        # 最初に成功したものを推奨として記録
        if available_model is None:
            available_model = model_name
            
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg:
            print("❌ 失敗 (存在しません - 404)")
        elif "429" in error_msg or "Quota" in error_msg:
            print("⚠️ 失敗 (回数制限オーバー - 429)")
        else:
            print(f"❌ 失敗 (その他のエラー: {error_msg[:50]}...)")
            
    # 連投制限に引っかからないように少し休憩
    time.sleep(1)

print("-" * 50)
if available_model:
    print(f"🎉 結論: あなたの環境では '{available_model}' を使うのがベストです！")
else:
    print("😭 全滅しました... APIキーの権限を確認する必要があります。")