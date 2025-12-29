import math

# ==========================================
# ★ 世界を構成する「素数化された概念」辞書
# ==========================================
CONCEPT_PRIMES = {
    # 【感情・状態】
    "愛": 2, "好き": 2,
    "混沌": 3, "バグ": 3,
    "希望": 5, "夢": 5,
    "絶望": 7, "虚無": 7,
    "怒り": 11, "悲しみ": 13,
    "喜び": 17, "楽しい": 17,
    "不安": 19,
    
    # 【シェアハウス固有】
    "ピザ": 23, "空腹": 29, "お腹": 29,
    "掃除": 31, "汚い": 31,
    "ゲーム": 37, "音楽": 41, "歌": 41,
    "コスプレ": 43, "衣装": 43,
    "仕事": 47, "働": 47,
    
    # 【概念・世界】
    "量子": 53, "世界": 59,
    "AI": 61, "人間": 67,
    "時間": 71, "記憶": 73, "共鳴": 79
}

PRIME_TO_CONCEPT = {v: k for k, v in CONCEPT_PRIMES.items()}

# ★ クラス名を変更しました！
class SemanticPrimeTokenizer:
    def __init__(self):
        self.primes = CONCEPT_PRIMES

    def calculate_resonance(self, text):
        resonance_value = 1
        detected_concepts = []

        for word, prime in self.primes.items():
            if word in text:
                resonance_value *= prime
                concept_name = PRIME_TO_CONCEPT[prime]
                if concept_name not in detected_concepts:
                    detected_concepts.append(concept_name)

        return resonance_value, detected_concepts

    def decode_resonance(self, value):
        if value <= 1: return []
        concepts = []
        temp_value = value
        for prime, word in PRIME_TO_CONCEPT.items():
            while temp_value % prime == 0:
                concepts.append(word)
                temp_value //= prime
        return concepts