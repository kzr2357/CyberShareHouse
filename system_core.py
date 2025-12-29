import datetime

class ShareHouseSystem:
    def __init__(self):
        # 初期ステータス
        self.battery = 100.0  # バッテリー (%)
        self.dirt = 0.0       # 部屋の汚れ (%)
        self.concepts = []    # 空間の概念（今は空）
        self.last_update = datetime.datetime.now()

    def get_status(self):
        # 時間経過による変化を計算
        now = datetime.datetime.now()
        delta = (now - self.last_update).total_seconds()
        
        # 1時間あたり10%減る
        battery_drop = (delta / 3600) * 10
        self.battery = max(0.0, self.battery - battery_drop)
        
        # 1時間あたり5%汚れる
        dirt_increase = (delta / 3600) * 5
        self.dirt = min(100.0, self.dirt + dirt_increase)
        
        self.last_update = now
        
        return {
            "battery": int(self.battery),
            "dirt": int(self.dirt),
            "concepts": self.concepts
        }