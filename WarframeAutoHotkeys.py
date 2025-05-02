import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import glob
import subprocess
import json

class AHKRunner:
    def __init__(self, master, ahk_folder, ahk_executable):
        self.master = master
        self.ahk_folder = ahk_folder
        self.ahk_executable = ahk_executable
        self.current_process = None
        self.scripts = []

        self.setup_theme()
        self.setup_ui()
        self.load_scripts()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        self.bg_color = "#f0f0f0"
        self.fg_color = "#333333"
        self.accent_color = "#0078d4"
        
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", 
                       background=self.bg_color,
                       foreground=self.fg_color,
                       font=('Segoe UI', 10))
        style.configure("TRadiobutton",
                       background=self.bg_color,
                       foreground=self.fg_color,
                       font=('Segoe UI', 9),
                       focuscolor=self.bg_color)
        style.map("TRadiobutton",
                 background=[('active', self.bg_color)],
                 foreground=[('active', self.accent_color)])

    def setup_ui(self):
        self.master.title("Warframe AutoHotkeys")
        self.master.geometry("500x400")
        self.master.configure(bg=self.bg_color)
        self.master.iconbitmap(self.get_icon_path())

        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header = ttk.Label(main_frame, 
                          text="Select a script to run:",
                          font=('Segoe UI', 12, 'bold'))
        header.pack(pady=(0, 10), anchor='w')

        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(scroll_frame,
                               yscrollcommand=scrollbar.set,
                               bg=self.bg_color,
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

        self.inner_frame.bind("<Configure>", self.on_frame_configure)

        self.status_bar = ttk.Label(self.master, 
                                  text="Ready",
                                  relief=tk.SUNKEN,
                                  anchor=tk.W,
                                  font=('Segoe UI', 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.radio_var = tk.StringVar()

    def load_scripts(self):
        pattern = os.path.join(self.ahk_folder, "*.ahk")
        self.scripts = glob.glob(pattern)
        self.scripts.sort()

        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        for idx, script in enumerate(self.scripts):
            rb = ttk.Radiobutton(
                self.inner_frame,
                text=os.path.basename(script),
                variable=self.radio_var,
                value=script,
                command=lambda s=script: self.run_script(s),
                style='TRadiobutton'
            )
            rb.pack(anchor='w', padx=20, pady=5)
        self.radio_var.set('')

    def run_script(self, script_path):
        self.stop_current_process()
        try:
            self.current_process = subprocess.Popen(
                [self.ahk_executable, script_path]
            )
            self.update_status(f"Running: {os.path.basename(script_path)}")
        except Exception as e:
            self.show_error(f"Failed to run script: {str(e)}")

    def stop_current_process(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=3)
                self.update_status("Stopped")
            except:
                pass
            finally:
                self.current_process = None

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.master.after(3000, lambda: self.status_bar.config(text="Ready"))

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.update_status("Failed")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_icon_path(self):
        return ""

    def on_close(self):
        self.stop_current_process()
        self.master.destroy()

if __name__ == "__main__":
    config_path = Path(__file__).parent / "Config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        AHK_FOLDER = config["AHK_FOLDER"]
        AHK_EXE = config["AHK_EXE"]
        
        if not Path(AHK_EXE).exists() or AHK_EXE == "":
            raise ValueError("AutoHotKey executable file not found")
        if not Path(AHK_FOLDER).exists() or AHK_FOLDER == "":
            raise ValueError("AutoHotKey folder not found")
            
    except Exception as e:
        messagebox.showerror("Configuration Error", 
            f"Loading configuration failed: {str(e)}\n"
            "Please check your configuration file.")
        exit()

    root = tk.Tk()
    app = AHKRunner(root, AHK_FOLDER, AHK_EXE)
    root.geometry("400x300")
    root.mainloop()