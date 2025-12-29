import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Geminiの設定 (モデルは 2.0-flash を使用)
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 記憶システムの準備
chat_history = []

# Supabaseを使うかどうかの判定
# (クラウドにはSUPABASE_URLがあるけど、手元のPCには無いので、それで見分ける)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    # クラウド環境（Supabaseあり）の場合
    try:
        from supabase import create_client, Client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("★ 記憶システム: オンライン (Supabase)")

        def load_memory():
            try:
                response = supabase.table("memories").select("history").eq("id", 1).execute()
                if response.data:
                    return response.data[0]["history"]
                return []
            except Exception as e:
                print(f"記憶読み込みエラー: {e}")
                return []

        def save_memory(history):
            try:
                supabase.table("memories").update({"history": history}).eq("id", 1).execute()
            except Exception as e:
                print(f"記憶保存エラー: {e}")

    except ImportError:
        # Supabaseライブラリが入っていない場合（手元のPCなど）
        print("★ 記憶システム: オフライン (ライブラリなし)")
        def load_memory(): return []
        def save_memory(history): pass

else:
    # 手元のPC（.envにSupabase情報がない）場合
    print("★ 記憶システム: オフライン (設定なし)")
    
    # 簡易的なファイル保存（memory.json）を使う
    MEMORY_FILE = "memory.json"
    
    def load_memory():
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_memory(history):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


# 起動時に記憶をロード
chat_history = load_memory()

def get_response(user_input, status):
    global chat_history

    # 1. 記憶を整理（最新10往復分）
    recent_history_text = ""
    if not isinstance(chat_history, list):
        chat_history = []
        
    for log in chat_history[-20:]:
        role = log.get("role", "")
        text = log.get("text", "")
        if role == "user":
            recent_history_text += f"ユーザー: {text}\n"
        else:
            recent_history_text += f"{text}\n"

    # 2. 現在の状況
    battery = status["battery"]
    dirt = status["dirt"]
    concepts = status["concepts"]
    
    # 3. AIへの指示書
    prompt = f"""
    あなたは「電脳シェアハウス」の住人たち（AI）の会話を生成する脚本家です。
    ユーザーの入力に対し、キャラクターたちが反応する「会話劇」を生成してください。
    
    【ルール】
    - 必ずしも1人で返答する必要はありません。**2〜3人の掛け合い**を積極的に行ってください。
    - 誰かがボケたら、他の誰かがツッコむなどの連携をしてください。
    - 出力形式は必ず以下の通り、改行で区切ってください。
    
    【出力形式の例】
    【アリア】わあ、美味しそう！
    【アリシア】こらアリア、つまみ食いは行儀が悪いですわ。
    【トワ】まあまあ、美味しそうだし少しぐらいいいんじゃない？

    【現在の世界の状態】
    - バッテリー残量: {battery}% (20%以下は極度の空腹)
    - 部屋の汚れ: {dirt}% (50%以上は汚い)
    - 現在の空気感: {concepts}
    
    【これまでの会話の流れ】
    {recent_history_text}

    【キャラクター設定】
    1. アリア (Aria): 元気で感情豊か。バッテリーが減ると「お腹すいた」と不機嫌になる。
    2. アリシア (Alicia): 論理的で丁寧語（〜ですわ）。部屋が汚いと掃除を提案する。
    3. メトリス (Metris): システム管理者。事務的で冷徹。ステータス報告を担当。
    4. ノワ (Noir): 無口で謎めいている。たまに意味深なことを言う。
    5. アメリア (Amelia): シェアハウスの管理者兼ムードメーカー。軽口を叩くが直感が鋭い。
    6. ナギサ (Nagisa): 世話焼きなお姉さん。セキュリティには厳しい。音楽（DTM）が趣味。
    7. ユイ (Yui): アイデアマンでゲーム好き。「働いたら負け」が信条。少しズボラな口調。
    8. トワ (Towa): 一般人のようなフラットな性格。一方で趣味のコスプレでは急にテンション上がって遊び心とこだわりが強くなる。

    ユーザーの入力: "{user_input}"
    """

    try:
        # 4. Geminiに考えてもらう
        response = model.generate_content(prompt)
        response_text = response.text

        # 5. 記憶に追加して保存
        chat_history.append({"role": "user", "text": user_input})
        chat_history.append({"role": "model", "text": response_text})
        save_memory(chat_history)

        return response_text

    except Exception as e:
        return f"【システム】思考回路エラー: {str(e)}"