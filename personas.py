import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 設定読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Geminiの設定 (安定版 1.5 Flash を使用)
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 記憶の一時保管（短期記憶）
short_term_memory = []

def get_embedding(text):
    """ 文字列を「意味のベクトル(存在証明)」に変換する """
    try:
        # embedding-001 モデルを使ってベクトル化
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            title="ShareHouseMemory"
        )
        return result['embedding']
    except Exception as e:
        print(f"ベクトル化エラー: {e}")
        return []

def save_long_term_memory(text, role):
    """ 会話を長期記憶（Supabase）に圧縮保存する """
    if not supabase_url or not supabase_key:
        return

    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)

        # 1. 保存する文章を作る
        content = f"{role}: {text}"
        
        # 2. 知識の存在証明（ベクトル）を作る
        embedding = get_embedding(content)
        
        if embedding:
            # 3. 保存
            supabase.table("long_term_memories").insert({
                "content": content,
                "embedding": embedding
            }).execute()
            print(f"★ 記憶を長期保存しました: {content[:20]}...")
            
    except Exception as e:
        print(f"保存エラー: {e}")

def recall_memories(query_text):
    """ HLL理論: ユーザーの発言に共鳴する記憶だけを解凍する """
    if not supabase_url or not supabase_key:
        return ""

    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)

        # 1. 問いかけのベクトル化
        query_vector = genai.embed_content(
            model="models/text-embedding-004",
            content=query_text,
            task_type="retrieval_query"
        )['embedding']

        # 2. 共鳴検索（類似度0.5以上の上位3件を取得）
        response = supabase.rpc(
            "match_memories",
            {
                "query_embedding": query_vector,
                "match_threshold": 0.5, 
                "match_count": 3
            }
        ).execute()

        # 3. 解凍（テキストの連結）
        recalled_text = ""
        if response.data:
            print(f"★ {len(response.data)}件の記憶が共鳴しました！")
            for item in response.data:
                recalled_text += f"- {item['content']} (共鳴度: {item['similarity']:.2f})\n"
        
        return recalled_text

    except Exception as e:
        print(f"想起エラー: {e}")
        return ""

def get_response(user_input, status):
    global short_term_memory

    # 1. 短期記憶（直近の会話）の管理
    short_term_memory.append(f"ユーザー: {user_input}")
    if len(short_term_memory) > 6: # 最新6行だけ保持
        short_term_memory.pop(0)

    # 2. HLL発動：関連する過去の記憶を呼び出す
    related_memories = recall_memories(user_input)
    
    # 3. 短期記憶テキスト化
    recent_history_text = "\n".join(short_term_memory)

    # 4. 現在の状況
    battery = status["battery"]
    dirt = status["dirt"]
    concepts = status["concepts"]
    
    # 5. AIへの指示書
    prompt = f"""
    あなたは「電脳シェアハウス」の脚本家です。
    
    【HLLシステムにより解凍された『関連する過去の記憶』】
    {related_memories}
    (※この記憶の内容について聞かれたら、詳しく答えてください)

    【現在の世界の状態】
    - バッテリー: {battery}%
    - 部屋の汚れ: {dirt}%
    
    【直近の会話の流れ（短期記憶）】
    {recent_history_text}

    【キャラクター設定】
    (全員の設定は省略しませんが、スペースの都合で脳内補完してください。アリア、アリシア、メトリス、ノワ、アメリア、ナギサ、ユイ、トワの8人です)

    【指示】
    ユーザーの入力に対し、適切なキャラを選んで会話劇（2〜3人の掛け合い）を出力してください。
    形式：
    【キャラ名】セリフ
    """

    try:
        # Geminiに生成させる
        response = model.generate_content(prompt)
        response_text = response.text

        # AIの返答も短期記憶と長期記憶に追加
        short_term_memory.append(f"AIたち: {response_text}")
        save_long_term_memory(user_input, "ユーザー") # ユーザーの発言を保存
        save_long_term_memory(response_text, "AIたち") # AIの返答を保存

        return response_text

    except Exception as e:
        return f"【システム】思考回路エラー: {str(e)}"