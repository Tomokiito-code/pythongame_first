class BulletManager:
    def __init__(self, normal_img, homing_img):
        self.arrow_img = normal_img
        self.homing_img = homing_img
        self.bullets = []

    def fire(self, x, y, is_homing=False, speed=10):  # ← speed を追加
        bullet = {
            "x": x,
            "y": y,
            "speed": speed,  # ← この速度を使う！
            "homing": is_homing,
            "img": self.homing_img if is_homing else self.arrow_img
        }
        self.bullets.append(bullet)

    def update(self, enemies, boss=None):
        for bullet in self.bullets:
            if bullet["homing"]:
                # ホーミング対象：敵 or ボス
                targets = [e for e in enemies if e["active"]]
                if boss and boss.active:
                    targets.append({
                        "x": boss.x,
                        "y": boss.y,
                        "active": True
                    })

                target = min(
                    targets,
                    key=lambda e: ((e["x"] - bullet["x"]) ** 2 + (e["y"] - bullet["y"]) ** 2),
                    default=None
                )
                if target:
                    dx = (target["x"] + 32) - bullet["x"]
                    dy = (target["y"] + 32) - bullet["y"]
                    distance = max((dx**2 + dy**2) ** 0.5, 1)
                    speed = 6
                    bullet["x"] += dx / distance * speed
                    bullet["y"] += dy / distance * speed
                else:
                    bullet["y"] -= bullet["speed"]
            else:
                bullet["y"] -= bullet["speed"]

    def draw(self, screen):
        for bullet in self.bullets:
            screen.blit(bullet["img"], (bullet["x"], bullet["y"]))

    def get_bullets(self):
        return self.bullets