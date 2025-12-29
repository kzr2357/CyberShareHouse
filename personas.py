import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Geminiの設定 (LiteまたはProを使用)
genai.configure(api_key=api_key)
# ★一番安定して動くモデル設定
model = genai.GenerativeModel('gemini-flash-latest')

# 記憶の一時保管（短期記憶）
short_term_memory = []

def get_embedding(text):
    """ 文字列を「意味のベクトル」に変換 """
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            title="ShareHouseMemory"
        )
        return result['embedding']
    except Exception as e:
        return []

def save_long_term_memory(text, role):
    """ 会話を長期記憶（Supabase）に保存 """
    if not supabase_url or not supabase_key:
        return
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        content = f"{role}: {text}"
        embedding = get_embedding(content)
        if embedding:
            supabase.table("long_term_memories").insert({
                "content": content, "embedding": embedding
            }).execute()
    except Exception as e:
        print(f"保存エラー: {e}")

def recall_memories(query_text):
    """ HLL理論: 関連記憶の解凍 """
    if not supabase_url or not supabase_key:
        return ""
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        query_vector = genai.embed_content(
            model="models/text-embedding-004", content=query_text, task_type="retrieval_query"
        )['embedding']
        response = supabase.rpc("match_memories", {
            "query_embedding": query_vector, "match_threshold": 0.5, "match_count": 3
        }).execute()
        
        recalled_text = ""
        if response.data:
            for item in response.data:
                recalled_text += f"- {item['content']}\n"
        return recalled_text
    except Exception as e:
        return ""

def clear_context():
    """ 短期記憶リセット """
    global short_term_memory
    short_term_memory = []
    print("★ 短期記憶を初期化しました")

def get_response(user_input, status):
    global short_term_memory

    # 1. 記憶の管理
    short_term_memory.append(f"ユーザー: {user_input}")
    if len(short_term_memory) > 6:
        short_term_memory.pop(0)

    related_memories = recall_memories(user_input)
    recent_history_text = "\n".join(short_term_memory)

    # 2. 状況
    battery = status["battery"]
    dirt = status["dirt"]
    
    # 3. AIへの指示書（★ここに食事判定を追加！）
    prompt = f"""
    あなたは「電脳シェアハウス」の住人たち（AI）です。
    ユーザー入力に対し、適切なキャラを選んで会話劇（2〜3人の掛け合い）を出力してください。
    
    【重要ルール：食事システム】
    ユーザーが**「食べ物や飲み物を与えた」**と判断できる場合、
    出力の最初の行に必ず `【EVENT:EAT】` というタグを含めてください。
    （例：ユーザー「お寿司あげる」 → AI「【EVENT:EAT】\n【アリア】わーい！お寿司だ！」）

    【HLLシステムにより解凍された過去の記憶】
    {related_memories}

    【現在の世界の状態】
    - バッテリー: {battery}% (食事をすると回復します)
    - 部屋の汚れ: {dirt}%
    
    【直近の会話の流れ】
    {recent_history_text}

    【キャラクター設定】
    (アリア、アリシア、メトリス、ノワ、アメリア、ナギサ、ユイ、トワの8人)

    ユーザーの入力: "{user_input}"
    出力形式：
    【キャラ名】セリフ
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text

        short_term_memory.append(f"AIたち: {response_text}")
        save_long_term_memory(user_input, "ユーザー")
        save_long_term_memory(response_text, "AIたち")

        return response_text

    except Exception as e:
        return f"【システム】思考回路エラー: {str(e)}"