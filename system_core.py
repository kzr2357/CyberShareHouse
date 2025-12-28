import time
from prime_tokenizer import SemanticPrimeTokenizer

class ShareHouseSystem:
    def __init__(self):
        self.tokenizer = SemanticPrimeTokenizer()
        
        # パラメータ初期値
        self.battery = 100.0
        self.dirt = 0.0
        self.last_update = time.time()
        
        # 世界の「雰囲気」を素数で管理（初期状態：秩序ある論理）
        self.world_state = self.tokenizer.encode(["秩序", "論理"])

    def update(self):
        """時間の経過処理"""
        current_time = time.time()
        minutes = (current_time - self.last_update) / 60
        
        if minutes >= 0.1: # テスト用に高速化（実際は数分単位）
            self.battery -= minutes * 2.0
            self.dirt += minutes * 1.5
            self.last_update = current_time
            
            # 範囲制限
            self.battery = max(0, self.battery)
            self.dirt = min(100, self.dirt)

    def get_status(self):
        self.update()
        
        # 状態に応じて「概念」を付与
        current_concepts = []
        if self.battery < 30: current_concepts.append("空腹")
        if self.dirt > 50: current_concepts.append("混沌")
        else: current_concepts.append("秩序")
        
        # 現在の状態値を計算
        current_state_val = self.tokenizer.encode(current_concepts)
        
        # 世界との共鳴チェック
        resonance = self.tokenizer.check_resonance(self.world_state, current_state_val)
        
        return {
            "battery": round(self.battery, 1),
            "dirt": round(self.dirt, 1),
            "concepts": current_concepts,
            "resonance": resonance # 共鳴している概念
        }