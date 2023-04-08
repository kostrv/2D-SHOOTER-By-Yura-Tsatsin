from pygame import *
from random import uniform, randint
'''импортируем функцию для засекания времени, чтобы интерпретатор
 не искал эту функцию в pygame модуле time, даем ей другое название сами 
 '''
 
 
import time as timer
delayer = time.Clock()
# подгружаем отдельно функции для работы со шрифтом
font.init()
font_titles = font.SysFont('Corbel', 80)
font_subtitles = font.SysFont('Corbel', 35, True) # третий параметр True означает что шрифт будет жирным, четвертый - курсив
win = font_titles.render('Ты выиграл!', True, (255, 255, 255))
lose = font_titles.render('Ты проиграл!', True, (180, 0, 0))
pause_text = font_titles.render('Пауза', True, (255, 255, 255))
lose_boss = font_titles.render('ХА-ХА! Пропустил босса!', True, (180, 0, 0))
restart = font_subtitles.render('R - перезапуск', True, (255, 255, 255))  # сообщение о рестарте
start = font.SysFont('Corbel', 50).render('Нажми цифру чтобы начать', True, (255, 255, 255))  # сообщение о старте
start_diff = font_subtitles.render('1 - Легко, 2 - Норм, 3 - Капец', True, (0, 255, 255))  # выбор сложности
font2 = font.SysFont('Tahoma', 30)
# фоновая музыка
mixer.init()
#lol kek cheburek
mixer.music.load('sounds/space.ogg') # заменил на Daft Punk - Castor
#mixer.music.set_volume(0.4) # громкость музыки 40%
fire_sound = mixer.Sound('sounds/fire.ogg')
reload_sound = mixer.Sound('sounds/reload.ogg')
reload_sound.set_volume(0.5)
select_sound = mixer.Sound('sounds/select_diff.ogg')
boss_sound = mixer.Sound('sounds/boss.ogg')
game_over_sound = mixer.Sound('sounds/game_over.ogg')
destroy_sound = mixer.Sound('sounds/destroy.ogg')
heal = mixer.Sound('sounds/heal.ogg')
collide = mixer.Sound('sounds/collide.ogg')
collide.set_volume(0.5)

# нам нужны такие картинки:
img_back = "images/galaxy.png"  # фон игры
img_bullet = "images/bullet.png"  # пуля
img_hero = "images/rocket.png"  # герой
img_enemy = "images/ufo.png"  # враг
img_ast = "images/asteroid.png"  # астероид
img_boss = "images/boss.png"  # босс
img_healthpack = "images/healthpack.png"  # аптечка

''' Да-да, всё равно нулю так как после выбора сложности подставим туда значения '''
score = 0  # сбито кораблей
lost = 0  # пропущено кораблей
life = 0  # текущие жизни
boss_counter = 0 # счетчик убитых боссов
boss_comming = 0 # через сколько придет следующий босс
num_fire = 0  # переменная для подсчта выстрела

class Difficult():
    """Класс отвечает за сложность в игре. 
    Кстати, данная подсказка будет показываться 
    каждый раз при объявлении класса. Попробуй
    навести указатель на имя класса в любом 
    месте программы."""
    def __init__(self, goal=50, max_lost=10, max_life=5, max_enemies=5, reload_time=1, boss_comming_at=20):
        self.goal = goal # столько кораблей нужно сбить для победы
        self.max_lost = max_lost # проиграли, если пропустили столько
        self.max_life = max_life # нужно для рестарта, тут храним максимальное количество жизней
        self.max_enemies = max_enemies # максимальное количество врагов
        self.reload_time = reload_time # время перезарядки
        self.boss_comming_at = boss_comming_at # храним через сколько набранных очков придёт босс
# класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
 # конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # Вызываем конструктор класса (Sprite):
        sprite.Sprite.__init__(self)
        # каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        # каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    # метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# класс главного игрока
class Player(GameSprite):
    # метод для управления спрайтом стрелками клавиатуры
    def update(self):
        global is_busy
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    # метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 10, 30, -15)
        bullets.add(bullet)

