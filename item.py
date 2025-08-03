# item.py
import pygame
import random

ITEM_SIZE = 32

def create_item(x, y):
    item_type = random.choice(["heal", "speed"])
    return {
        "x": x,
        "y": y,
        "type": item_type,
        "float_offset": 0,
        "dir": 1
    }

def update_items(items):
    for item in items:
        item["float_offset"] += item["dir"]
        if abs(item["float_offset"]) > 10:
            item["dir"] *= -1

def draw_items(items, screen, heal_img, speed_img):
    for item in items:
        img = heal_img if item["type"] == "heal" else speed_img
        float_y = item["y"] + item["float_offset"]
        screen.blit(img, (item["x"], float_y))

def check_item_collision(items, player_rect, player):
    collected = []
    for item in items[:]:
        float_y = item["y"] + item["float_offset"]
        item_rect = pygame.Rect(item["x"], float_y, ITEM_SIZE, ITEM_SIZE)
        if item_rect.colliderect(player.rect):
            if item["type"] == "heal":
                player.hp = min(player.max_hp, player.hp + 30)
            else:
                player.speed += 2
                player.speed_boost_timer = pygame.time.get_ticks()
            collected.append(item)
            items.remove(item)
    return collected