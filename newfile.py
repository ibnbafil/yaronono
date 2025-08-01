import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flight Simulator")

plane = pygame.Surface((80, 40))
plane.fill((255, 0, 0))

plane_x, plane_y = 100, HEIGHT // 2
velocity = 0
gravity = 0.3
lift = -6

# Кнопки
button_up = pygame.Rect(650, 450, 100, 50)
button_down = pygame.Rect(650, 520, 100, 50)

# Препятствия
obstacle_width = 50
obstacle_gap = 200
obstacle_speed = 3
obstacles = []
obstacle_timer = 0
obstacle_interval = 2000  # Время между препятствиями (мс)

clock = pygame.time.Clock()
running = True

while running:
    screen.fill((135, 206, 250))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if button_up.collidepoint(x, y):
                velocity = lift
            if button_down.collidepoint(x, y):
                velocity = -lift

    velocity += gravity
    plane_y += velocity

    # Ограничение самолёта в границах экрана
    if plane_y < 0:
        plane_y = 0
        velocity = 0
    if plane_y + 40 > HEIGHT:
        plane_y = HEIGHT - 40
        velocity = 0

    # Генерация препятствий
    if pygame.time.get_ticks() - obstacle_timer > obstacle_interval:
        obstacle_timer = pygame.time.get_ticks()
        obstacle_height = random.randint(100, 400)
        obstacles.append([WIDTH, obstacle_height])

    # Отрисовка препятствий
    for obs in obstacles[:]:
        obs[0] -= obstacle_speed
        pygame.draw.rect(screen, (0, 255, 0), (obs[0], 0, obstacle_width, obs[1]))
        pygame.draw.rect(screen, (0, 255, 0), (obs[0], obs[1] + obstacle_gap, obstacle_width, HEIGHT - obs[1] - obstacle_gap))

        # Проверка столкновения
        if (plane_x + 80 > obs[0] and plane_x < obs[0] + obstacle_width) and \
           (plane_y < obs[1] or plane_y + 40 > obs[1] + obstacle_gap):
            running = False  # Завершаем игру при столкновении

        if obs[0] + obstacle_width < 0:
            obstacles.remove(obs)

    # Отрисовка самолёта
    screen.blit(plane, (plane_x, plane_y))

    # Отрисовка кнопок
    pygame.draw.rect(screen, (200, 0, 0), button_up)
    pygame.draw.rect(screen, (0, 0, 200), button_down)
    font = pygame.font.Font(None, 36)
    screen.blit(font.render("UP", True, (255, 255, 255)), (675, 460))
    screen.blit(font.render("DOWN", True, (255, 255, 255)), (660, 530))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()