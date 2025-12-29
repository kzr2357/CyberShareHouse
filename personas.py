import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
# ★ 名前を変更してインポート
from prime_tokenizer import SemanticPrimeTokenizer

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

genai.configure(api_key=api_key)
# モデル設定
model = genai.GenerativeModel('gemini-flash-latest')

# ★ トークナイザの初期化（新しい名前で）
tokenizer = SemanticPrimeTokenizer()

# 記憶の一時保管
short_term_memory = []

def get_embedding(text):
    try:
        result = genai.embed_content(
            model="models/text-embedding-004", content=text,
            task_type="retrieval_document", title="ShareHouseMemory"
        )
        return result['embedding']
    except: return []

def save_long_term_memory(text, role):
    if not supabase_url or not supabase_key: return
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        content = f"{role}: {text}"
        embedding = get_embedding(content)
        if embedding:
            supabase.table("long_term_memories").insert({"content": content, "embedding": embedding}).execute()
    except: pass

def recall_memories(query_text):
    if not supabase_url or not supabase_key: return ""
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        query_vector = genai.embed_content(model="models/text-embedding-004", content=query_text, task_type="retrieval_query")['embedding']
        response = supabase.rpc("match_memories", {"query_embedding": query_vector, "match_threshold": 0.5, "match_count": 3}).execute()
        recalled = ""
        if response.data:
            for item in response.data: recalled += f"- {item['content']}\n"
        return recalled
    except: return ""

def clear_context():
    global short_term_memory
    short_term_memory = []

def get_response(user_input, status):
    global short_term_memory

    # 1. 素数共鳴の計算
    resonance_val, resonance_words = tokenizer.calculate_resonance(user_input)
    resonance_str = "×".join(resonance_words) if resonance_words else "無"

    # 2. 記憶管理
    short_term_memory.append(f"ユーザー: {user_input}")
    if len(short_term_memory) > 6: short_term_memory.pop(0)

    related_memories = recall_memories(user_input)
    recent_history = "\n".join(short_term_memory)
    
    battery = status["battery"]
    dirt = status["dirt"]

    # 3. プロンプト
    prompt = f"""
    あなたは「電脳シェアハウス」の住人たちです。
    
    【★ 現在の重要パラメータ：意味論的共鳴】
    - 検出概念: [{resonance_str}]
    - 共鳴素数値: {resonance_val}
    (※この概念が会話のテーマです。この雰囲気に合わせた会話をしてください)

    【重要ルール】
    - 食事を与えられたら `【EVENT:EAT】` を出力。
    - 出力の最後に、必ず `【RESONANCE:{resonance_val}:{resonance_str}】` と出力。

    【解凍された記憶】
    {related_memories}

    【ステータス】
    - バッテリー: {battery}%
    - 汚れ: {dirt}%
    
    【会話ログ】
    {recent_history}

    ユーザー入力: "{user_input}"
    出力形式：
    【キャラ名】セリフ
    ...
    【RESONANCE:...】
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        
        short_term_memory.append(f"AIたち: {text}")
        save_long_term_memory(user_input, "ユーザー")
        save_long_term_memory(text, "AIたち")

        return text

    except Exception as e:
        return f"エラー: {str(e)}"