from math import pi, tan
from random import randint

#import ez_profile
import pygame

from camera import Camera
from mesh import Mesh
from shapes import Box, Quad
from util import (BACK, DOWN, FORWARD, LEFT, RIGHT, UP, Vec2, Vec3, color_mult,
                  draw_text, map_range, rotate_by_vec, z_average)

SENSITIVITY = 0.6
S_WIDTH = 1280
S_HEIGHT = 720
S_CENTER = (S_WIDTH / 2, S_HEIGHT / 2)
S_CENTER_X = S_CENTER[0]
S_CENTER_Y = S_CENTER[1]


class Bullet(Mesh):
    def __init__(self, pos, vel):
        super().__init__(Box(2, 2, 2), pos, (0, 0, 0))
        self.life_time = 2
        self.vel = vel

    def update(self, dt):
        self.pos += self.vel * dt
        self.life_time -= dt
        if self.life_time <= 0:
            return True
        return False


def main():
    pygame.init()
    flags = pygame.FULLSCREEN | pygame.SCALED
    disp = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    clock = pygame.time.Clock()

    delta = 0
    cam = Camera(90, 0.1, 1000, (0, 1, 10), (0, 0, 0))
    cam.set_viewport(S_WIDTH, S_HEIGHT)
    cam.set_drawmode(Camera.FACES)

    meshs = []
    cube = Mesh(Box(2, 2, 2), (-10, 1, 0), (0, 0, 0), Vec3(0, 0, 128))
    meshs.append(cube)
    meshs.append(Mesh(Box(2, 5, 2), (10, 2.5, 0), (0, 0, 0), Vec3(198, 0, 64)))
    meshs.append(Mesh(Quad(100, 100), (0, 0, 0), (90, 0, 0), (0, 128, 0)))
    meshs.append(Mesh.from_obj("./cow.obj", (0, 1, 0), (0, 0, 0)))

    bullets = []

    running = True
    display_mode = Camera.FACES
    pygame.mouse.set_pos(S_CENTER)
    pygame.mouse.set_visible(False)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_m:
                    display_mode = (display_mode + 1) % 8
                    cam.set_drawmode(display_mode)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # print("Pew")
                bullets.append(
                    Bullet(
                        cam.pos,
                        cam.camera_forward() * 100,
                    )
                )
                meshs.append(bullets[-1])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            cam.pos += LEFT.rotate_y(-cam.rot.y) * 3 * delta
        if keys[pygame.K_d]:
            cam.pos += RIGHT.rotate_y(-cam.rot.y) * 3 * delta
        if keys[pygame.K_w]:
            cam.pos += FORWARD.rotate_y(-cam.rot.y) * 3 * delta
        if keys[pygame.K_s]:
            cam.pos += BACK.rotate_y(-cam.rot.y) * 3 * delta
        if keys[pygame.K_e]:
            cam.pos += UP * 3 * delta
        if keys[pygame.K_q]:
            cam.pos += DOWN * 3 * delta

        rel = pygame.mouse.get_pos()
        pygame.mouse.set_pos(S_CENTER)
        cam.rot.y += (rel[0] - S_CENTER_X) * SENSITIVITY
        cam.rot.x += (rel[1] - S_CENTER_Y) * SENSITIVITY

        if keys[pygame.K_LEFT]:
            cam.rot.y += -30 * delta
        if keys[pygame.K_RIGHT]:
            cam.rot.y += 30 * delta
        if keys[pygame.K_UP]:
            cam.rot.x += 30 * delta
        if keys[pygame.K_DOWN]:
            cam.rot.x -= 30 * delta

        cam.rot.x = max(cam.rot.x, -80)
        cam.rot.x = min(cam.rot.x, 80)
        cube.rot.x += 40 * delta
        cube.rot.y += 25 * delta

        for bullet in bullets[::-1]:
            if bullet.update(delta):
                meshs.remove(bullet)
                bullets.remove(bullet)

        cam.clear()
        cam.render_multi(meshs)
        cam.draw(disp, (0, 0))

        draw_text(disp, str(cam.pos), Vec2(10, 10))
        draw_text(disp, str(cam.rot), Vec2(10, 24))
        draw_text(disp, str(display_mode), Vec2(10, 38))
        draw_text(disp, str(len(bullets)), Vec2(10, 52))
        pygame.display.set_caption(str(clock.get_fps()))
        pygame.display.flip()
        delta = clock.tick(60) / 1000

if __name__ == "__main__":
    main()