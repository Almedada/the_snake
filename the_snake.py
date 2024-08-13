from random import randint
import pygame as pg
import os

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 11

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()

# Словарь для управления поворотами
TURNS = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT
}

# Файл для хранения рекордов
SCORES_FILE = "scores.txt"


def load_scores():
    """Загружает таблицу рекордов из файла."""
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as file:
            scores = file.readlines()
        return [int(score) for score in scores]
    return []


def save_score(score):
    """Сохраняет новый рекорд в файл."""
    scores = load_scores()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:10]  # Топ10
    with open(SCORES_FILE, "w") as file:
        for scor in scores:
            file.write(f"{scor}\n")


def display_scores():
    """Выводит таблицу рекордов на экран."""
    scores = load_scores()
    font = pg.font.SysFont(None, 36)
    y = 50
    for score in scores:
        text = font.render(f"{score}", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        y += 40


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self):
        # Центр экрана для начальной позиции
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self):
        """Метод для отрисовки объекта на экране."""
        pass

    def randomize_position(self):
        """Генерация случайной позиции объекта на экране."""
        self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                         randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw_cell(self, position, color):
        """Отрисовывает отдельную клетку на экране."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, представляющий яблочко в игре."""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def draw(self):
        """Отрисовка яблочка на экране."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.body_color = SNAKE_COLOR

    def update_direction(self, next_direction):
        """Обновляет направление движения змейки."""
        if (
            next_direction[0] != -self.direction[0]
            or next_direction[1] != -self.direction[1]
        ):
            self.direction = next_direction

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def move(self):
        """Обновляет позицию змейки."""
        if self.next_direction:
            self.update_direction(self.next_direction)

        cur_x, cur_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head_position = (
            (cur_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (cur_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        # Проверка на столкновение с собственным телом
        if new_head_position in self.positions[1:]:
            return False  # Возвращаем False для завершения игры

        # Затираем последний сегмент, если он есть
        if self.last:
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR,
                         pg.Rect(self.last, (GRID_SIZE, GRID_SIZE)))

        # Вставляем новую позицию головы в начало списка
        self.last = self.positions[-1]
        self.positions.insert(0, new_head_position)

        # Если длина змейки больше текущего размера, удаляем последний сегмент
        if len(self.positions) > self.length:
            self.positions.pop()

        return True  # Возвращаем True, если игра продолжается

    def draw(self):
        """Отрисовывает змейку на экране."""
        for position in self.positions:
            self.draw_cell(position, self.body_color)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            next_direction = TURNS.get(event.key, snake.direction)
            if next_direction != snake.direction:
                snake.next_direction = next_direction


def main():
    """Функция, запускающая игру."""
    pg.init()
    while True:
        apple = Apple()
        snake = Snake()
        score = 0

        while True:
            clock.tick(SPEED)
            handle_keys(snake)
            if not snake.move():
                save_score(snake.length - 1)
                screen.fill(BOARD_BACKGROUND_COLOR)
                display_scores()
                pg.display.update()
                pg.time.wait(3000)  # Показываем рекорды 3 секунды
                break  # Выход из внутреннего цикла, чтобы начать новую игру

            # Проверка на поедание яблока
            if snake.get_head_position() == apple.position:
                snake.length += 1
                apple.randomize_position()
                score += 1

            # Очистка экрана и отрисовка объектов
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.draw()
            snake.draw()
            pg.display.update()


if __name__ == '__main__':
    main()
