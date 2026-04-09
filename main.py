import tkinter as tk
import random
import os
import pygame  # для звука

class SnakeGame:
    # Константы для цветов, размеров и текстов
    COLORS = {
        'bg': 'black',
        'snake_head': 'white',
        'snake_body': '#AAAAAA',
        'food': 'red',
        'food_outline': 'white',
        'text_normal': 'white',
        'text_highlight': 'yellow',
        'game_over_bg': '#330000',
        'button_bg': 'white',
        'button_hover': '#e0e0e0',
        'button_active': 'lightgray',
        'button_active_hover': '#c0c0c0'
    }
    FONTS = {
        'title': ('Arial', 30, 'bold'),
        'score': ('Arial', 12),
        'game_over': ('Arial', 22, 'bold'),
        'menu': ('Arial', 14),
        'timer': ('Arial', 12, 'bold')
    }
    DIFFICULTIES = [('Легко', 150), ('Средне', 100), ('Сложно', 60)]

    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")

        # Инициализация pygame mixer для звука
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()

        self.width = 600
        self.height = 400
        self.seg_size = 20

        self.high_score = self.load_high_score()
        self.running = False
        self.paused = False
        self.game_over_active = False
        self.in_menu = True          # флаг для перерисовки при изменении размера
        self.timer_after_id = None
        self.current_speed = None

        # Для обработки направления: чтобы за один шаг менялось не более одного раза
        self.next_direction = None

        # Сохраняемые данные для экрана завершения
        self.game_over_title = ""
        self.game_over_score = 0
        self.countdown = 5

        self.setup_ui()

    # ========== Звуки ==========
    def load_sounds(self):
        sound_files = {
            'eat': 'eat.wav',
            'game_over': 'game_over.wav',
            'bg_music': 'background_music.mp3'
        }
        for name, file in sound_files.items():
            if os.path.exists(file):
                try:
                    self.sounds[name] = pygame.mixer.Sound(file)
                except:
                    pass
        # фоновая музыка играет в цикле
        if 'bg_music' in self.sounds:
            self.sounds['bg_music'].play(-1)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # ========== Работа с рекордом ==========
    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass

    # ========== UI setup ==========
    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height,
                                bg=self.COLORS['bg'], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Привязываем событие изменения размера холста
        self.canvas.bind("<Configure>", self.on_resize)

        self.root.update()
        self.show_menu()

    def get_center(self):
        return self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2

    # ========== Обработчик изменения размера окна ==========
    def on_resize(self, event):
        # Перерисовываем текущий экран с новым центром
        if self.in_menu:
            self.show_menu()
        elif self.game_over_active:
            self.redraw_game_over()

    # ========== Меню с клавиатурным управлением и мышью ==========
    def show_menu(self):
        self.cancel_timer()
        self.canvas.delete("all")
        self.running = False
        self.game_over_active = False
        self.in_menu = True

        # Отвязываем старые обработчики
        self.root.unbind("<KeyPress>")
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")
        self.root.unbind("<Return>")

        w, h = self.get_center()

        self.canvas.create_text(w, h - 120, text="ЗМЕЙКА",
                                fill=self.COLORS['text_normal'], font=self.FONTS['title'])
        self.canvas.create_text(w, h - 70,
                                text=f"Рекорд: {self.high_score}",
                                fill=self.COLORS['text_highlight'], font=self.FONTS['menu'])

        # Создаем фрейм для кнопок
        self.menu_frame = tk.Frame(self.canvas, bg=self.COLORS['bg'])
        self.canvas.create_window(w, h + 30, window=self.menu_frame)

        self.menu_buttons = []
        self.menu_speeds = []
        for text, speed in self.DIFFICULTIES:
            btn = tk.Button(self.menu_frame, text=text,
                            width=15, bg=self.COLORS['button_bg'],
                            font=self.FONTS['menu'],
                            relief='raised', bd=2)
            # Привязываем события мыши
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_hover(b, enter=True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_hover(b, enter=False))
            btn.bind("<Button-1>", lambda e, s=speed: self.start_game(s))
            btn.pack(pady=5)
            self.menu_buttons.append(btn)
            self.menu_speeds.append(speed)

        # Индекс выбранной кнопки для навигации с клавиатуры
        self.selected_menu_index = 0
        # Кнопки изначально не выделены (все в обычном состоянии)

        # Привязываем клавиши для меню
        self.root.bind("<KeyPress>", self.menu_key_handler)  # для цифр и других клавиш
        self.root.bind("<Up>", self.menu_navigate)
        self.root.bind("<Down>", self.menu_navigate)
        self.root.bind("<Return>", self.menu_select)

    def on_button_hover(self, button, enter):
        """Обработчик наведения мыши на кнопку"""
        index = self.menu_buttons.index(button)
        if enter:
            # При наведении меняем фон в зависимости от того, выделена ли кнопка
            if index == self.selected_menu_index:
                button.config(bg=self.COLORS['button_active_hover'])
            else:
                button.config(bg=self.COLORS['button_hover'])
        else:
            # При уходе мыши возвращаем фон, соответствующий состоянию выделения
            if index == self.selected_menu_index:
                button.config(bg=self.COLORS['button_active'], relief='sunken')
            else:
                button.config(bg=self.COLORS['button_bg'], relief='raised')

    def highlight_button(self, index):
        """Выделяет кнопку с заданным индексом, снимает выделение с предыдущей"""
        # Снимаем выделение с предыдущей активной кнопки
        if hasattr(self, 'selected_menu_index'):
            prev = self.selected_menu_index
            if 0 <= prev < len(self.menu_buttons):
                self.menu_buttons[prev].config(bg=self.COLORS['button_bg'], relief='raised')
        # Выделяем новую
        self.selected_menu_index = index
        self.menu_buttons[index].config(bg=self.COLORS['button_active'], relief='sunken')

    def menu_key_handler(self, event):
        # Обработка цифр 1,2,3 в меню: только выделяем соответствующую кнопку
        if event.char in ('1', '2', '3'):
            idx = int(event.char) - 1
            if 0 <= idx < len(self.menu_buttons):
                self.highlight_button(idx)
        # Остальные клавиши (например, стрелки) обрабатываются отдельно

    def menu_navigate(self, event):
        if not hasattr(self, 'menu_buttons'):
            return
        if event.keysym == "Up":
            new_idx = (self.selected_menu_index - 1) % len(self.menu_buttons)
        elif event.keysym == "Down":
            new_idx = (self.selected_menu_index + 1) % len(self.menu_buttons)
        else:
            return
        self.highlight_button(new_idx)

    def menu_select(self, event):
        # Запуск игры с выбранной сложностью по Enter
        if hasattr(self, 'menu_buttons') and self.menu_speeds:
            speed = self.menu_speeds[self.selected_menu_index]
            self.start_game(speed)

    # ========== Запуск игры ==========
    def start_game(self, speed):
        self.cancel_timer()
        # Отвязываем все обработчики клавиш
        self.root.unbind("<KeyPress>")
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")
        self.root.unbind("<Return>")

        if hasattr(self, 'menu_frame'):
            self.menu_frame.destroy()

        self.current_speed = speed
        self.speed = speed
        self.score = 0
        self.running = True
        self.paused = False
        self.game_over_active = False
        self.in_menu = False
        self.direction = "Right"
        self.next_direction = None  # сброс следующего направления

        w, h = self.get_center()
        max_x = (self.canvas.winfo_width() - self.seg_size) // self.seg_size
        max_y = (self.canvas.winfo_height() - self.seg_size) // self.seg_size
        start_x = min(max(2, (int(w) // self.seg_size)), max_x - 2) * self.seg_size
        start_y = min(max(2, (int(h) // self.seg_size)), max_y - 2) * self.seg_size

        self.snake = [(start_x, start_y),
                      (start_x - self.seg_size, start_y),
                      (start_x - 2*self.seg_size, start_y)]

        self.food = self.create_food()
        if self.food is None:
            self.victory()
            return

        self.root.bind("<KeyPress>", self.handle_keys)
        self.update()

    # ========== Создание еды с проверкой свободного места ==========
    def create_food(self):
        max_x = (self.canvas.winfo_width() - self.seg_size) // self.seg_size
        max_y = (self.canvas.winfo_height() - self.seg_size) // self.seg_size
        total_cells = (max_x + 1) * (max_y + 1)

        if len(self.snake) >= total_cells:
            self.victory()
            return None

        attempts = 0
        while attempts < 1000:
            x = random.randint(0, max_x) * self.seg_size
            y = random.randint(0, max_y) * self.seg_size
            if (x, y) not in self.snake:
                return (x, y)
            attempts += 1

        self.victory()
        return None

    # ========== Управление ==========
    def handle_keys(self, event):
        key = event.keysym
        char = event.char

        # Пауза по пробелу (должна работать всегда)
        if key in ('space', 'p', 'P'):
            self.toggle_pause()
            return

        # Быстрый запуск уровней по цифрам 1,2,3 (в игре) - перезапуск с новой сложностью
        if char in ('1', '2', '3'):
            speed_map = {'1': 150, '2': 100, '3': 60}
            self.start_game(speed_map[char])
            return

        # Если игра на паузе или не запущена, остальные клавиши игнорируем
        if not self.running or self.paused:
            return

        # Карта клавиш в направления (стрелки + WASD + русские буквы)
        key_to_dir = {
            # стрелки
            'Up': 'Up', 'Down': 'Down', 'Left': 'Left', 'Right': 'Right',
            # WASD (латиница)
            'w': 'Up', 'W': 'Up',
            's': 'Down', 'S': 'Down',
            'a': 'Left', 'A': 'Left',
            'd': 'Right', 'D': 'Right',
            # русские буквы (как символы)
            'ц': 'Up', 'Ц': 'Up',
            'ф': 'Left', 'Ф': 'Left',
            'ы': 'Down', 'Ы': 'Down',
            'в': 'Right', 'В': 'Right',
        }
        # Дополнительные имена keysym для русских букв (если раскладка русская и keysym не латиница)
        cyrillic_keysym = {
            'Cyrillic_ts': 'Up',    # ц
            'Cyrillic_ef': 'Left',  # ф
            'Cyrillic_yery': 'Down',# ы
            'Cyrillic_ve': 'Right'  # в
        }

        new_dir = None
        if key in key_to_dir:
            new_dir = key_to_dir[key]
        elif key in cyrillic_keysym:
            new_dir = cyrillic_keysym[key]
        elif char in key_to_dir:
            new_dir = key_to_dir[char]

        if new_dir:
            opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
            if new_dir != opposite.get(self.direction):
                self.next_direction = new_dir

    def toggle_pause(self):
        if self.running:
            self.paused = not self.paused
            self.draw()  # обновим экран, чтобы убрать/показать надпись

    # ========== Логика движения ==========
    def move_snake(self):
        # Применяем накопленное направление (если есть)
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

        head_x, head_y = self.snake[0]

        if self.direction == "Up":
            head_y -= self.seg_size
        elif self.direction == "Down":
            head_y += self.seg_size
        elif self.direction == "Left":
            head_x -= self.seg_size
        elif self.direction == "Right":
            head_x += self.seg_size

        new_head = (head_x, head_y)

        # Проверка столкновения с границами
        if (head_x < 0 or head_x >= self.canvas.winfo_width() or
            head_y < 0 or head_y >= self.canvas.winfo_height()):
            self.game_over()
            return

        # Проверка столкновения с самой собой
        if new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.play_sound('eat')
            self.food = self.create_food()
            if self.food is None:
                return
        else:
            self.snake.pop()

    # ========== Игровой цикл ==========
    def update(self):
        if self.running:
            if not self.paused:
                self.move_snake()
                if self.running:
                    self.draw()
            else:
                self.draw()

        if self.running:
            self.root.after(self.speed, self.update)

    # ========== Отрисовка ==========
    def draw(self):
        self.canvas.delete("all")

        # Еда (яблочко)
        x, y = self.food
        # Рисуем красный круг
        self.canvas.create_oval(x+2, y+2, x+self.seg_size-2, y+self.seg_size-2,
                                fill=self.COLORS['food'], outline='darkred', width=2)
        # Листик
        self.canvas.create_line(x+self.seg_size-6, y+2, x+self.seg_size-2, y-2, fill='green', width=2)

        # Змейка
        for i, (sx, sy) in enumerate(self.snake):
            if i == 0:  # голова с глазками
                # Основной квадрат (скругленный)
                self.canvas.create_rectangle(sx+1, sy+1, sx+self.seg_size-1, sy+self.seg_size-1,
                                             fill=self.COLORS['snake_head'], outline='gray', width=2)
                # Глазки
                eye_offset = 5
                if self.direction in ('Right', 'Left'):
                    # горизонтальное направление
                    eye1 = (sx + eye_offset, sy + eye_offset)
                    eye2 = (sx + eye_offset, sy + self.seg_size - eye_offset)
                else:  # вертикальное
                    eye1 = (sx + eye_offset, sy + eye_offset)
                    eye2 = (sx + self.seg_size - eye_offset, sy + eye_offset)
                self.canvas.create_oval(eye1[0]-2, eye1[1]-2, eye1[0]+2, eye1[1]+2, fill='black')
                self.canvas.create_oval(eye2[0]-2, eye2[1]-2, eye2[0]+2, eye2[1]+2, fill='black')
            else:
                # Тело (скругленные квадраты)
                self.canvas.create_rectangle(sx+2, sy+2, sx+self.seg_size-2, sy+self.seg_size-2,
                                             fill=self.COLORS['snake_body'], outline='gray', width=1)

        # Счёт
        self.canvas.create_text(50, 20, text=f"Счет: {self.score}",
                                fill=self.COLORS['text_normal'], font=self.FONTS['score'])

        # Индикатор паузы
        if self.paused:
            w, h = self.get_center()
            self.canvas.create_text(w, h, text="ПАУЗА",
                                    fill=self.COLORS['text_highlight'], font=self.FONTS['title'])

    # ========== Завершение игры ==========
    def game_over(self):
        if not self.running:
            return
        self.running = False
        self.game_over_active = True
        self.in_menu = False
        self.play_sound('game_over')

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

        self.game_over_title = "ИГРА ОКОНЧЕНА"
        self.game_over_score = self.score
        self.countdown = 5
        self.show_game_over_screen()

    def victory(self):
        if not self.running:
            return
        self.running = False
        self.game_over_active = True
        self.in_menu = False
        self.play_sound('game_over')  # можно отдельный звук победы

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

        self.game_over_title = "ПОБЕДА!"
        self.game_over_score = self.score
        self.countdown = 5
        self.show_game_over_screen()

    # ========== Экран завершения ==========
    def show_game_over_screen(self):
        self.canvas.delete("all")
        w, h = self.get_center()

        # Подложка
        self.canvas.create_rectangle(w-200, h-110, w+200, h+110,
                                      fill=self.COLORS['game_over_bg'],
                                      outline=self.COLORS['text_normal'], width=2)

        # Заголовок
        self.canvas.create_text(w, h - 40, text=self.game_over_title,
                                fill=self.COLORS['text_normal'], font=self.FONTS['game_over'])
        # Счёт
        self.canvas.create_text(w, h + 10, text=f"Ваш счет: {self.game_over_score}",
                                fill=self.COLORS['text_normal'], font=self.FONTS['menu'])

        # Рамка для кнопок
        button_frame = tk.Frame(self.canvas, bg=self.COLORS['game_over_bg'])
        self.canvas.create_window(w, h + 70, window=button_frame)

        # Кнопка "Заново"
        restart_btn = tk.Button(button_frame, text="Заново",
                                command=self.restart_game,
                                width=10, bg=self.COLORS['button_bg'])
        restart_btn.pack(side='left', padx=5)

        # Кнопка "Меню"
        menu_btn = tk.Button(button_frame, text="Меню",
                             command=self.show_menu,
                             width=10, bg=self.COLORS['button_bg'])
        menu_btn.pack(side='left', padx=5)

        # Таймер (сдвинут ниже, чтобы не наезжать на кнопки)
        self.timer_text_id = self.canvas.create_text(w, h + 140,
                                                     text=f"Возврат в меню через: {self.countdown}",
                                                     fill=self.COLORS['text_highlight'],
                                                     font=self.FONTS['timer'])

        self.tick_timer()

    def redraw_game_over(self):
        """Перерисовывает экран завершения при изменении размера окна"""
        self.cancel_timer()
        self.show_game_over_screen()

    def restart_game(self):
        if self.current_speed is not None:
            self.cancel_timer()
            self.start_game(self.current_speed)

    # ========== Таймер возврата в меню ==========
    def tick_timer(self):
        if self.countdown > 1:
            self.countdown -= 1
            self.canvas.itemconfig(self.timer_text_id,
                                   text=f"Возврат в меню через: {self.countdown}")
            self.timer_after_id = self.root.after(1000, self.tick_timer)
        else:
            self.show_menu()

    def cancel_timer(self):
        if self.timer_after_id:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    game = SnakeGame(root)
    root.mainloop()