# ===== ライブラリ読み込み =====
import pygame             # ゲーム用ライブラリ
import random             # 敵出現位置をランダムに設定するため
import datetime           # スコアログに時間を記録するため

# ===== ゲームウィンドウ初期化 =====
pygame.init()
screen = pygame.display.set_mode((1200, 800))            # ウィンドウサイズ設定
pygame.display.set_caption("Shooter Game")               # ウィンドウのタイトル表示

# ===== グラフィック素材読み込み =====
background_img = pygame.image.load("dungeon_bg.png")     # 背景画像
background_img = pygame.transform.scale(background_img, (1200, 800))  # リサイズ

player_img = pygame.image.load("player.png")             # プレイヤー画像
player_img = pygame.transform.scale(player_img, (64, 64))

enemy_img = pygame.image.load("enemy.png")               # 敵画像
enemy_img = pygame.transform.scale(enemy_img, (64, 64))

arrow_img = pygame.image.load("arrow.png")               # 弾（矢）画像
arrow_img = pygame.transform.scale(arrow_img, (10, 32))

homing_arrow_img = pygame.image.load("arrow_homing.png")  # ← ファイル名は任意でOK！
homing_arrow_img = pygame.transform.scale(homing_arrow_img, (10, 32))  # 通常矢と同じサイズに調整

# ===== 音楽・効果音読み込みと再生開始 =====
pygame.mixer.music.load("bgm.mp3")                       # BGM
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)                              # 無限ループ

shot_se = pygame.mixer.Sound("shot.wav")                 # 発射音
gameover_se = pygame.mixer.Sound("gameover.wav")         # ゲームオーバー音
gameclear_se = pygame.mixer.Sound("gameclear.wav")       # ステージクリア音


# ===== アイテム画像の読み込み（仮素材）=====
item_heal_img = pygame.image.load("item_heal.png")
item_heal_img = pygame.transform.scale(item_heal_img, (32, 32))

item_speed_img = pygame.image.load("item_speed.png")
item_speed_img = pygame.transform.scale(item_speed_img, (32, 32))

# ===== アイテム関連の変数追加 =====
items = []  # 出現中のアイテムリスト
speed_boost_timer = 0  # スピードアップの効果時間管理


# ===== ゲーム状態変数の初期化 =====
player_x = 400                                           # プレイヤー初期位置（X）
player_y = 600 - player_img.get_height()                 # プレイヤー初期位置（Y）
player_speed = 5                                         # プレイヤー移動スピード
enemy_speed = 2                                          # 敵の移動スピード
bullet_speed = 5                                         # 矢のスピード
speed = 2                                                # ← bullet_speed より少し遅めにしてあえてモッサリ追尾 
player_rect = pygame.Rect(player_x, player_y, 64, 64)    # プレイヤーの当たり判定矩形
player_hp = 100                  # 現在のHP
max_hp = 100                     # 最大HP
bullets = []                     # 矢リスト（辞書でx, y座標を管理）
enemy_list = []                  # 敵リスト
fallen_enemies = 0               # 落下した敵の数
score = 0                        # スコア（撃破数）
game_over = False                # ゲームオーバーフラグ
stage_cleared = False            # ステージクリアフラグ
player_hit = False               # プレイヤーが敵に当たったか
hit_timer = 0                    # 被弾時間記録
score_logged = False             # スコア記録済みか
clear_sound_played = False       # クリア効果音が再生済みか
space_pressed_time = 0  # 追加（変数）

# ===== 関数定義 =====

# 敵を生成する関数（ランダムX座標、Y座標上部）
def generate_enemies(num=5):
    return [{"x": random.randint(0, 1136), "y": random.randint(-600, -64), "active": True} for _ in range(num)]

# 中央にテキストを描画（テキスト、サイズ、色、Y座標）
def draw_centered_text(text_str, size, color, y):
    font = pygame.font.SysFont(None, size)
    text = font.render(text_str, True, color)
    screen.blit(text, text.get_rect(center=(600, y)))

# ゲームオーバーをトリガーする（BGM停止＋SE再生）
def trigger_game_over():
    global game_over
    if not game_over:
        game_over = True
        pygame.mixer.music.stop()
        gameover_se.play()

# ゲームの状態を初期化（Rキーで再開時に使用）
def reset_game():
    global player_x, player_y, bullets, enemy_list, fallen_enemies
    global score, game_over, stage_cleared, player_hit, hit_timer
    global score_logged, clear_sound_played
    global player_hp
    global items

    player_x = 400
    player_y = 600 - player_img.get_height()
    bullets = []
    enemy_list = generate_enemies()     # 新しい敵を生成
    fallen_enemies = 0
    score = 0
    game_over = False
    stage_cleared = False
    player_hit = False
    hit_timer = 0
    score_logged = False
    clear_sound_played = False
    pygame.mixer.music.load("bgm.mp3")     # ← この2行は再度BGMながす
    pygame.mixer.music.play(-1)
    player_hp = max_hp                     # ← 忘れずにHPも回復！
    restart_hint_timer = pygame.time.get_ticks()   #現在時刻をセット
    items = []  # ← ★ドロップアイテムも初期化！！

