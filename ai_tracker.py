class SimpleAITracker:
    def __init__(self, track_size=60):
        self.track_size = track_size  # ログ保存の最大サイズ
        self.positions = []           # プレイヤーX座標履歴
        self.damage_log = []          # 被弾履歴（1 or 0）

    def record(self, player_x, was_hit):
        # プレイヤー位置を記録
        self.positions.append(player_x)
        if len(self.positions) > self.track_size:
            self.positions.pop(0)

        # 被弾情報を記録
        self.damage_log.append(1 if was_hit else 0)
        if len(self.damage_log) > self.track_size:
            self.damage_log.pop(0)

    def analyze_player_movement(self, screen_width):
        # 履歴から逃げ方向を分析
        left = sum(1 for x in self.positions if x < screen_width // 3)
        right = sum(1 for x in self.positions if x > screen_width * 2 // 3)
        center = len(self.positions) - (left + right)

        if left > right:
            return "left"
        elif right > left:
            return "right"
        else:
            return "center"

    def evolve_attack_pattern(self):
        # 直近の被弾量に応じて攻撃パターンを進化
        recent_hits = sum(self.damage_log[-30:])
        if recent_hits > 7:
            return {"bullet_count": 3, "bullet_speed": 7.5}
        elif recent_hits > 3:
            return {"bullet_count": 2, "bullet_speed": 6.0}
        else:
            return {"bullet_count": 1, "bullet_speed": 4.5}

    def get_strategy(self, screen_width):
        # 移動傾向＋攻撃パターンをまとめて取得
        direction = self.analyze_player_movement(screen_width)
        pattern = self.evolve_attack_pattern()
        return direction, pattern