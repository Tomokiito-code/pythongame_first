import pygame
import sys
import random
from ai_tracker import SimpleAITracker
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player
from bullet import BulletManager
from enemy import generate_enemies, update_enemies, draw_enemies, get_enemy_rect
from boss import Boss
from item import create_item, update_items, draw_items, check_item_collision
from ui import draw_homing_cooldown, draw_score, draw_hp_bar, draw_text_centered, draw_restart_hint, draw_boss_hp_bar
from sound import load_sounds, play_bgm, stop_bgm
from score_log import log_score
from boss import StaticBoss

PLAYER_NAME = "智喜"
PLAYER_LEVEL = 12

# --- 初期化 ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
button_registry = {}
sounds = load_sounds()

# --- ホーム画面UI ---
def draw_home():
    screen.fill((30, 30, 40))  # 背景カラー
    title = font.render("⚔️ Shooter Game", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))

    draw_button("初級編", SCREEN_HEIGHT // 2, (0, 200, 255), "easy", "assets/icon_easy.png")
    draw_button("無限編", SCREEN_HEIGHT // 2 + 80, (255, 100, 100), "infinity", "assets/mugen.png")
    draw_button("Exit", SCREEN_HEIGHT // 2 + 160, (200, 200, 200), "exit", "assets/icon_exit.png")

def draw_button(text, y, color, tag, icon_path=None):
    btn_font = pygame.font.Font("assets/NotoSansJP-VariableFont_wght.ttf", 36)
    btn_surf = btn_font.render(text, True, color)
    text_rect = btn_surf.get_rect()

    icon_size = 32
    padding = 15

    # アイコンとテキストを合計した横幅
    total_width = icon_size + padding + text_rect.width
    rect = pygame.Rect((SCREEN_WIDTH // 2 - total_width // 2 - padding, y - 20), (total_width + padding * 2, 45))
    pygame.draw.rect(screen, (80, 80, 80), rect)

    # アイコン描画
    if icon_path:
        try:
            icon_img = pygame.image.load(icon_path)
            icon_img = pygame.transform.scale(icon_img, (icon_size, icon_size))
            icon_x = rect.x + padding
            icon_y = y
            icon_rect = icon_img.get_rect(center=(icon_x + icon_size // 2, icon_y))
            screen.blit(icon_img, icon_rect)
        except pygame.error as e:
            print(f"アイコン読み込み失敗: {icon_path} - {e}")

    # テキスト描画（アイコンの右側に配置）
    text_x = rect.x + icon_size + padding * 2
    screen.blit(btn_surf, (text_x, y - text_rect.height // 2))

    # クリック領域登録
    button_registry[tag] = rect

def check_button_click(pos):
    for tag, rect in button_registry.items():
        if rect.collidepoint(pos):
            return tag
    return None    

def run_game(screen, clock):
    play_bgm()
    background_img = pygame.transform.scale(pygame.image.load("assets/dungeon_bg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    player_img = pygame.transform.scale(pygame.image.load("assets/player.png"), (64, 64))
    enemy_img = pygame.transform.scale(pygame.image.load("assets/enemy.png"), (64, 64))
    boss_img = pygame.transform.scale(pygame.image.load("assets/boss.png"), (128, 128))
    arrow_img = pygame.transform.scale(pygame.image.load("assets/arrow.png"), (10, 32))
    homing_arrow_img = pygame.transform.scale(pygame.image.load("assets/arrow_homing.png"), (10, 32))
    item_heal_img = pygame.transform.scale(pygame.image.load("assets/item_heal.png"), (32, 32))
    item_speed_img = pygame.transform.scale(pygame.image.load("assets/item_speed.png"), (32, 32))
    fireball_img = pygame.transform.scale(pygame.image.load("assets/fireball.png"), (24, 24))

    player = Player(player_img)
    bullet_manager = BulletManager(arrow_img, homing_arrow_img)
    enemy_list = generate_enemies()
    items = []
    boss = None
    boss_spawned = False
    score = 0
    ENEMY_SPEED = 2
    game_over = False
    stage_cleared = False
    score_logged = False
    space_pressed_time = 0
    last_homing_time = 0
    homing_cooldown = 10000

    running = True
    while running:
        screen.blit(background_img, (0, 0))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    space_pressed_time = pygame.time.get_ticks()
                elif (game_over or stage_cleared) and event.key == pygame.K_r:
                    stop_bgm()
                    return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and not game_over and not stage_cleared:
                    duration = pygame.time.get_ticks() - space_pressed_time
                    now = pygame.time.get_ticks()
                    can_use_homing = now - last_homing_time >= homing_cooldown
                    is_homing = duration >= 500 and can_use_homing
                    charge_ratio = min(duration / 1000, 1)
                    bullet_speed = int(10 + (40 - 10) * charge_ratio)
                    bullet_x = player.x + player.width // 2 - arrow_img.get_width() // 2
                    bullet_manager.fire(bullet_x, player.y, is_homing, bullet_speed)
                    if is_homing:
                        last_homing_time = now
                    sounds["shot"].play()
                    space_pressed_time = 0

        if not game_over and not stage_cleared:
            player.handle_input(keys)
            player.update_hit_status()
            bullet_manager.update(enemy_list, boss)
            update_enemies(enemy_list, ENEMY_SPEED)
            update_items(items)

            for enemy in enemy_list:
                if enemy["active"] and enemy["y"] > SCREEN_HEIGHT:
                    enemy["active"] = False
                    game_over = True
                    stop_bgm()
                    sounds["gameover"].play()
                    break

            if all(not e["active"] for e in enemy_list) and not boss_spawned:
                boss = StaticBoss(boss_img, SCREEN_WIDTH // 2 - 64, 50, fireball_img)
                boss_spawned = True

            if boss and boss.active:
                boss.update()
                for fb in boss.fireballs[:]:
                    fire_rect = pygame.Rect(fb["x"] - 8, fb["y"] - 8, 16, 16)
                    if fire_rect.colliderect(player.get_hitbox()):
                        player.take_damage(20)
                        boss.fireballs.remove(fb)

            if boss:
                draw_boss_hp_bar(screen, boss.hp, boss.max_hp)

            for enemy in enemy_list:
                if enemy["active"] and get_enemy_rect(enemy).colliderect(player.get_hitbox()):
                    player.take_damage(50)
                if boss and boss.active and boss.get_hitbox().colliderect(player.get_hitbox()):
                    player.take_damage(50)

            for bullet in bullet_manager.get_bullets()[:]:
                bullet_rect = pygame.Rect(bullet["x"], bullet["y"], 10, 32)
                for enemy in enemy_list:
                    if enemy["active"] and bullet_rect.colliderect(get_enemy_rect(enemy)):
                        enemy["active"] = False
                        bullet_manager.bullets.remove(bullet)
                        score += 1
                        if random.random() < 0.3:
                            items.append(create_item(enemy["x"], enemy["y"]))
                        break
                if boss and boss.active and bullet_rect.colliderect(boss.get_hitbox()):
                    boss.take_damage(60)
                    bullet_manager.bullets.remove(bullet)
                    score += 3

            check_item_collision(items, player.rect, player)

            if hasattr(player, "speed_boost_timer") and player.speed_boost_timer:
                if pygame.time.get_ticks() - player.speed_boost_timer > 5000:
                    player.speed = 5
                    player.speed_boost_timer = 0

            if player.hp <= 0:
                game_over = True
                stop_bgm()
                sounds["gameover"].play()
            elif boss and not boss.active and not stage_cleared:
                stage_cleared = True
                stop_bgm()
                sounds["clear"].play()

        draw_score(screen, score)
        draw_hp_bar(screen, player.hp, player.max_hp)  # ✅ HPゲージ表示
        draw_enemies(enemy_list, screen, enemy_img)
        bullet_manager.draw(screen)
        draw_items(items, screen, item_heal_img, item_speed_img)
        player.draw(screen)
        if boss and boss.active:
            boss.draw(screen)

        if game_over:
            draw_text_centered(screen, "GAME OVER", 100, (255, 0, 0), 400)
            draw_restart_hint(screen)
            if not score_logged:
                log_score("GAME OVER", score)
                score_logged = True
        elif stage_cleared:
            draw_text_centered(screen, "STAGE CLEARED!", 80, (0, 255, 0), 400)
            draw_restart_hint(screen)
            if not score_logged:
                log_score("BOSS CLEARED", score)
                score_logged = True

        if keys[pygame.K_SPACE] and not game_over and not stage_cleared:
            duration = pygame.time.get_ticks() - space_pressed_time
            if duration >= 200:
                cooldown_remaining = max(0, homing_cooldown - (pygame.time.get_ticks() - last_homing_time))
                if cooldown_remaining > 0:
                    draw_homing_cooldown(screen, cooldown_remaining)

        pygame.display.update()
        clock.tick(60)

def run_infinite_battle(screen, clock):
    try:
        background_img = pygame.transform.scale(
            pygame.image.load("assets/infinity_bg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        arrow_img = pygame.transform.scale(pygame.image.load("assets/arrow.png"), (10, 32))
        homing_arrow_img = pygame.transform.scale(pygame.image.load("assets/arrow_homing.png"), (10, 32))
        player_img = pygame.transform.scale(pygame.image.load("assets/player.png"), (64, 64))
    except pygame.error as e:
        print("画像読み込みエラー:", e)
        return

 # 🔊 サウンド読み込み（修正ポイント）
    sounds = load_sounds()
    if "bgm" in sounds and sounds["bgm"]:
        play_bgm()
    else:
        print("⚠️ BGMが読み込まれていないため、再生できません。")

    stage_level = 1
    score = 0
    player_hits = 0
    player = Player(player_img)
    bullet_manager = BulletManager(arrow_img, homing_arrow_img)
    active_boss = Boss(stage_level)
    boss_group = pygame.sprite.Group(active_boss)
    ai_tracker = SimpleAITracker()

    running = True
    print("無限編スタート")


    while True:
        screen.blit(background_img, (0, 0))

        # 🎮 入力・プレイヤー更新
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update_hit_status()

        # 🧠 毎フレーム学習データ記録
        ai_tracker.record(player.rect.centerx, player.damage_timer > 0)

        # 🎯 イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                stop_bgm()
                return
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                bullet_x = player.x + player.width // 2 - 5
                bullet_manager.fire(bullet_x, player.y, is_homing=False, speed=16)
                sounds["shot"].play()

        # 🎯 衝突判定（プレイヤー弾 vs ボス）
        for bullet in bullet_manager.get_bullets()[:]:
            bullet_rect = pygame.Rect(bullet["x"], bullet["y"], 10, 32)
            if bullet_rect.colliderect(active_boss.get_hitbox()):
                bullet_manager.bullets.remove(bullet)
                active_boss.health -= 1
                player_hits += 1

        # 🔥 衝突判定（ボス弾 vs プレイヤー）
        for fb in active_boss.fireballs[:]:
            fire_rect = pygame.Rect(fb["x"] - 8, fb["y"] - 8, 16, 16)
            if fire_rect.colliderect(player.get_hitbox()):
                player.take_damage(20)
                active_boss.fireballs.remove(fb)

        # 🏆 ステージ進行判定
        if player_hits >= 5 or active_boss.health <= 0:
            stage_level += 1
            score += 100
            player_hits = 0
            draw_text_centered(screen, "Boss Defeated!", 40, (255, 255, 0), SCREEN_HEIGHT // 2)
            pygame.display.update()
            pygame.time.wait(1500)

            # 🧠 AI戦略反映（解析＆適応）
            preferred_side, config = ai_tracker.get_strategy(SCREEN_WIDTH)
            active_boss = Boss(stage_level, strategy=preferred_side)
            active_boss.set_attack_pattern(config)
            boss_group = pygame.sprite.Group(active_boss)

        # 💀 ゲームオーバー
        if player.hp <= 0:
            draw_text_centered(screen, "GAME OVER", 80, (255, 0, 0), SCREEN_HEIGHT // 2)
            stop_bgm()
            sounds["gameover"].play()
            pygame.display.update()
            pygame.time.wait(2000)
            return

        # 👾 ボス更新
        for boss in boss_group:
            if boss.health > 0:
                boss.update(player)

        # 🔄 弾更新・描画
        bullet_manager.update([], active_boss)
        screen.blit(background_img, (0, 0))
        player.draw(screen)
        active_boss.draw(screen)
        bullet_manager.draw(screen)

        draw_boss_hp_bar(screen, active_boss.health, 100 + stage_level * 20)
        draw_text_centered(screen, f"無限ボス Lv.{stage_level}", 36, (255, 100, 255), 50)
        draw_text_centered(screen, f"Score: {score}", 28, (255, 255, 255), 90)

        pygame.display.update()
        clock.tick(60)


while True:
    draw_home()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            action = check_button_click(event.pos)
            if action == "easy":
                run_game(screen, clock)
            elif action == "infinity":
                run_infinite_battle(screen, clock)
            elif action == "exit":
                pygame.quit()
                sys.exit()

    pygame.display.update()
    clock.tick(60)