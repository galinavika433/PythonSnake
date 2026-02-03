import tkinter as tk
import random

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game - Gemini AI")

        # Начальные размеры
        self.width = 600
        self.height = 400
        self.seg_size = 20

        self.high_score = 0
        self.running = False

        self.setup_ui()

    def setup_ui(self):
        # Настройка холста (растягивается по окну)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, 
                                bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.root.update()
        self.show_menu()

    def get_center(self):
        """Возвращает текущий центр холста для позиционирования текста"""
        return self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2

    def show_menu(self):
        self.canvas.delete("all")
        self.running = False

        w, h = self.get_center()

        self.canvas.create_text(w, h - 120, text="ЗМЕЙКА", fill="white", font=("Arial", 30, "bold"))
        self.canvas.create_text(w, h - 70, text=f"Рекорд: {self.high_score}", fill="yellow", font=("Arial", 14))

        self.menu_frame = tk.Frame(self.canvas, bg="black")
        self.canvas.create_window(w, h + 30, window=self.menu_frame)

        difficulties = [("Легко", 150), ("Средне", 100), ("Сложно", 60)]
        for text, speed in difficulties:
            btn = tk.Button(self.menu_frame, text=text, command=lambda s=speed: self.start_game(s), 
                            width=15, bg="white", font=("Arial", 12))
            btn.pack(pady=5)

    def start_game(self, speed):
        if hasattr(self, 'menu_frame'):
            self.menu_frame.destroy()

        self.speed = speed
        self.score = 0
        self.running = True
        self.direction = "Right"

        w, h = self.get_center()
        start_x = (w // self.seg_size) * self.seg_size
        start_y = (h // self.seg_size) * self.seg_size

        self.snake = [(start_x, start_y), (start_x - self.seg_size, start_y), (start_x - 2*self.seg_size, start_y)]
        self.food = self.create_food()

        self.root.bind("<KeyPress>", self.handle_keys)
        self.update()

    def create_food(self):
        max_x = (self.canvas.winfo_width() - self.seg_size) // self.seg_size
        max_y = (self.canvas.winfo_height() - self.seg_size) // self.seg_size

        while True:
            x = random.randint(0, max_x) * self.seg_size
            y = random.randint(0, max_y) * self.seg_size
            if (x, y) not in self.snake:
                return (x, y)

    def handle_keys(self, event):
        if not self.running: return
        key = event.keysym
        all_dirs = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if key in all_dirs and key != all_dirs.get(self.direction):
            self.direction = key

    def move_snake(self):
        head_x, head_y = self.snake[0]

        if self.direction == "Up": head_y -= self.seg_size
        elif self.direction == "Down": head_y += self.seg_size
        elif self.direction == "Left": head_x -= self.seg_size
        elif self.direction == "Right": head_x += self.seg_size

        new_head = (head_x, head_y)

        if (head_x < 0 or head_x >= self.canvas.winfo_width() or 
            head_y < 0 or head_y >= self.canvas.winfo_height() or 
            new_head in self.snake):
            self.game_over()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self.food = self.create_food()
        else:
            self.snake.pop()

    def update(self):
        if self.running:
            self.move_snake()
            if self.running:
                self.draw()
                self.root.after(self.speed, self.update)

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_oval(self.food[0], self.food[1], 
                                self.food[0]+self.seg_size, self.food[1]+self.seg_size, 
                                fill="red", outline="white")
        for i, (x, y) in enumerate(self.snake):
            color = "white" if i == 0 else "#AAAAAA"
            self.canvas.create_rectangle(x, y, x+self.seg_size, y+self.seg_size, fill=color, outline="black")

        self.canvas.create_text(50, 20, text=f"Счет: {self.score}", fill="white", font=("Arial", 12))

    def game_over(self):
        self.running = False
        if self.score > self.high_score:
            self.high_score = self.score

        w, h = self.get_center()

        # Подложка
        self.canvas.create_rectangle(w-200, h-110, w+200, h+110, fill="#330000", outline="white", width=2)

        # Текст
        self.canvas.create_text(w, h - 40, text="ИГРА ОКОНЧЕНА", fill="white", font=("Arial", 22, "bold"))
        self.canvas.create_text(w, h + 10, text=f"Ваш счет: {self.score}", fill="white", font=("Arial", 16))

        # Создаем объект текста для таймера и сохраняем его ID
        self.countdown = 5
        self.timer_text_id = self.canvas.create_text(w, h + 70, 
                                                     text=f"Возврат в меню через: {self.countdown}", 
                                                     fill="yellow", font=("Arial", 12, "bold"))

        # Запускаем отсчет
        self.tick_timer()

    def tick_timer(self):
        """Метод для динамического обновления таймера на экране"""
        if self.countdown > 1:
            self.countdown -= 1
            # Обновляем текст существующего объекта на Canvas по его ID
            self.canvas.itemconfig(self.timer_text_id, text=f"Возврат в меню через: {self.countdown}")
            # Планируем следующий «тик» через 1 секунду
            self.root.after(1000, self.tick_timer)
        else:
            # Когда время вышло, выходим в меню
            self.show_menu()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    game = SnakeGame(root)
    root.mainloop()