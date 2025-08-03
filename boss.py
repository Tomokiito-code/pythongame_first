import pygame
import random
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT

# 初級編用：自由な位置と画像を渡すボス
class StaticBoss:
    def __init__(self, image, x, y, fireball_img=None):
        self.image = image
        self.x = x
        self.y = y
        self.width = image.get_width() if image else 128
        self.height = image.get_height() if image else 128
        self.max_hp = 300
        self.hp = 300
        self.second_phase = False
        self.active = True
        self.phase = 1  # 移動方向（1:右、2:左）

        self.fireballs = []
        self.last_fire_time = pygame.time.get_ticks()
        self.fire_cooldown = random.randint(800, 1800)
        self.fireball_img = fireball_img

    def update(self):
        if not self.active:
            return

        speed = 2 if not self.second_phase else 4
        self.x += speed if self.phase == 1 else -speed
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.phase = 2
        elif self.x < 0:
            self.x = 0
            self.phase = 1

        now = pygame.time.get_ticks()
        if now - self.last_fire_time > self.fire_cooldown:
            self.shoot_fire()
            self.last_fire_time = now
            self.fire_cooldown = random.randint(700, 1600)

        for fb in self.fireballs:
            fb["x"] += fb["vx"]
            fb["y"] += fb["vy"]

        self.fireballs = [fb for fb in self.fireballs if 0 <= fb["x"] <= SCREEN_WIDTH and fb["y"] < SCREEN_HEIGHT]

    def shoot_fire(self):
        fire_count = random.randint(2, 5)
        for _ in range(fire_count):
            angle_deg = random.uniform(-60, 60)
            speed = random.uniform(3, 5)
            rad = math.radians(angle_deg)
            vx = math.sin(rad) * speed
            vy = math.cos(rad) * speed
            self.fireballs.append({
                "x": self.x + self.width // 2,
                "y": self.y + self.height - 12,
                "vx": vx,
                "vy": vy
            })

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        for fb in self.fireballs:
            if self.fireball_img:
                offset = self.fireball_img.get_width() // 2
                screen.blit(self.fireball_img, (fb["x"] - offset, fb["y"] - offset))
            else:
                pygame.draw.circle(screen, (255, 100, 0), (int(fb["x"]), int(fb["y"])), 8)

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= self.max_hp // 2 and not self.second_phase:
            self.second_phase = True
        if self.hp <= 0:
            self.active = False

# 無限編用：ステージ進行に応じて強化されるボス
class Boss(pygame.sprite.Sprite):
    def __init__(self, level, strategy="center"):
        super().__init__()
        self.stage_level = level
        self.attack_strategy = strategy
        self.health = 100 + level * 20
        self.move_direction = 1

        self.last_fire_time = 0
        self.fireballs = []

        boss_img = pygame.image.load("assets/infinity_boss.png").convert_alpha()
        boss_img = pygame.transform.scale(boss_img, (128, 128))
        self.image = boss_img
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 100))

    def set_attack_pattern(self, config):
        self.bullet_count = config.get("bullet_count", 1)
        self.bullet_speed = config.get("bullet_speed", 5.0)

    
    def update(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time > 800:
            self.fire_projectile(player)
            self.last_fire_time = current_time

        speed = 2 + self.stage_level * 0.3
        self.rect.x += speed * self.move_direction

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.move_direction *= -1

        for fb in self.fireballs:
            fb["x"] += fb["vx"]
            fb["y"] += fb["vy"]

        self.fireballs = [
            fb for fb in self.fireballs
            if 0 <= fb["x"] <= SCREEN_WIDTH and fb["y"] <= SCREEN_HEIGHT
        ]

    def fire_projectile(self, player):
        bullet_count = 1 + (self.stage_level // 2)
        bullet_speed = 5 + self.stage_level * 0.5

        base_x = self.rect.centerx
        base_y = self.rect.bottom

        for _ in range(bullet_count):
            dx = player.rect.centerx - base_x
            dy = player.rect.centery - base_y
            distance = math.hypot(dx, dy)
            if distance == 0:
                distance = 1

            vx = (dx / distance) * bullet_speed
            vy = (dy / distance) * bullet_speed

            self.fireballs.append({
                "x": base_x + random.randint(-10, 10),
                "y": base_y + random.randint(-5, 5),  # y座標にもブレを追加！
                "vx": vx,
                "vy": vy
            })

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        for fb in self.fireballs:
            pygame.draw.circle(screen, (255, 100, 0), (int(fb["x"]), int(fb["y"])), 8)

    def get_hitbox(self):
        return self.rect