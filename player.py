import pygame

class Player:
    def __init__(self, image, max_hp=100, speed=5):
        self.image = image
        self.max_hp = max_hp
        self.hp = max_hp
        self.speed = speed
        self.width = image.get_width()
        self.height = image.get_height()
        self.x = 400
        self.y = 600 - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # 被弾状態管理
        self.hit = False
        self.hit_timer = 0           # 描画演出用
        self.damage_timer = 0        # AI用：学習で利用（被弾→無敵時間など）

    def handle_input(self, keys, screen_width=1200, screen_height=800):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < screen_width - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < screen_height - self.height:
            self.y += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        if self.hit:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)  # 被弾演出（赤点滅）
        else:
            screen.blit(self.image, (self.x, self.y))

    def get_hitbox(self):
        return self.rect.inflate(-16, -10)  # 少し小さくして判定を優しく

    def take_damage(self, amount):
        if self.damage_timer == 0:  # 無敵時間中は無効
            self.hp = max(0, self.hp - amount)
            self.hit = True
            self.hit_timer = pygame.time.get_ticks()
            self.damage_timer = 30  # AI用：30フレーム分「被弾中」として扱う

    def update_hit_status(self):
        # 描画用フラグの解除
        if self.hit and pygame.time.get_ticks() - self.hit_timer > 100:
            self.hit = False

        # AI学習用フレームカウント（毎フレーム減らす）
        if self.damage_timer > 0:
            self.damage_timer -= 1

    def reset(self):
        self.x = 400
        self.y = 600 - self.height
        self.hp = self.max_hp
        self.hit = False
        self.hit_timer = 0
        self.damage_timer = 0
        self.rect.topleft = (self.x, self.y)