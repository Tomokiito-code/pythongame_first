import random
import pygame

def generate_enemies(n=5):
    return [{"x": random.randint(0, 1136), "y": random.randint(-600, -64), "active": True} for _ in range(n)]

def update_enemies(enemies, speed):
    for e in enemies:
        if e["active"]:
            e["y"] += speed

def draw_enemies(enemies, screen, img):
    for e in enemies:
        if e["active"]:
            screen.blit(img, (e["x"], e["y"]))

def get_enemy_rect(e):
    return pygame.Rect(e["x"], e["y"], 64, 64)