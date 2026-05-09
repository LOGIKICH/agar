import customtkinter as ctk
import tkinter as tk
import random
import threading
import time
import json
import os
from PIL import Image, ImageDraw, ImageTk

# ------------------------------------------------------------
# Допоміжний клас для анімованої бульбашки
# ------------------------------------------------------------
class Bubble:
    """Анімована бульбашка, що рухається вгору та перезапускається знизу."""
    def __init__(self, canvas, width, height, speed, size, color, glow_color):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.speed = speed
        self.size = size
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = color
        self.glow_color = glow_color

        # Основний овал
        self.id = canvas.create_oval(
            self.x, self.y, self.x + size, self.y + size,
            fill=color, outline=color, width=1
        )
        # Світіння (більший напівпрозорий овал)
        self.glow = canvas.create_oval(
            self.x - 6, self.y - 6, self.x + size + 6, self.y + size + 6,
            fill=glow_color, outline="", stipple="gray50"
        )
        # Блик (біла цятка)
        highlight_size = max(2, size // 5)
        self.highlight = canvas.create_oval(
            self.x + size * 0.2, self.y + size * 0.2,
            self.x + size * 0.2 + highlight_size, self.y + size * 0.2 + highlight_size,
            fill="white", outline=""
        )

    def move(self):
        """Перемістити бульбашку вгору; якщо вийшла за верхню межу — скинути вниз."""
        self.y -= self.speed
        if self.y < -100:
            self.y = self.height + random.randint(0, 200)
            self.x = random.randint(0, self.width)
        self.canvas.move(self.id, 0, -self.speed)
        self.canvas.move(self.glow, 0, -self.speed)
        self.canvas.move(self.highlight, 0, -self.speed)


# ------------------------------------------------------------
# Головний клас Launcher
# ------------------------------------------------------------
class Launcher(ctk.CTk):
    """Головне вікно лаунчера з усією логікою роботи."""
    CONFIG_FILE = "launcher_config.json"
    WINDOW_WIDTH = 480
    WINDOW_HEIGHT = 420

    def __init__(self):
        super().__init__()
        self.title("Agar.io Launcher • Premium Edition")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)


        self.username = None
        self.host = None
        self.port = None



        # Завантаження збережених даних
        self.config = self._load_config()

        # Створення інтерфейсу
        self._create_background_canvas()
        self._create_bubbles()
        self._create_main_frame()
        self._create_input_fields()
        self._create_controls()

        # Запуск анімацій
        self._animate_bubbles()
        self._blink_title()

    # --------------------------------------------------------
    # Ініціалізація інтерфейсу
    # --------------------------------------------------------
    def _create_background_canvas(self):
        """Створює канвас і градієнтне тло."""
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        self._update_gradient_background()

    def _update_gradient_background(self):
        """Генерує градієнтне зображення з зірками та встановлює його на канвас."""
        w, h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)

        top = (10, 15, 35)
        bottom = (45, 25, 85)
        for y in range(h):
            r = int(top[0] + (bottom[0] - top[0]) * y / h)
            g = int(top[1] + (bottom[1] - top[1]) * y / h)
            b = int(top[2] + (bottom[2] - top[2]) * y / h)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # Додаємо зірки
        for _ in range(120):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(1, 2)
            brightness = random.randint(150, 255)
            draw.ellipse((x, y, x + size, y + size), fill=(brightness, brightness, brightness))

        self.bg_image = ImageTk.PhotoImage(img)
        if hasattr(self, 'bg_img_id'):
            self.canvas.itemconfig(self.bg_img_id, image=self.bg_image)
        else:
            self.bg_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

    def _create_bubbles(self):
        """Створює набір бульбашок різного розміру, кольору та швидкості."""
        self.bubbles = []
        color_schemes = [
            ("#ff4d4d", "#ff9999"),  # червоний
            ("#4dff4d", "#99ff99"),  # зелений
            ("#4d4dff", "#9999ff"),  # синій
            ("#ffff4d", "#ffff99"),  # жовтий
            ("#ff4dff", "#ff99ff"),  # рожевий
            ("#4dffff", "#99ffff"),  # блакитний
            ("#ffa64d", "#ffcc99"),  # оранжевий
        ]

        # Маленькі (5 шт)
        for _ in range(5):
            col, glow = random.choice(color_schemes)
            self.bubbles.append(Bubble(
                self.canvas, self.WINDOW_WIDTH, self.WINDOW_HEIGHT,
                random.uniform(0.4, 0.7), random.randint(15, 25), col, glow
            ))
        # Середні (6 шт)
        for _ in range(6):
            col, glow = random.choice(color_schemes)
            self.bubbles.append(Bubble(
                self.canvas, self.WINDOW_WIDTH, self.WINDOW_HEIGHT,
                random.uniform(0.8, 1.2), random.randint(26, 40), col, glow
            ))
        # Великі (4 шт)
        for _ in range(4):
            col, glow = random.choice(color_schemes)
            self.bubbles.append(Bubble(
                self.canvas, self.WINDOW_WIDTH, self.WINDOW_HEIGHT,
                random.uniform(1.3, 1.8), random.randint(41, 60), col, glow
            ))

    def _create_main_frame(self):
        """Створює головний фрейм з тінню та внутрішнім сяйвом."""
        self.main_frame = ctk.CTkFrame(
            self, corner_radius=24, fg_color="#0a0f1f",
            border_width=1, border_color="#2a3f6e"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.75)

        self.glow_frame = ctk.CTkFrame(
            self.main_frame, corner_radius=24, fg_color="#14223d"
        )
        self.glow_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.98)

    def _create_input_fields(self):
        """Створює поля введення (нік, IP, порт) з іконками."""
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self.main_frame, text="⊛ AGAR.IO LAUNCHER ⊛",
            font=("Segoe UI", 26, "bold"), text_color="#7aa9ff"
        )
        self.title_label.pack(pady=(24, 12))

        # Нікнейм
        self.nick_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.nick_frame.pack(pady=6, padx=28, fill="x")
        ctk.CTkLabel(self.nick_frame, text="👤", font=("Segoe UI", 16), width=30).pack(side="left", padx=(0, 5))
        self.entry_nick = ctk.CTkEntry(
            self.nick_frame, placeholder_text="Ваш нікнейм", height=42,
            font=("Segoe UI", 14), corner_radius=12
        )
        self.entry_nick.pack(side="left", fill="x", expand=True)
        self.entry_nick.insert(0, self.config.get("nick", ""))

        # IP-адреса
        self.ip_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.ip_frame.pack(pady=6, padx=28, fill="x")
        ctk.CTkLabel(self.ip_frame, text="🌐", font=("Segoe UI", 16), width=30).pack(side="left", padx=(0, 5))
        self.entry_ip = ctk.CTkEntry(
            self.ip_frame, placeholder_text="IP-адреса сервера", height=42,
            font=("Segoe UI", 14), corner_radius=12
        )
        self.entry_ip.pack(side="left", fill="x", expand=True)
        self.entry_ip.insert(0, self.config.get("ip", "127.0.0.1"))

        # Порт
        self.port_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.port_frame.pack(pady=6, padx=28, fill="x")
        ctk.CTkLabel(self.port_frame, text="🔌", font=("Segoe UI", 16), width=30).pack(side="left", padx=(0, 5))
        self.entry_port = ctk.CTkEntry(
            self.port_frame, placeholder_text="Порт", height=42,
            font=("Segoe UI", 14), corner_radius=12
        )
        self.entry_port.pack(side="left", fill="x", expand=True)
        self.entry_port.insert(0, self.config.get("port", "443"))

    def _create_controls(self):
        """Створює кнопку входу, прогрес-бар та рядок статусу."""
        self.button = ctk.CTkButton(
            self.main_frame, text="▶ УВІЙТИ В ГРУ ◀", height=46,
            font=("Segoe UI", 16, "bold"), corner_radius=14,
            fg_color="#1e3f8a", hover_color="#2b5fd6", command=self._login
        )
        self.button.pack(pady=18, padx=28, fill="x")

        self.progress = ctk.CTkProgressBar(self.main_frame, height=8, corner_radius=4)
        self.progress.pack(pady=(5, 5), padx=28, fill="x")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self.main_frame, text="Готовий до підключення",
            font=("Segoe UI", 12), text_color="#a0b4d7"
        )
        self.status_label.pack(pady=(5, 20))

    # --------------------------------------------------------
    # Анімації
    # --------------------------------------------------------
    def _animate_bubbles(self):
        """Анімація руху бульбашок (рекурсивний виклик)."""
        for bubble in self.bubbles:
            bubble.move()
        self.after(30, self._animate_bubbles)

    def _blink_title(self):
        """Мерехтіння кольору заголовка."""
        current = self.title_label.cget("text_color")
        new_color = "#3a6eff" if current == "#7aa9ff" else "#7aa9ff"
        self.title_label.configure(text_color=new_color)
        self.after(800, self._blink_title)

    # --------------------------------------------------------
    # Робота з конфігурацією
    # --------------------------------------------------------
    def _load_config(self):
        """Завантажує збережені дані з JSON-файлу."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_config(self):
        """Зберігає поточні дані в JSON-файл."""
        self.config["nick"] = self.entry_nick.get().strip()
        self.config["ip"] = self.entry_ip.get().strip()
        self.config["port"] = self.entry_port.get().strip()
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    # --------------------------------------------------------
    # Логіка підключення
    # --------------------------------------------------------
    def _show_status(self, text, color="#a0b4d7", auto_reset=True):
        """Відображає повідомлення в рядку статусу."""
        self.status_label.configure(text=text, text_color=color)
        if auto_reset and color != "red":
            self.after(3000, lambda: self.status_label.configure(
                text="Готовий до підключення", text_color="#a0b4d7"
            ))

    def _simulate_connection(self, nick, ip, port):
        """Симуляція процесу підключення (виконується в окремому потоці)."""
        for i in range(1, 5):
            time.sleep(0.5)
            self.after(0, lambda p=i/4: self.progress.set(p))
        self.after(0, self._connection_success, nick, ip, port)

    def _connection_success(self, nick, ip, port):
        """Дії після успішного підключення."""
        self.progress.set(1)
        self._show_status(f"✅ Підключено! Вітаємо, {nick} → {ip}:{port}", "#66ff66")
        self.button.configure(state="normal", text="▶ УВІЙТИ В ГРУ ◀")
        # Імітація запуску гри
        self.after(1500, lambda: self._show_status("🎮 Запуск гри... Зачекайте", "#88aaff"))
        self.after(2500, lambda: self._show_status("Гра запущена! Гарної гри!", "#66ff66"))
        # Тут можна додати реальний запуск клієнта, наприклад:
        # import subprocess
        # subprocess.Popen(["agario_client.exe", nick, ip, str(port)])

    def _login(self):
        """Обробник натискання кнопки «Увійти в гру»."""
        nick = self.entry_nick.get().strip()
        ip = self.entry_ip.get().strip()
        port_str = self.entry_port.get().strip()

        if not nick:
            self._show_status("❌ Введіть нікнейм", "red", auto_reset=False)
            return
        if not ip:
            self._show_status("❌ Введіть IP-адресу", "red", auto_reset=False)
            return
        if not port_str.isdigit():
            self._show_status("❌ Порт має бути числом", "red", auto_reset=False)
            return

        self._save_config()
        self.button.configure(state="disabled", text="⏳ ПІДКЛЮЧЕННЯ...")
        self.progress.set(0.2)
        self._show_status("🔗 З'єднання з сервером...", "#ffcc44")

        threading.Thread(target=self._simulate_connection,
                         args=(nick, ip, int(port_str)), daemon=True).start()

    def _on_closing(self):
        """Зберігає конфігурацію та закриває вікно."""
        self._save_config()
        self.destroy()


# ------------------------------------------------------------
# Точка входу
# ------------------------------------------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = Launcher()
    app.mainloop()