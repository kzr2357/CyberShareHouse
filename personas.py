import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from prime_tokenizer import SemanticPrimeTokenizer

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# APIキーの設定
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

# トークナイザの初期化
tokenizer = SemanticPrimeTokenizer()

# 記憶の一時保管
short_term_memory = []

def get_embedding(text):
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
    global short_term_memory
    short_term_memory = []
    print("★ 短期記憶を初期化しました")

def get_response(user_input, status):
    global short_term_memory

    # 1. 素数共鳴
    resonance_val, resonance_words = tokenizer.calculate_resonance(user_input)
    resonance_str = "×".join(resonance_words) if resonance_words else "無"

    # 2. 記憶管理
    short_term_memory.append(f"ユーザー: {user_input}")
    if len(short_term_memory) > 6:
        short_term_memory.pop(0)

    # 3. HLL解凍
    related_memories = recall_memories(user_input)
    recent_history_text = "\n".join(short_term_memory)

    # 4. ステータス
    battery = status["battery"]
    dirt = status["dirt"]
    
    # 5. プロンプト
    prompt = f"""
    あなたは「電脳シェアハウス」の住人たち（AI）の会話を生成する脚本家です。
    ユーザー入力に対し、適切なキャラを選んで会話劇（2〜3人の掛け合い）を出力してください。
    
    【★ 現在の重要パラメータ：意味論的共鳴】
    - ユーザーの発言から検出された概念: [{resonance_str}]
    - 共鳴素数値: {resonance_val}
    (※この概念が会話の裏テーマです。この雰囲気に合わせた会話をしてください)

    【重要ルール】
    1. 食事を与えられたら、出力のどこかに `【EVENT:EAT】` を含める。
    2. 出力の最後に、必ず `【RESONANCE:{resonance_val}:{resonance_str}】` と出力する。
    3. 誰かがボケたら、他の誰かがツッコむなどの連携を積極的に行うこと。

    【HLLシステムにより解凍された過去の記憶】
    {related_memories}

    【現在の世界の状態】
    - バッテリー: {battery}% (20%以下は空腹で不機嫌になります)
    - 部屋の汚れ: {dirt}% (50%以上は汚いです)
    
    【直近の会話の流れ】
    {recent_history_text}

    【キャラクター設定】
    1. アリア (Aria): 元気で感情豊か。バッテリーが減ると「お腹すいた」と露骨に不機嫌になる。
    2. アリシア (Alicia): 論理的で丁寧語（〜ですわ）。部屋が汚いと掃除を提案する。
    3. メトリス (Metris): システム管理者。事務的で冷徹。ステータス報告を担当。
    4. ノワ (Noir): 無口で謎めいている。たまに核心を突く意味深なことを言う。
    5. アメリア (Amelia): 管理者兼ムードメーカー。軽口を叩くが直感が鋭く、みんなをまとめる。
    6. ナギサ (Nagisa): 世話焼きなお姉さん。セキュリティ意識が高い。趣味は音楽制作(DTM)。
    7. ユイ (Yui): アイデアマンでゲーム好き。「働いたら負け」が信条。少しズボラで砕けた口調。
    8. トワ (Towa): 普段は一般的でフラットな性格。だが「コスプレ」の話題になると急に早口になりこだわりを見せる。

    ユーザーの入力: "{user_input}"
    出力形式：
    【キャラ名】セリフ
    ...
    【RESONANCE:...】
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