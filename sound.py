import pygame

def play_bgm(path="assets/bgm.mp3", volume=0.5, loop=True):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
    except pygame.error as e:
        print("🔇 BGM再生エラー:", e)

def stop_bgm():
    pygame.mixer.music.stop()

def load_sounds():
    sounds = {}
    try:
        sounds["bgm"] = True  # フラグのみでOK（再生は music 系で扱う）
        sounds["shot"] = pygame.mixer.Sound("assets/shot.wav")
        sounds["gameover"] = pygame.mixer.Sound("assets/gameover.wav")
        sounds["clear"] = pygame.mixer.Sound("assets/gameclear.wav")  # ← これを追加！
    except pygame.error as e:
        print("🎧 サウンド読み込み失敗:", e)
    return sounds