# класс спрайта-врага
class Enemy(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        global lost
        # исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Boss(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, lifes_count):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y, 1)
        self.lifes = lifes_count # у босса новое поле для количества жизней
    def update(self):
        global finish
        self.rect.y += self.speed
        if self.rect.y > win_height:
            mixer.music.stop() # останавливаем музыку
            collide.play()
            finish = True
            window.blit(background, (0, 0))
            make_frame() # отрисовываем фон и счетчики размещая их по центру
            window.blit(lose_boss, (win_width / 2 - lose_boss.get_width() / 2, 200))
            window.blit(restart, (win_width / 2 - restart.get_width() / 2, 300))

class Healthpack(GameSprite):
    # функция старта отсчета до появления аптечки
    def start(self):
        global past_time
        self.rect.y = -60
        self.canMove = False
        self.startTime = past_time # запоминаем время когда начался отчет
    # функция начала падения аптечки
    def create(self):
        self.rect.x = randint(80, win_width - 80)
        self.rect.y = 0
        self.canMove = True
    # функция вызывается когда мы ловим или упускаем аптечку
    def hasTaked(self):
        self.rect.y = -60
        self.canMove = False
    # движение
    def update(self):
        ''' 
            Проверка времени ведется всегда,
            аптечка появляется каждые 30 секунд 
            после того как её поймают
            или упустият. Если ловим, то +1 жизнь.
        '''
        global life, past_time
        if past_time - self.startTime >= 30:
            self.create()
            self.startTime = past_time
        if self.canMove:
            if sprite.collide_rect(ship, health):
                life += 1
                heal.play()
                self.hasTaked()
            if self.rect.y < 0:
                self.hasTaked()
            self.rect.y += self.speed

# класс спрайта-пули
class Bullet(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        # исчезает, если дойдет до края экрана
        if self.rect.y < 0:
            self.kill()

# Создаем окошко
# window = display.set_mode((0, 0), FULLSCREEN) # можно установить полноэкранный режим
window = display.set_mode((800, 500))           # и тогда эту строку нужно закомментировать
display.set_caption("SuperMegaShooter2070Pro")
win_width = display.Info().current_w  # получаем ширину окна
win_height = display.Info().current_h  # получаем высоту окна
background = transform.scale(image.load(img_back), (win_width, win_height))
''' Можно так же адаптировать размеры спрайтов, чтобы была зависимость размера спрайта от размера экрана '''
# создаем спрайты
ship = Player(img_hero, 5, win_height - 60, 80, 55, 10)
boss = Boss(img_boss, randint(80, win_width - 80), -40, 80, 81, 10)
health = Healthpack(img_healthpack, randint(80, win_width - 80), -50, 50, 50, 7)
difficult = None
monsters = sprite.Group()
asteroids = sprite.Group()
bullets = sprite.Group()

finish = False # переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
run = True  # флаг сбрасывается кнопкой закрытия окна
rel_time = False  # флаг отвечающий за перезарядку
first_start = True # переменная чтобы игра не начиналась после запуска
pause = False # переменная котороя отвечает за паузу
boss_time = False # переменная которая определяет появится босс или нет
show_hud = True # переменная которая отвечает за отображение худа

def make_ememies():
    ''' функция uniform из модуля рандом даёт нам возможность получать рандомное число, 
    но не целое, а с плавающей запятой(float). Таким образом, скорость в меньшем диапазоне
    будет наиболее разнообразней чем с целыми числами.
    '''
    for i in range(difficult.max_enemies):
        monsters.add(Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, uniform(1.5, 3.0)))
    for i in range(3):
        asteroids.add(Enemy(img_ast, randint(30, win_width - 30), randint(-40, 30), 80, 50, uniform(1.0, 2.0)))
''' 
    Зачем выность в отдельную функцию отрисовку фона и счетчиков?
    - Потому что эта часть будет повторяться три раза в ходе программы.
    1. В ходе игры. 2. При проигрыше. 3. При выигрыше.  
    
    Зачем делать это при выигрыше и проигрыше?
    - Для того чтобы счетчики корректно отображались и не врали.  
'''
def make_frame():
    if show_hud or finish: # отрисовка худа будет производиться принудительно при конце игры
        window.blit(font2.render("Счет: " + str(score) + "/" + str(difficult.goal), 1, (255, 255, 255)), (10, 20))
        window.blit(font2.render("Пропущено: " + str(lost) + "/" + str(difficult.max_lost), 1, (255, 255, 255)), (10, 50))
        window.blit(font2.render("Боссов: " + str(boss_counter), 1, (255, 255, 255)), (10, 80))

top_score = 0
try:
    with open("top.score", "r") as file:
        top_score = int(file.read()) # читаем прошлый рекорд из файла
except Exception as ex:
    top_score = 0
top_start = font_subtitles.render('Твой прошлый рекорд: ' + str(top_score), True, (0, 150, 150)) 

'''
    Функция нужна чтобы записывать в файл рекордное значение очков.
    Записыватся только если текущие очки больше записанных.
'''
def record_top():
    global top_score, score
    if score > top_score:
        top_text = font_subtitles.render("Новый рекорд: " + str(score), 1, (0, 200, 10))
        window.blit(top_text, (win_width / 2 - top_text.get_width() / 2, 350))
        top_score = score
        with open("top.score", "w") as file:
            file.write(str(top_score))
    else:
        top_text = font_subtitles.render("Твой рекорд: " + str(top_score), 1, (0, 150, 50))
        window.blit(top_text, (win_width / 2 - top_text.get_width() / 2, 350))

''' 
    Так как функция timer.time() используется в нескольких участках программы,
    то есть вероятность что она будет вызвана одновременно двумя функциями, а
    это неминуемо приведет к ошибке, так как игра однопоточная, поэтому мы её
    будем вызывать только при старте программы и на каждой итерации цикла игры,
    только когда игра в процессе, т.е. когда ставим на паузу или проигрываем
    функция не будет вызываться. Записывать время будет в переменную past_time.
'''
past_time = timer.time() 

''' 
    Чтобы отобразить надпись ровно по центру нужно знать ширину и высоту окна,
    а так же ширину и высоту спрайта, в данном случае текстового. Формула ниже
'''
window.blit(start, (win_width / 2 - start.get_width() / 2 , win_height / 2 - start.get_height() / 2))
window.blit(start_diff, (win_width / 2 - start_diff.get_width() / 2 , win_height / 2 - start_diff.get_height() / 2 + 50))
if top_score > 0: # зачем выводить рекордные очки если они равны нулю?
    window.blit(top_start, (win_width / 2 - top_start.get_width() / 2 , win_height / 2 - top_start.get_height() / 2 + 100))
display.update()

# Основной цикл игры:
while run:
    # событие нажатия на кнопку Закрыть
    for e in event.get():
        if e.type == QUIT:
            run = False
        # событие нажатия на пробел - спрайт стреляет
        elif e.type == KEYDOWN:
            # событие нажатия на escape - пауза (вкл/выкл)
            if e.key == K_ESCAPE:
                if pause and not first_start and not finish:
                    pause = False
                    mixer.music.unpause()
                elif not pause and not first_start and not finish:
                    pause = True
                    mixer.music.pause()
                    window.blit(pause_text, (win_width / 2 - pause_text.get_width() / 2 , win_height / 2 - pause_text.get_height() / 2))
                    display.update()
            elif e.key == K_q: # выход из игры по нажатию Q
                run = False
            # событие нажатия на пробел - спрайт стреляет
            elif e.key == K_SPACE and not finish and not pause:
                # проверяем сколько выстеров сделано и не происходит ли перезарядка
                if num_fire < 5 and rel_time == False:
                    num_fire = num_fire + 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >= 5 and rel_time == False:  # если игрок сделал 5 выстрелов
                    reload_sound.play()
                    last_time = past_time  # засекаем время, когда это произошло
                    rel_time = True  # ставив флаг перезарядки
            # легкий уровень сложности
            elif e.key == K_1 and first_start:
                difficult = Difficult() # стандартные значения соответсвуют легкой сложности
                life = difficult.max_life
                boss_comming = difficult.boss_comming_at
                select_sound.play()
                mixer.music.play() # воспроизводим музыку только при начале игры
                first_start = False
                make_ememies()
                health.start()
            # средний уровень сложности
            elif e.key == K_2 and first_start:
                difficult = Difficult(125, 7, 4, 7, 2, 15)
                life = difficult.max_life
                boss_comming = difficult.boss_comming_at
                select_sound.play()
                mixer.music.play() # воспроизводим музыку только при начале игры
                first_start = False
                make_ememies()
                health.start()
            # сложный уровень сложности
            elif e.key == K_3 and first_start:
                difficult = Difficult(300, 5, 3, 10, 3, 10)
                life = difficult.max_life
                boss_comming = difficult.boss_comming_at
                select_sound.play()
                mixer.music.play() # воспроизводим музыку только при начале игры
                first_start = False
                make_ememies()
                health.start()
            # рестарт - клавиша R, сработает только если игра закончена
            elif e.key == K_r and finish:  
                # обнуляемся
                score = 0
                lost = 0
                life = difficult.max_life
                boss_counter = 0
                num_fire = 0
                boss_comming = difficult.boss_comming_at
                for monster in monsters:
                    monster.kill() # убираем всех врагов
                for asteroid in asteroids:
                    asteroid.kill() # убиваем все астероиды
                make_ememies()
                for bullet in bullets:
                    ''' удаляем все пули которые на сцене, если этого
                        не сделать они продолжат лететь после рестарта '''
                    bullet.kill()
                if boss_time:
                    boss.kill()
                    boss_time = False
                finish = False
                health.start()
                mixer.music.play() # воспроизводим музыку только при начале игры
            elif e.key == K_h and not first_start and not finish and not pause:
                show_hud = not show_hud # переворачиваем значение худа
    if not first_start:
        if not pause:
            # сама игра: действия спрайтов, проверка правил игры, перерисовка
            if not finish:
                past_time = timer.time()
                # отрисовываем фон
                window.blit(background, (0, 0))

                # производим движения спрайтов
                ship.update()
                monsters.update()
                asteroids.update()
                bullets.update()
                health.update()
                # обновляем их в новом местоположении при каждой итерации цикла
                ship.reset()
                monsters.draw(window)
                asteroids.draw(window)
                bullets.draw(window)
                health.reset()
                # отрисовываем  счетчики
                make_frame() 

                # проверяем, если сейчас босс должен быть на сцене
                if boss_time:
                    cols = sprite.spritecollide(boss, bullets, True) # собираем касания с пулями
                    for col in cols:
                        boss.lifes -= 1 # отнимаем боссу жизни
                    if show_hud:
                        window.blit(font2.render("BOSS: " + str(boss.lifes), 1, (255, 0, 0)), (10, 140)) # обновляем счетчик
                    boss.update()
                    boss.reset()
                    if boss.lifes <= 0: # если у босса кончились жизни
                        boss_time = False 
                        score += 5 
                        boss_comming = score + difficult.boss_comming_at # следующий босс появится через "текущие очки" + "через сколько должен появится босс"
                        boss_counter += 1 # счетчик поверженных боссов +1
                        boss.kill() # совсем убиваем его со сцены
                if not boss_time and boss_comming - score <= 0: # если не время босса и "когда должен прийти босс" - "текущие очки" меньше или равно нулю, то пришло время выпускать босса
                    boss_time = True
                    boss = Boss(img_boss, randint(80, win_width - 80), -40, 80, 81, 5) # параметра скорости нет, скорость у боссов - 1
                    boss_sound.play() # звук появления босса
                
                # проверка столкновения пули и монстров (и монстр, и пуля при касании исчезают)
                collides = sprite.groupcollide(monsters, bullets, True, True)
                for c in collides:
                    # этот цикл повторится столько раз, сколько монстров подбито
                    score += 1
                    destroy_sound.play()
                    monsters.add(Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, uniform(1.5, 3.0)))
                
                # если спрайт коснулся врага уменьшает жизнь
                if sprite.spritecollide(ship, monsters, False):
                    sprite.spritecollide(ship, monsters, True)
                    monsters.add(Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, uniform(1.5, 3.0)))
                    life -= 1
                    collide.play()
                if sprite.spritecollide(ship, asteroids, False):
                    sprite.spritecollide(ship, asteroids, True)
                    asteroids.add(Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, uniform(1.0, 2.0)))
                    life -= 1
                    collide.play()

                # проигрыш
                if life == 0 or lost >= difficult.max_lost or ship.rect.colliderect(boss): # касание босса - это тоже проигрыш
                    # проиграли, ставим фон и больше не управляем спрайтами.
                    mixer.music.stop() # останавливаем музыку
                    finish = True
                    window.blit(background, (0, 0))
                    make_frame() # отрисовываем фон и счетчики размещая их по центру
                    window.blit(lose, (win_width / 2 - lose.get_width() / 2, 200))
                    window.blit(restart, (win_width / 2 - restart.get_width() / 2, 300))
                    game_over_sound.play()
                    record_top()

                ''' закомментируй если хочешь бесконечную игру '''
                # проверка выигрыша: сколько очков набрали?
                if score >= difficult.goal:
                    mixer.music.stop() # останавливаем музыку
                    finish = True
                    window.blit(background, (0, 0))
                    make_frame() # отрисовываем фон и счетчики
                    window.blit(win, (win_width / 2 - win.get_width() / 2, 200))
                    window.blit(restart, (win_width / 2 - restart.get_width() / 2, 300))
                    record_top()
                ''' закомментируй если хочешь бесконечную игру '''

                # перезарядка
                if rel_time == True:
                    now_time = past_time  # считываем время
                    if now_time - last_time < difficult.reload_time:  # пока не прошло reload_time выводим информацию о перезарядке
                        if show_hud:
                            window.blit(font2.render("Патроны: заряжаем", 1, (255, 0, 0)), (10, 110))
                    else:
                        num_fire = 0   # обнуляем счетчик пуль
                        rel_time = False  # сбрасываем флаг перезарядки
                else:
                    if show_hud:
                        window.blit(font2.render("Патроны: " + str(5 - num_fire), 1, (255, 255, 255)), (10, 110))

                if show_hud:
                    # задаем разный цвет в зависимости от кол-ва жизней
                    if life >= difficult.max_life or life > 2:
                        life_color = (0, 150, 0)
                    elif life == 2:
                        life_color = (150, 150, 0)
                    else:
                        life_color = (150, 0, 0)

                    text_life = font2.render("♥ " + str(life), 1, life_color)
                    window.blit(text_life, (730, 10))

                display.update()
            delayer.tick(30)