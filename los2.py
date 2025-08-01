import pygame
import random
import math
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flight Simulator")

# Загрузка изображения самолёта
plane_img = pygame.image.load("/storage/emulated/0/Plane.png")
plane_img = pygame.transform.scale(plane_img, (80, 40))  # Устанавливаем размер самолёта 150x40 пикселей
plane_rect = plane_img.get_rect()

plane_x, plane_y = 100, HEIGHT // 2
velocity_y = 0
gravity = 0.6
lift = -6

speed = 300  # Начальная скорость (км/ч)
max_speed = 800
min_speed = 200

# Препятствия
obstacle_width = 150  # Обычная ширина препятствий
obstacle_gap = 160
obstacle_speed = 3
obstacles = []
obstacle_timer = 0.3
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

# Функции для анимации и звука
def play_fireworks():
    colors = [(255, 0, 0), (255, 255, 0), (0, 0, 255), (139, 69, 19), (0, 0, 0), (0, 255, 255), (255, 192, 203), (0, 255, 0)]
    for _ in range(50):
        color = random.choice(colors)
        pygame.draw.circle(screen, color, (random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)), random.randint(5, 20))
        pygame.display.flip()
        time.sleep(0.05)

def play_lose_sound():
    lose_sound = pygame.mixer.Sound("/storage/emulated/0/Vzriv.mp3")  # Путь к звуку проигрыша
    lose_sound.play()

def play_win_sound():
    win_sound = pygame.mixer.Sound("/storage/emulated/0/Zvuuk143.mp3")  # Путь к звуку победы
    win_sound.play()

def display_win():
    text = font.render("YOU WIN!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.fill((0, 0, 0))  # Черный фон для контраста
    screen.blit(text, text_rect)
    pygame.display.flip()
    play_fireworks()  # Показ фейерверков
    play_win_sound()  # Воспроизведение звука победы

def display_lose():
    text = font.render("YOU LOSE!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.fill((0, 0, 0))  # Черный фон для контраста
    screen.blit(text, text_rect)
    pygame.display.flip()
    play_lose_sound()  # Воспроизведение звука проигрыша
    time.sleep(2)  # Пауза для отображения текста

# Основной игровой цикл
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((135, 206, 250))

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
    speed += (dx / joystick_radius) * 5
    speed -= 15 / 30  # Автоматическое снижение скорости
    speed = max(min_speed, min(max_speed, speed))

    if speed <= min_speed:
        display_lose()  # Проигрыш при слишком низкой скорости
        running = False

    # Генерация препятствий
    if pygame.time.get_ticks() - obstacle_timer > obstacle_interval:
        obstacle_timer = pygame.time.get_ticks()
        obstacle_height = random.randint(100, 400)
        obstacles.append([WIDTH, obstacle_height, False])  # False означает, что счёт не начислен

    # Отрисовка препятствий
    for obs in obstacles[:]:
        # Для всех препятствий, кроме 100-го, делаем ширину в 3 раза меньше
        if score % 100 == 99:  # Если это 100-е препятствие (особое)
            obstacle_width = 150  # Аэропорт (ширина в 2 раза меньше, чем раньше)
        else:
            obstacle_width = 50  # Ширина всех остальных препятствий в 3 раза меньше обычной (150 -> 50)

        obs[0] -= obstacle_speed * (speed / 300)  # Скорость зависит от текущей скорости самолёта
        pygame.draw.rect(screen, (0, 255, 0), (obs[0], 0, obstacle_width, obs[1]))
        pygame.draw.rect(screen, (0, 255, 0), (obs[0], obs[1] + obstacle_gap, obstacle_width, HEIGHT - obs[1] - obstacle_gap))

        # Проверка столкновения
        if (plane_x + plane_rect.width > obs[0] and plane_x < obs[0] + obstacle_width) and \
           (plane_y < obs[1] or plane_y + 40 > obs[1] + obstacle_gap):
            if score % 100 != 99:  # Проигрыш только для обычных препятствий, не для особого
                display_lose()  # Завершаем игру при столкновении
                running = False

        # Начисление очков за пройденные препятствия
        if obs[0] + obstacle_width < plane_x and not obs[2]:
            score += 1
            obs[2] = True  # Отмечаем препятствие как пройденное

        if obs[0] + obstacle_width < 0:
            obstacles.remove(obs)

    # Проверка на победу (если приземлиться с нужной скоростью на 100-м препятствии)
    if score % 100 == 99 and plane_y + 40 >= HEIGHT and abs(speed) < 318:
        display_win()
        time.sleep(2)  # Пауза, чтобы табличка "YOU WIN!" оставалась видимой
        running = False

    # Проверка на поражение при посадке с слишком высокой скоростью
    if plane_y + 40 >= HEIGHT and abs(speed) > 350:
        display_lose()  # Проигрыш при посадке с высокой скоростью
        running = False

    # Отрисовка самолёта
    screen.blit(plane_img, (plane_x, plane_y))

    # Отрисовка счёта и скорости
    screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))
    screen.blit(font.render(f"Speed: {int(speed)} km/h", True, (0, 0, 0)), (10, 40))

    # Отрисовка джойстика
    pygame.draw.circle(screen, (50, 50, 50), joystick_center, joystick_radius)
    pygame.draw.circle(screen, (200, 0, 0), joystick_knob_pos, joystick_knob_radius)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()