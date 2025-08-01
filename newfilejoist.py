import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flight Simulator")

plane = pygame.Surface((80, 40))
plane.fill((255, 0, 0))

plane_x, plane_y = 100, HEIGHT // 2
velocity_y = 0
gravity = 0.3
lift = -6

speed = 300  # Начальная скорость (км/ч)
max_speed = 600
min_speed = 200

# Препятствия
obstacle_width = 50
obstacle_gap = 160
obstacle_speed = 3
obstacles = []
obstacle_timer = 0
obstacle_interval = 2000  # Время между препятствиями (мс)

# Джойстик
joystick_center = (100, HEIGHT - 100)
joystick_radius = 40
joystick_knob_radius = 20
joystick_knob_pos = list(joystick_center)
joystick_active = False

# Счётчик препятствий
score = 0
font = pygame.font.Font(None, 36)

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
            if math.hypot(x - joystick_center[0], y - joystick_center[1]) < joystick_radius:
                joystick_active = True
                joystick_knob_pos = [x, y]
        if event.type == pygame.MOUSEBUTTONUP:
            joystick_active = False
            joystick_knob_pos = list(joystick_center)  # Возвращаем в центр
        if event.type == pygame.MOUSEMOTION and joystick_active:
            x, y = event.pos
            dx, dy = x - joystick_center[0], y - joystick_center[1]
            distance = math.hypot(dx, dy)
            if distance > joystick_radius:
                dx = dx / distance * joystick_radius
                dy = dy / distance * joystick_radius
            joystick_knob_pos = [joystick_center[0] + dx, joystick_center[1] + dy]

    # Управление самолётом с джойстика
    dx = joystick_knob_pos[0] - joystick_center[0]
    dy = joystick_knob_pos[1] - joystick_center[1]

    # Вертикальное движение
    if dy < 0:
        velocity_y = lift * (-dy / joystick_radius)
    elif dy > 0:
        velocity_y = -lift * (dy / joystick_radius)
    else:
        velocity_y += gravity  # Применяем гравитацию

    plane_y += velocity_y

    # Ограничение самолёта в границах экрана
    if plane_y < 0:
        plane_y = 0
        velocity_y = 0
    if plane_y + 40 > HEIGHT:
        plane_y = HEIGHT - 40
        velocity_y = 0

    # Горизонтальное движение джойстика изменяет скорость
    speed += (dx / joystick_radius) * 5  # Увеличение/уменьшение скорости
    speed -= 15 / 30  # Автоматическое снижение скорости
    speed = max(min_speed, min(max_speed, speed))

    if speed <= min_speed:
        running = False  # Проигрыш при слишком низкой скорости

    # Генерация препятствий
    if pygame.time.get_ticks() - obstacle_timer > obstacle_interval:
        obstacle_timer = pygame.time.get_ticks()
        obstacle_height = random.randint(100, 400)
        obstacles.append([WIDTH, obstacle_height, False])  # False означает, что счёт не начислен

    # Отрисовка препятствий
    for obs in obstacles[:]:
        obs[0] -= obstacle_speed * (speed / 300)  # Скорость зависит от текущей скорости самолёта
        pygame.draw.rect(screen, (0, 255, 0), (obs[0], 0, obstacle_width, obs[1]))
        pygame.draw.rect(screen, (0, 255, 0), (obs[0], obs[1] + obstacle_gap, obstacle_width, HEIGHT - obs[1] - obstacle_gap))

        # Проверка столкновения
        if (plane_x + 80 > obs[0] and plane_x < obs[0] + obstacle_width) and \
           (plane_y < obs[1] or plane_y + 40 > obs[1] + obstacle_gap):
            running = False  # Завершаем игру при столкновении

        # Начисление очков за пройденные препятствия
        if obs[0] + obstacle_width < plane_x and not obs[2]:
            score += 1
            obs[2] = True  # Отмечаем препятствие как пройденное

        if obs[0] + obstacle_width < 0:
            obstacles.remove(obs)

    # Отрисовка самолёта
    screen.blit(plane, (plane_x, plane_y))

    # Отрисовка счёта и скорости
    screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))
    screen.blit(font.render(f"Speed: {int(speed)} km/h", True, (0, 0, 0)), (10, 40))

    # Отрисовка джойстика
    pygame.draw.circle(screen, (50, 50, 50), joystick_center, joystick_radius)
    pygame.draw.circle(screen, (200, 0, 0), joystick_knob_pos, joystick_knob_radius)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()