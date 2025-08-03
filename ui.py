import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT

def draw_text_centered(screen, text, size, color, y):
    font = pygame.font.SysFont(None, size)
    rendered = font.render(text, True, color)
    screen.blit(rendered, rendered.get_rect(center=(600, y)))

def draw_hp_bar(screen, hp, max_hp):
    bar_width = 200
    bar_height = 20
    x = 30
    y = 30
    fill = int((hp / max_hp) * bar_width)
    
    pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))      # 赤：最大HP
    pygame.draw.rect(screen, (0, 255, 0), (x, y, fill, bar_height))           # 緑：現在HP
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)  # 枠線

def draw_score(screen, score):
    font = pygame.font.SysFont(None, 40)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def draw_restart_hint(screen):
    draw_text_centered(screen, "Press R to Restart", 40, (200, 200, 200), 500)

def draw_homing_hint(screen):
    font = pygame.font.SysFont(None, 28)
    text = font.render("長押しでホーミング発射", True, (255, 255, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 40))

def draw_charge_bar(screen, charge_duration):
    max_duration = 1000  # 最大チャージ時間（ms）
    ratio = min(charge_duration / max_duration, 1)
    bar_width = 200
    bar_height = 10
    x = SCREEN_WIDTH // 2 - bar_width // 2
    y = SCREEN_HEIGHT - 60

    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (255, 255, 0), (x, y, bar_width * ratio, bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

def draw_boss_hp_bar(screen, hp, max_hp):
    bar_width = 300
    bar_height = 15
    x = SCREEN_WIDTH // 2 - bar_width // 2
    y = 20
    ratio = max(min(hp / max_hp, 1), 0)

    pygame.draw.rect(screen, (80, 80, 80), (x, y, bar_width, bar_height))              # 背景バー
    pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width * ratio, bar_height))      # 残りHP
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)       # 枠線

def draw_homing_cooldown(screen, cooldown_remaining):
    font = pygame.font.SysFont("Yu Gothic", 26)
    seconds = int(cooldown_remaining / 1000) + 1
    message = f"ホーミングまであと {seconds} 秒"
    text = font.render(message, True, (0, 0, 0))  # ← 黒文字に変更！
    screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 35))

# def draw_homing_gauge(screen, cooldown_remaining, cooldown_total):
#     bar_width = 200
#     bar_height = 10
#     x = SCREEN_WIDTH // 2 - bar_width // 2
#     y = SCREEN_HEIGHT - 30

#     ratio = 1 - min(cooldown_remaining / cooldown_total, 1)
#     fill_color = (0, 255, 0) if ratio >= 1 else (255, 255, 0)

#     pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
#     pygame.draw.rect(screen, fill_color, (x, y, bar_width * ratio, bar_height))
#     pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

#     # READY表示
#     if ratio >= 1:
#         font = pygame.font.SysFont(None, 22)
#         text = font.render("READY!", True, (0, 255, 100))
#         screen.blit(text, (x + bar_width // 2 - 30, y - 22))
#     else:
#         font = pygame.font.SysFont(None, 20)
#         seconds = max(1, int(cooldown_remaining / 1000) + 1)
#         text = font.render(f"{seconds}s", True, (180, 180, 180))
#         screen.blit(text, (x + bar_width // 2 - 10, y - 22))





