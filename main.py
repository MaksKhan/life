import pygame as pg
from math import floor
import sys

# цвета
b = (0, 0, 0)
g = (128, 128, 128)
p = (102, 0, 255)
# ширина, высота
width, height = 1280, 960
# остальное
size = 10
speed = 100
lifes = 0


# полотно, поле, на котором все происходит
class Canvas:
    def __init__(self):
        pg.init()
        self.event = pg.USEREVENT
        self.screen = pg.display.set_mode((width, height))
        pg.time.set_timer(self.event, speed)

        # ширина, высота, цвет и спрайты поля
        self.fieldWidth = floor(width / size)
        self.fieldHeight = floor(height / size)
        self.stop = True
        self.speed = speed
        self.colour = (128, 128, 128)
        self.sprites = pg.sprite.Group()

        # массив для клеток на поле
        self.tiles = [[] for _ in range(self.fieldWidth)]
        for x in range(self.fieldWidth):
            for y in range(self.fieldHeight):
                self.tiles[x].append(Tile(self, x, y))

        # переменные для обработки нажатий
        self.previous_click = 0
        self.previous_x = 0
        self.previous_y = 0

    # рендер событий и отображение меню
    def play(self):
        while True:
            self.events()
            self.sprites.draw(self.screen)
            self.events()
            self.sprites.draw(self.screen)
            self.screen.blit(pg.font.SysFont('courier new', 20).render(f'Количество жизней: {lifes}', False, p),
                             (20, 0))
            self.screen.blit(pg.font.SysFont('courier new', 20).render(f'Скорость{1000 / speed}', False, p), (20, 15))
            pg.display.flip()
            pg.display.flip()

    # создание мира заново, при рестарте или изменении масштаба
    def new(self):
        self.fieldWidth = floor(width / size)
        self.fieldHeight = floor(height / size)
        self.stop = True
        self.speed = speed
        self.colour = (128, 128, 128)
        self.sprites = pg.sprite.Group()
        self.tiles = [[] for _ in range(self.fieldWidth)]
        for x in range(self.fieldWidth):
            for y in range(self.fieldHeight):
                self.tiles[x].append(Tile(self, x, y))
        self.previous_click = 0
        self.previous_x = 0
        self.previous_y = 0
        return None

    # рассчет следующего хода (поколения)
    def nextMove(self):
        temp = [[] for _ in range(self.fieldWidth)]
        global lifes
        lifes = 0
        for x in range(self.fieldWidth):
            for y in range(self.fieldHeight):

                # рассчет соседей, выжевет организим или умрет
                k = sum([self.tiles[x - 1][y].alive, self.tiles[x][y - 1].alive,
                         self.tiles[x - 1][(y + 1) % self.fieldHeight].alive,
                         self.tiles[x - 1][y - 1].alive,
                         self.tiles[x][(y + 1) % self.fieldHeight].alive,
                         self.tiles[(x + 1) % self.fieldWidth][(y + 1) % self.fieldHeight].alive,
                         self.tiles[(x + 1) % self.fieldWidth][y - 1].alive,
                         self.tiles[(x + 1) % self.fieldWidth][y].alive])

                if not self.tiles[x][y].alive:
                    if k == 3:
                        temp[x].append(True)
                    elif k == -1:
                        pass
                    else:
                        temp[x].append(False)
                elif self.tiles[x][y].alive:  # если живая добавляет в счетчик
                    lifes += 1
                if self.tiles[x][y].alive and (k <= 1 or k >= 4):  # умирает
                    temp[x].append(False)
                elif self.tiles[x][y].alive:  # остается жить или новая жизнь
                    temp[x].append(True)
        for x in range(self.fieldWidth):
            for y in range(self.fieldHeight):
                if temp[x][y]:
                    if not self.tiles[x][y].alive:  # вызывает функцию новой жизни
                        self.tiles[x][y].newLive()
                else:
                    if self.tiles[x][y].alive:  # вызывает функцию новой жизни
                        self.tiles[x][y].death()

        return None

    # обработка пользовательского ввода
    def events(self):
        for event in pg.event.get():
            global size
            click = pg.mouse.get_pressed()

            # обработка скроллов мыши
            if event.type == pg.MOUSEBUTTONDOWN:
                global speed
                if event.button == 4 and speed < 300:  # чтобы не было слишком медленно
                    speed += 5
                    pg.time.set_timer(self.event, speed)
                elif event.button == 5 and speed > 40:  # чтобы не стало слишком быстрой
                    speed -= 5
                    pg.time.set_timer(self.event, speed)

            # обработка кликов мыши, постановка клетки
            x, y = pg.mouse.get_pos()
            x = floor(x / size)
            y = floor(y / size)

            if (click, x, y) != (self.previous_click, self.previous_x, self.previous_y):  # чтобы можно было проводить
                if click[0]:  # 0 - это лкм, добавляет
                    self.tiles[x][y].newLive()
                elif click[2] and self.tiles[x][y].alive:  # 2 - это пкм, стирает
                    self.tiles[x][y].death()
            self.previous_click, self.previous_x, self.previous_y = click, x, y  # чтобы не было путаницы, не удалялось сразу

            if not self.stop and event.type == self.event:  # начало новой
                self.nextMove()

            # обработка с клавиатуры
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:  # пауза
                    self.stop = not (self.stop)
                elif event.key == pg.K_r:  # рестарт
                    self.new()
                elif event.key == pg.K_w and size < 30:  # масштаб увеличить
                    size += 5
                    self.new()
                elif event.key == pg.K_s:  # масштаб уменьшить
                    if size > 5:
                        size -= 5
                    self.new()
            else:
                pass
            if event.type == pg.QUIT:  # при закрытии, чтобы без ошибок
                pg.quit()
                sys.exit()


# класс, представляющий клетку
class Tile(pg.sprite.Sprite):
    def __init__(self, field, x, y):
        self.groups = field.sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((size, size))  # изображение
        self.rect = self.image.get_rect()  # создание клетки
        self.rect.x, self.rect.y = x * size, y * size
        self.death()

    def newLive(self, colour=b):  # создает живой организм
        self.alive = True
        self.colour = colour
        self.image.fill(colour)
        return None

    def death(self):  # помер
        self.alive = False
        self.image.fill(g)
        return None


# старт игры
c = Canvas()
c.new()
c.play()
