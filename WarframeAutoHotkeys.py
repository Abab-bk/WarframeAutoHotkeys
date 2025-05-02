import customtkinter as tk
import tkinter.messagebox as msgbox
from pathlib import Path
import os
import glob
import subprocess
import json
import re

class AppSaver():
    # { "varName": "value"  }
    @staticmethod
    def save_settings(script_path, entries, window):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line == '; @export' and (i + 1) < len(lines):
                    var_line = lines[i + 1].strip()
                    match = re.match(r'global\s+(\w+)\s*:=\s*(.+?)(;.*)?$', var_line)
                    
                    if not match: continue

                    var_name = match.group(1)
                    if var_name not in entries: continue
                    
                    new_value = entries[var_name]
                    comment = match.group(3) or ''
                    lines[i + 1] = f'global {var_name} := {new_value}{comment}\n'
                    del entries[var_name]
                    i += 1
                i += 1

            with open(script_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            AHKRunner.show_info("Configuration saved successfully.")
            window.destroy()
        except Exception as e:
            AHKRunner.show_error(f"Failed to save configuration: {str(e)}")

    @staticmethod
    def parse_exported_variables(script_path):
        variables = {}
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line == '; @export':
                    if i + 1 < len(lines):
                        var_line = lines[i + 1].strip()
                        match = re.match(r'global\s+(\w+)\s*:=\s*(.+?)(;.*)?$', var_line)
                        if match:
                            var_name = match.group(1)
                            var_value = match.group(2).strip()
                            variables[var_name] = var_value
                            i += 1  # Skip variable line
                i += 1
        except Exception as e:
            AHKRunner.show_error(f"Parse error: {str(e)}")
        return variables


class SettingsWindow(tk.CTkToplevel):
    def __init__(self, script_path, values, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.title("Settings")
        self.settings_frame = SettingsFrame(self, "Settings", values)
        self.values = values
        self.script_path = script_path
        
        self.grid_columnconfigure(0, weight=1)

        self.button_frame = tk.CTkFrame(self)
        self.save_btn = tk.CTkButton(self.button_frame, text="Save", command=self.save_settings)
        self.cancel_btn = tk.CTkButton(self.button_frame, text="Cancel", command=self.destroy)
        
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.button_frame.grid_columnconfigure((0, 1), weight=1)  # 给两个列相同的权重  
        self.save_btn.grid(row=0, column=0, padx=(0, 10), sticky="e")  
        self.cancel_btn.grid(row=0, column=1, padx=(10, 0), sticky="w")

        self.settings_frame.grid(row=0, column=0, sticky="nsew")

        self.lift()  
        self.attributes("-topmost", True)  
        self.grab_set()

    def save_settings(self):  
        entries = {}  
        for idx, (var_name, _) in enumerate(self.values.items()):  
            entries[var_name] = self.settings_frame.inputs[idx].get()  
        
        AppSaver.save_settings(self.script_path, entries, self)

class SettingsFrame(tk.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master, label_text=title)  
        self.grid_columnconfigure(0, weight=1)  
        self.grid_columnconfigure(1, weight=2)  
        self.values = values
        self.inputs = []
    
        for idx, (var_name, var_value) in enumerate(self.values.items()):  
            label = tk.CTkLabel(self, text=var_name, anchor="w")  
            input_widget = tk.CTkEntry(self, textvariable=tk.StringVar(master=self, value=var_value))  
            
            self.inputs.append(input_widget)  
            
            label.grid(row=idx, column=0, sticky="w", padx=(20, 10), pady=5)  
            input_widget.grid(row=idx, column=1, sticky="ew", padx=(10, 20), pady=5)

class ScriptEntryDef():
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.splitext(os.path.basename(file_path))[0]
    
class ScriptEntryWidget(tk.CTkFrame):
    def __init__(self, master, entryDef, radio_var, index, runner):
        super().__init__(master)

        self.runner = runner
        self.entryDef = entryDef
        self.radio_btn = tk.CTkRadioButton(
            self,
            text="",
            variable=radio_var,
            value=index,
            command=self.on_radio_click
            )
        self.label = tk.CTkLabel(self, text=entryDef.file_name, anchor="w")
        self.button = tk.CTkButton(
            self,
            text="Settings",
            command=lambda: AHKRunner.open_settings(entryDef.file_path)
            )

        self.radio_btn.grid(row=0, column=0, sticky="w")
        self.label.grid(row=0, column=1, sticky="w")
        self.button.grid(row=0, column=2, sticky="e")

        self.grid_columnconfigure((0, 1, 2), weight=1)
    
    def on_radio_click(self):  
        self.runner.run_script(self.entryDef.file_path)

class HomePage(tk.CTkScrollableFrame):
    def __init__(self, master, title, values, runner):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.radio_var = tk.IntVar(value=0)

        for i, value in enumerate(self.values):
            widget = ScriptEntryWidget(self, value, self.radio_var, i, runner)
            widget.grid(row=i, column=0, sticky="ew", padx=20, pady=5)


class AHKRunner:
    def __init__(self, master, ahk_folder, ahk_executable):
        self.master = master
        self.ahk_folder = ahk_folder
        self.ahk_executable = ahk_executable
        self.current_process = None
        self.scripts = []

        self.setup()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup(self):
        self.master.title("Warframe AutoHotkeys")
        self.master.geometry("500x400")
        self.master.grid_columnconfigure(0, weight=1)

        pattern = os.path.join(self.ahk_folder, "*.ahk")
        self.scripts = glob.glob(pattern)
        self.scripts.sort()

        self.script_defs = [ScriptEntryDef(file_path) for file_path in self.scripts]
        self.home_page = HomePage(self.master, "", self.script_defs, self)
        self.home_page.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        pattern = os.path.join(self.ahk_folder, "*.ahk")
        self.scripts = glob.glob(pattern)
        self.scripts.sort()

    @staticmethod
    def open_settings(script_path):
        variables = AppSaver.parse_exported_variables(script_path)
        if not variables:
            AHKRunner.show_info("No exported variables found in the script.")
            return
        SettingsWindow(script_path, variables)

    def run_script(self, script_path):
        self.stop_current_process()
        try:
            self.current_process = subprocess.Popen(
                [self.ahk_executable, script_path]
            )
        except Exception as e:
            self.show_error(f"Failed to run script: {str(e)}")

    def stop_current_process(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=3)
            finally:
                self.current_process = None

    @staticmethod
    def show_error(message):
        msgbox.showerror("Error", message)

    @staticmethod
    def show_info(message):
        msgbox.showinfo("Info", message)

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
        AHKRunner.show_error(f"Loading configuration failed: {str(e)}\n"
                "Please check your configuration file.")
        exit()

    root = tk.CTk()
    app = AHKRunner(root, AHK_FOLDER, AHK_EXE)
    root.mainloop()