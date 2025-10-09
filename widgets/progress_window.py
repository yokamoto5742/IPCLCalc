import tkinter as tk

from utils.config_manager import load_config


class ProgressWindow:
    def __init__(self):
        self.root = None
        self.progress_window = None
        self.progress_label = None

        config = load_config()

        self.font_size = config.getint('Appearance', 'font_size', fallback=11)
        self.window_width = config.getint('Appearance', 'window_width', fallback=500)
        self.window_height = config.getint('Appearance', 'window_height', fallback=150)

    def create(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("進行状況")
        self.progress_window.geometry(f"{self.window_width}x{self.window_height}")
        self.progress_window.resizable(False, False)

        # ウィンドウを中央に配置
        self.progress_window.update_idletasks()
        width = self.progress_window.winfo_width()
        height = self.progress_window.winfo_height()
        x = (self.progress_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.progress_window.winfo_screenheight() // 2) - (height // 2)
        self.progress_window.geometry(f"{width}x{height}+{x}+{y}")

        self.progress_label = tk.Label(
            self.progress_window,
            text="計算処理を開始します...",
            font=("MS Gothic", self.font_size),
            wraplength=self.window_width - 50,
            justify=tk.LEFT,
            padx=20,
            pady=20
        )
        self.progress_label.pack(expand=True, fill=tk.BOTH)

        self.progress_window.update()

    def update(self, message: str):
        if self.progress_label:
            self.progress_label.config(text=message)
            self.progress_window.update()

    def close(self):
        if self.progress_window:
            self.progress_window.destroy()
        if self.root:
            self.root.destroy()
