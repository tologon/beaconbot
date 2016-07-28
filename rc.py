# Manual control of the robot
# WASD - forward, left, back, right
# Up Arrow - Speed up
# Down Arrow - Slow down
# Space - "brake"
import atexit
from platform import Platform
import pygame
from pygame.locals import *

platform = Platform()
atexit.register(platform.shutdown)

# pygame stuff

pygame.init()
pygame.display.set_mode((100,100), NOFRAME)
clock = pygame.time.Clock()
speed = 200


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            break

    keys = pygame.key.get_pressed()
    left_power = 0
    right_power = 0

    if keys[K_a]:
        # turn left
        left_power -= speed
        right_power += speed
    if keys[K_d]:
        # turn right
        left_power += speed
        right_power -= speed
    if keys[K_w]:
        # go forward
        left_power += speed
        right_power += speed
    if keys[K_s]:
        # go backward
        left_power -= speed
        right_power -= speed

    if keys[K_UP]:
        if speed + 1 <= 255:
            speed += 5
    if keys[K_DOWN]:
        if speed -1 >= 60:
            speed -= 5
    if keys[K_SPACE]:
        left_power = -20
        right_power = -20

    if keys[K_ESCAPE] or keys[K_q] or keys[KMOD_LCTRL|K_c]:
        break

    # apply selected power
    platform._set_power_directional('LEFT', left_power)
    platform._set_power_directional('RIGHT', right_power)

    clock.tick(20)

pygame.quit()