# ===== 敵初期生成・タイマー開始 =====
enemy_list = generate_enemies()
clock = pygame.time.Clock()
running = True

# ===== メインゲームループ =====
while running:
    screen.blit(background_img, (0, 0))                         # 背景描画
    font = pygame.font.SysFont(None, 40)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # スコア描画
    screen.blit(score_text, (10, 10))
    # HPバー背景
    pygame.draw.rect(screen, (100, 100, 100), (10, 50, 200, 20))  # グレー背景

    # HPゲージ（赤色）
    bar_width = int(200 * player_hp / max_hp)
    pygame.draw.rect(screen, (255, 50, 50), (10, 50, bar_width, 20))

    # HP数値（小さく白文字で）
    font = pygame.font.SysFont(None, 24)
    hp_text = font.render(f"HP: {player_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (220, 48))

    # === イベント処理 ===
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # SPACEで矢を発射（ゲーム中のみ）
        # if not game_over and not stage_cleared and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        #     bullet_x = player_x + player_img.get_width() // 2 - arrow_img.get_width() // 2
        #     shot_se.play()
        
        # 最初に押された時刻だけ記録
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            space_pressed_time = pygame.time.get_ticks()

        # キーを離した瞬間に発射処理（1回だけ）
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if not game_over and not stage_cleared:
                press_duration = pygame.time.get_ticks() - space_pressed_time
                bullet_x = player_x + player_img.get_width() // 2 - arrow_img.get_width() // 2
                homing = press_duration >= 500  # 0.5秒以上押してたらホーミング弾
                bullets.append({"x": bullet_x, "y": player_y, "homing": homing,"created_at": pygame.time.get_ticks()})
                shot_se.play()

        # ゲームオーバー or クリア時にRキーでリスタート
        if (game_over or stage_cleared) and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()
            restart_hint_timer = pygame.time.get_ticks()  # ← ここで初めて記録！

    # ===== アイテムの描画・取得判定 =====
    for item in items[:]:  # items リストをコピーしてループ
        # 浮遊演出
        item["float_offset"] += item["dir"]
        if abs(item["float_offset"]) > 10:
            item["dir"] *= -1
        float_y = item["y"] + item["float_offset"]

        # アイテム種類に応じて画像選択
        img = item_heal_img if item["type"] == "heal" else item_speed_img
        screen.blit(img, (item["x"], float_y))

        # 当たり判定（プレイヤーに拾われたか）
        item_rect = pygame.Rect(item["x"], float_y, 32, 32)
        if item_rect.colliderect(player_rect):
            if item["type"] == "heal":
                player_hp = min(max_hp, player_hp + 30)  # 回復だが最大HPを超えない
            else:
                player_speed += 2
                speed_boost_timer = pygame.time.get_ticks()
            items.remove(item)

    # === ゲーム中の処理 ===
    if not game_over and not stage_cleared:
        # プレイヤーが被弾し一定時間経過後にゲームオーバー
        if player_hit and pygame.time.get_ticks() - hit_timer > 100:
            if player_hp <= 0:
                trigger_game_over()
            player_hit = False         # 攻撃演出を解除

        # プレイヤー移動（矢印キー）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < 1200 - 64:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < 800 - 64:
            player_y += player_speed

        player_rect.topleft = (player_x, player_y)
        hitbox = player_rect.inflate(-16, -10)  # ヒット判定縮小

        now = pygame.time.get_ticks()  # ← 先に取得して使い回す

        # === 弾の移動・削除 ===
        for bullet in bullets:
            if bullet.get("homing"):
                # 最も近い敵を探す
                target = None
                min_dist = float("inf")
                for e in enemy_list:
                    if e["active"]:
                        dx = e["x"] - bullet["x"]
                        dy = e["y"] - bullet["y"]
                        dist = dx**2 + dy**2
                        if dist < min_dist:
                            min_dist = dist
                            target = e
                # ターゲットに向かって追尾
                if target:
                    dx = target["x"] - bullet["x"]
                    dy = target["y"] - bullet["y"]
                    homing_strength = 0.025
                    bullet["x"] += dx * homing_strength
                    bullet["y"] += dy * homing_strength
            else:
                bullet["y"] -= bullet_speed

        # === 弾の削除（通常弾 or ホーミング弾の寿命）===
        bullets = [
            b for b in bullets
            if (
                (not b.get("homing") and b["y"] > -32) or
                (b.get("homing") and now - b.get("created_at", 0) < 5000)
            )
        ]

        # === 弾の描画 ===
        for bullet in bullets:
            if bullet.get("homing"):
                screen.blit(homing_arrow_img, (bullet["x"], bullet["y"]))
            else:
                screen.blit(arrow_img, (bullet["x"], bullet["y"]))   
                   
        for bullet in bullets:
            if bullet.get("homing"):
                screen.blit(homing_arrow_img, (bullet["x"], bullet["y"]))
            else:
                screen.blit(arrow_img, (bullet["x"], bullet["y"]))

        for bullet in bullets:
            if bullet.get("homing"):
                # 最も近い敵に向かって移動
                target = None
                min_dist = float("inf")
                for e in enemy_list:
                    if e["active"]:
                        dx = e["x"] - bullet["x"]
                        dy = e["y"] - bullet["y"]
                        dist = dx**2 + dy**2
                        if dist < min_dist:
                            min_dist = dist
                            target = e
                # ターゲットに向かって徐々に吸い寄せ
                if target:
                    dx = target["x"] - bullet["x"]
                    dy = target["y"] - bullet["y"]
                    homing_strength = 0.1  # 小さくするほどゆっくり曲がる
                    bullet["x"] += dx * homing_strength
                    bullet["y"] += dy * homing_strength
            else:
                bullet["y"] -= bullet_speed


        for enemy in enemy_list:
            if enemy["active"]:
                enemy["y"] += enemy_speed
                if enemy["y"] > 800:
                    enemy["active"] = False
                    fallen_enemies += 1
                rect = pygame.Rect(enemy["x"], enemy["y"], 64, 64)
                screen.blit(enemy_img, (enemy["x"], enemy["y"]))

                # プレイヤーとの接触判定
                if rect.colliderect(hitbox) and not player_hit:
                    player_hit = True
                    hit_timer = pygame.time.get_ticks()
                    player_hp -= 50

                # 🔽 弾と敵の衝突チェックは「このループ内で」行う
                for bullet in bullets:
                    bullet_rect = pygame.Rect(bullet["x"], bullet["y"], 10, 32)
                    if bullet_rect.colliderect(rect):
                        enemy["active"] = False
                        bullets.remove(bullet)
                        score += 1

                        # 🎁 アイテムドロップ（30%の確率）
                        if random.random() < 0.3:
                            item_type = random.choice(["heal", "speed"])
                            items.append({
                                "x": enemy["x"],
                                "y": enemy["y"],
                                "type": item_type,
                                "float_offset": 0,
                                "dir": 1
                            })
                        break  # この敵にはもう当たったので、弾チェックは抜ける
        
        # 敵を1体でも見逃したらゲームオーバー
        if fallen_enemies >= 1 and not player_hit:
            trigger_game_over()

        # 全敵撃破でステージクリア
        if all(not e["active"] for e in enemy_list) and not game_over:
            stage_cleared = True

        # ステージクリア時の演出（音再生）
        if stage_cleared and not clear_sound_played:
            clear_sound_played = True
            pygame.mixer.music.stop()
            gameclear_se.play()

        # ===== スピードアップの持続判定（5秒で元に戻す）=====
        if speed_boost_timer and pygame.time.get_ticks() - speed_boost_timer > 5000:
            player_speed = 5  # 元の速度に戻す
            speed_boost_timer = 0

    # === プレイヤーの描画 ===
    if player_hit:
        pygame.draw.rect(screen, (255, 0, 0), (player_x, player_y, 64, 64))  # 被弾時：赤い四角で描画（点滅演出用）
    else:
        screen.blit(player_img, (player_x, player_y))                        # 通常時：プレイヤー画像を表示

    # === ゲームオーバー時のテキストとスコア記録 ===
    if game_over:
        draw_centered_text("GAME OVER", 100, (255, 0, 0), 400)               # GAME OVER を中央に表示
        if game_over and not score_logged:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")         # 現在日時取得
            with open("score_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{now}] GAME OVER - Score: {score}\n")             # スコアをテキストファイルに記録
            score_logged = True

    # === ステージクリア時のテキストとスコア記録 ===
    if stage_cleared:
        draw_centered_text("STAGE CLEARED!", 80, (0, 255, 0), 400)           # クリア時は緑色で表示
        if not score_logged:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            with open("score_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{now}] STAGE CLEARED - Score: {score}\n")         # ログ記録
            score_logged = True

    # === 再スタートのヒント表示（ゲーム終了 or クリア時）===
    # 再スタート後5秒以内なら表示（5000ミリ秒）
    now = pygame.time.get_ticks()
    if game_over or stage_cleared:
        draw_centered_text("Press R to Restart", 40, (200, 200, 200), 500)



    # === 描画を画面に反映し、FPSを一定に保つ ===
    pygame.display.update()     # 描画内容を一気に更新
    clock.tick(60)              # 1秒あたり60フレームに制御（=FPS60）

# === ゲーム終了時：ウィンドウを閉じて終了処理 ===
pygame.quit()