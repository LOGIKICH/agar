import customtkinter as ctk
import tkinter as tk
import random
import threading
import time
import json
import os
from PIL import Image, ImageDraw, ImageTk, ImageFilter

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "launcher_config.json"

class Bubble:
    def __init__(self, canvas, w, h, speed, size, color, glow_color):
        self.canvas = canvas
        self.w = w
        self.h = h
        self.speed = speed
        self.size = size
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)
        self.color = color
        self.glow_color = glow_color

        # Основний овал
        self.id = canvas.create_oval(
            self.x, self.y,
            self.x + size, self.y + size,
            fill=color,
            outline=color,
            width=1
        )
        # Світіння (більший напівпрозорий овал)
        self.glow = canvas.create_oval(
            self.x - 6, self.y - 6,
            self.x + size + 6, self.y + size + 6,
            fill=glow_color,
            outline="",
            stipple="gray50"  # легка текстура для ефекту прозорості
        )
        # Блик (маленька біла точка)
        highlight_size = max(2, size // 5)
        self.highlight = canvas.create_oval(
            self.x + size * 0.2, self.y + size * 0.2,
            self.x + size * 0.2 + highlight_size, self.y + size * 0.2 + highlight_size,
            fill="white",
            outline=""
        )

    def move(self):
        self.y -= self.speed
        if self.y < -100:
            self.y = self.h + random.randint(0, 200)
            self.x = random.randint(0, self.w)
            # змінюємо позицію блику теж
        self.canvas.move(self.id, 0, -self.speed)
        self.canvas.move(self.glow, 0, -self.speed)
        self.canvas.move(self.highlight, 0, -self.speed)

class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agar.io Launcher • Premium Edition")
        self.geometry("480x420")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Завантаження збережених даних
        self.load_config()

        # Основний фоновий канвас
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        self.update_gradient_background()

        # Масив бульбашок
        self.bubbles = []
        # Створюємо багато різнокольорових бульбашок різних розмірів і швидкостей
        colors = [
            ("#ff4d4d", "#ff9999"),  # червоний
            ("#4dff4d", "#99ff99"),  # зелений
            ("#4d4dff", "#9999ff"),  # синій
            ("#ffff4d", "#ffff99"),  # жовтий
            ("#ff4dff", "#ff99ff"),  # рожевий
            ("#4dffff", "#99ffff"),  # блакитний
            ("#ffa64d", "#ffcc99"),  # оранжевий
        ]
        for _ in range(5):
            col, glow = random.choice(colors)
            self.bubbles.append(Bubble(self.canvas, 480, 420, random.uniform(0.4, 0.7), random.randint(15, 25), col, glow))
        for _ in range(6):
            col, glow = random.choice(colors)
            self.bubbles.append(Bubble(self.canvas, 480, 420, random.uniform(0.8, 1.2), random.randint(26, 40), col, glow))
        for _ in range(4):
            col, glow = random.choice(colors)
            self.bubbles.append(Bubble(self.canvas, 480, 420, random.uniform(1.3, 1.8), random.randint(41, 60), col, glow))

        # Основний фрейм з тінню
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=24,
            fg_color="#0a0f1f",
            border_width=1,
            border_color="#2a3f6e"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.75)

        # Ефект внутрішнього світіння (робимо додатковий фрейм знизу)
        self.glow_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=24,
            fg_color="#14223d",
            width=10,
            height=10
        )
        self.glow_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.98)

        # Логотип або заголовок з анімацією
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="⊛ AGAR.IO LAUNCHER ⊛",
            font=("Segoe UI", 26, "bold"),
            text_color="#7aa9ff"
        )
        self.title_label.pack(pady=(24, 12))

        # Іконки для полів (емуляція через текст)
        self.nick_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.nick_frame.pack(pady=6, padx=28, fill="x")
        self.nick_icon = ctk.CTkLabel(self.nick_frame, text="👤", font=("Segoe UI", 16), width=30)
        self.nick_icon.pack(side="left", padx=(0, 5))
        self.entry_nick = ctk.CTkEntry(
            self.nick_frame, placeholder_text="Ваш нікнейм", height=42,
            font=("Segoe UI", 14), corner_radius=12
        )
        self.entry_nick.pack(side="left", fill="x", expand=True)
        self.entry_nick.insert(0, self.config.get("nick", ""))

        self.ip_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.ip_frame.pack(pady=6, padx=28, fill="x")
        self.ip_icon = ctk.CTkLabel(self.ip_frame, text="🌐", font=("Segoe UI", 16), width=30)
        self.ip_icon.pack(side="left", padx=(0, 5))
        self.entry_ip = ctk.CTkEntry(
            self.ip_frame, placeholder_text="IP-адреса сервера", height=42,
            font=("Segoe UI", 14), corner_radius=12
        )
        self.entry_ip.pack(side="left", fill="x", expand=True)
        self.entry_ip.insert(0, self.config.get("ip", "127.0.0.1"))

        self.port_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.port_frame.pack(pady=6, padx=28, fill="x")
        self.port_icon = ctk.CTkLabel(self.port_frame, text="🔌", font=("Segoe UI", 16), width=30)
        self.port_icon.pack(side="left", padx=(0, 5))
        self.entry_port = ctk.CTkEntry(
            self.port_frame, placeholder_text="Порт", height=42,
            font=("Segoe UI", 14), corner_radius=12
        )
        self.entry_port.pack(side="left", fill="x", expand=True)
        self.entry_port.insert(0, self.config.get("port", "443"))

        # Кнопка з градієнтом (емуляція через ховер)
        self.button = ctk.CTkButton(
            self.main_frame, text="▶ УВІЙТИ В ГРУ ◀", height=46,
            font=("Segoe UI", 16, "bold"),
            corner_radius=14,
            fg_color="#1e3f8a",
            hover_color="#2b5fd6",
            command=self.login
        )
        self.button.pack(pady=18, padx=28, fill="x")

        # Прогрес-бар для статусу підключення
        self.progress = ctk.CTkProgressBar(self.main_frame, height=8, corner_radius=4)
        self.progress.pack(pady=(5, 5), padx=28, fill="x")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self.main_frame, text="Готовий до підключення",
            font=("Segoe UI", 12), text_color="#a0b4d7"
        )
        self.status_label.pack(pady=(5, 20))

        # Анімація бульбашок
        self.animate_bubbles()
        # Блінк заголовка (невелика анімація кольору)
        self.blink_title()

    def update_gradient_background(self):
        w, h = 480, 420
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        top = (10, 15, 35)
        bottom = (45, 25, 85)
        for y in range(h):
            r = int(top[0] + (bottom[0] - top[0]) * y / h)
            g = int(top[1] + (bottom[1] - top[1]) * y / h)
            b = int(top[2] + (bottom[2] - top[2]) * y / h)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        # Додаємо зірки (випадкові точки)
        for _ in range(120):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(1, 2)
            brightness = random.randint(150, 255)
            draw.ellipse((x, y, x+size, y+size), fill=(brightness, brightness, brightness))
        self.bg_image = ImageTk.PhotoImage(img)
        if hasattr(self, 'bg_img_id'):
            self.canvas.itemconfig(self.bg_img_id, image=self.bg_image)
        else:
            self.bg_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

    def animate_bubbles(self):
        for b in self.bubbles:
            b.move()
        self.after(30, self.animate_bubbles)

    def blink_title(self):
        current = self.title_label.cget("text_color")
        new_color = "#3a6eff" if current == "#7aa9ff" else "#7aa9ff"
        self.title_label.configure(text_color=new_color)
        self.after(800, self.blink_title)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        self.config["nick"] = self.entry_nick.get().strip()
        self.config["ip"] = self.entry_ip.get().strip()
        self.config["port"] = self.entry_port.get().strip()
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def login(self):
        nick = self.entry_nick.get().strip()
        ip = self.entry_ip.get().strip()
        port = self.entry_port.get().strip()

        if not nick:
            self.show_status("❌ Введіть нікнейм", "red")
            return
        if not ip:
            self.show_status("❌ Введіть IP-адресу", "red")
            return
        if not port.isdigit():
            self.show_status("❌ Порт має бути числом", "red")
            return

        self.save_config()
        self.button.configure(state="disabled", text="⏳ ПІДКЛЮЧЕННЯ...")
        self.progress.set(0.2)
        self.show_status("🔗 З'єднання з сервером...", "#ffcc44")

        # Симуляція підключення в окремому потоці
        threading.Thread(target=self.simulate_connection, args=(nick, ip, int(port)), daemon=True).start()

    def simulate_connection(self, nick, ip, port):
        # Емуляція процесу підключення з прогресом
        for i in range(1, 5):
            time.sleep(0.5)
            self.after(0, lambda p=i/4: self.progress.set(p))
        # Успішне підключення
        self.after(0, self.connection_success, nick, ip, port)

    def connection_success(self, nick, ip, port):
        self.progress.set(1)
        self.show_status(f"✅ Підключено! Вітаємо, {nick} → {ip}:{port}", "#66ff66")
        self.button.configure(state="normal", text="▶ УВІЙТИ В ГРУ ◀")
        # Тут можна викликати реальний запуск клієнта гри
        # Наприклад: subprocess.Popen(["agario_client.exe", nick, ip, port])
        # Зараз просто імітуємо перехід
        self.after(1500, lambda: self.show_status("🎮 Запуск гри... Зачекайте", "#88aaff"))
        self.after(2500, lambda: self.show_status("Гра запущена! Гарної гри!", "#66ff66"))

    def show_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)
        # Анімація згасання через 3 секунди (тільки для звичайних повідомлень)
        if color != "red":
            self.after(3000, lambda: self.status_label.configure(text="Готовий до підключення", text_color="#a0b4d7"))

    def on_closing(self):
        self.save_config()
        self.destroy()

if __name__ == "__main__":
    app = Launcher()
    app.mainloop()