import tkinter as tk


class ProgressWindow:
    def __init__(self):
        self.root = None
        self.progress_window = None
        self.progress_label = None

    def create(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("進行状況")
        self.progress_window.geometry("500x150")
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
            text="処理を開始します...",
            font=("MS Gothic", 11),
            wraplength=450,
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
