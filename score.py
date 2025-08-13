# score.py

import time

class Score:
    def __init__(self):
        self.value = 0
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.last_kill_time = None
        self.combo_timeout = 2.0  # 秒

    def add(self, base_score):
        current_time = time.time()
        if self.last_kill_time and current_time - self.last_kill_time <= self.combo_timeout:
            self.combo_count += 1
        else:
            self.combo_count = 0
        self.last_kill_time = current_time
        self.combo_multiplier = 1.0 + self.combo_count * 0.1
        self.value += int(base_score * self.combo_multiplier)

    def reset_combo(self):
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.last_kill_time = None

    def draw_combo(self, screen, font):
        combo_text = font.render(f"Combo: {self.combo_count}", True, (255, 200, 200))
        multiplier_text = font.render(f"x{self.combo_multiplier:.1f}", True, (255, 180, 180))
        screen.blit(combo_text, (screen.get_width() - 180, 10))
        screen.blit(multiplier_text, (screen.get_width() - 180, 40))

    def force_combo(self, base_score):
        self.combo_count += 1
        self.combo_multiplier = 1.0 + self.combo_count * 0.1
        self.value += int(base_score * self.combo_multiplier)
        self.last_kill_time = time.time()

    def __str__(self):
        return str(self.value)  # ← これで f"{score}" が数値になる！