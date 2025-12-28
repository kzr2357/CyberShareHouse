import math

class SemanticPrimeTokenizer:
    def __init__(self):
        # 概念に素数を割り当て（世界を構成する因子）
        self.primes = {
            "悲しみ": 2, "喜び": 3, "空腹": 5, "音楽": 7,
            "論理": 11, "混沌": 13, "秘密": 17, "秩序": 19
        }

    def encode(self, concepts):
        """概念リストを「状態値（合成数）」に変換"""
        value = 1
        for c in concepts:
            if c in self.primes:
                value *= self.primes[c]
        return value

    def decode(self, value):
        """状態値から構成要素を復元"""
        concepts = []
        for k, v in self.primes.items():
            if value % v == 0:
                concepts.append(k)
        return concepts

    def check_resonance(self, state_a, state_b):
        """二つの状態の「共鳴（最大公約数）」を計算"""
        gcd_val = math.gcd(state_a, state_b)
        return self.decode(gcd_val)