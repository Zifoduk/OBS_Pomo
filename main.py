import time
import threading
import tkinter as tk
from tkinter import ttk, PhotoImage
import FileHandling
import os
import sys
from windows_toasts import WindowsToaster, ToastImageAndText1


os.chdir(sys._MEIPASS)
class PomodoroTimer:

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("600x350")
        self.root.title("Pomodoro OBS Timer")
        self.root.resizable(False,False)
        self.root.iconbitmap("data/icon.ico")

        self.s= ttk.Style()
        self.s.configure("TNotebook.Tab", font=("Ubuntu", 16))
        self.s.configure("TButton", font=("Ubuntu", 16))

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", pady=10, expand=True)

        self.tab1 = ttk.Frame(self.tabs, width=600, height=100)
        self.tab2 = ttk.Frame(self.tabs, width=600, height=100)
        self.tab3 = ttk.Frame(self.tabs, width=600, height=100)

        self.pomodoro_timer_label = ttk.Label(self.tab1, text="30:00", font=("Ubuntu", 48))
        self.pomodoro_timer_label.pack(pady=20)

        self.short_break_timer_label = ttk.Label(self.tab2, text="10:00", font=("Ubuntu", 48))
        self.short_break_timer_label.pack(pady=20)

        self.long_break_timer_label = ttk.Label(self.tab3, text="20:00", font=("Ubuntu", 48))
        self.long_break_timer_label.pack(pady=20)

        self.tab1_grid_layout = ttk.Frame(self.tab1)
        self.tab1_grid_layout.pack(pady=0)

        self.current_task_entry_label = ttk.Label(self.tab1_grid_layout, text="Current Task: ", font=("Ubuntu", 16))
        self.current_task_entry_label.grid(row=0, column=0)

        self.current_task = tk.StringVar()
        self.current_task_entry = ttk.Entry(self.tab1_grid_layout, textvariable=self.current_task, justify= "center")
        self.current_task_entry.grid(row=0, column=1)
        
        self.max_pomodoros_entry_label = ttk.Label(self.tab1_grid_layout, text="Max Pomodoros: ", font=("Ubuntu", 16))
        self.max_pomodoros_entry_label.grid(row=1, column=0)


        self.tabs.add(self.tab1, text="Pomodoro")
        self.tabs.add(self.tab2, text="Break")
        self.tabs.add(self.tab3, text="Long Break")

        self.grid_layout = ttk.Frame(self.root)
        self.grid_layout.pack(pady=10)

        self.start_button = ttk.Button(self.grid_layout, text="Start", command=self.start_timer_thread)
        self.start_button.grid(row=0, column=0)

        self.skip_button = ttk.Button(self.grid_layout, text="Skip", command=self.skip_clock)
        self.skip_button.grid(row=0, column=1)

        self.reset_button = ttk.Button(self.grid_layout, text="Reset", command=self.reset_clock)
        self.reset_button.grid(row=0, column=2)

        self.pomodoro_counter_label = ttk.Label(self.grid_layout, text="Pomodoros: 0", font=("Ubuntu", 16))
        self.pomodoro_counter_label.grid(row=1, column=0, columnspan=3)

        icon = PhotoImage(file='data/FolderIcon.png')
        self.folder_button = ttk.Button(self.grid_layout, image=icon, width=2, command=self.open_folder)
        self.folder_button.grid(row=0, column=3)

        


        self.pomodoros = 0
        self.skipped = False
        self.stopped = False
        self.running = False

        self.max_pomodoros = tk.StringVar()        
        self.max_pomodoros.trace("w", lambda name, index, mode, max_pomodoro=self.max_pomodoros: self.handle_max_pomodoro_change())
        self.max_pomodoros.set("1")
        self.max_pomodoros_entry = ttk.Entry(master=self.tab1_grid_layout, textvariable=self.max_pomodoros, justify= "center", width=5)
        self.max_pomodoros_entry.grid(row=1, column=1)

        self.reset_clock()
        self.root.mainloop()

    def handle_max_pomodoro_change(self):
        if not self.max_pomodoros.get().isnumeric():
            self.max_pomodoros.set("1")
        self.pomodoro_counter_label.config(text=f"Pomodoros: {self.pomodoros}/{self.max_pomodoros.get()}")

    def open_folder(self):
        os.startfile(self.program_path)
        pass

    def start_timer_thread(self):
        if not self.running:
            t = threading.Thread(target=self.preflight)
            t.start()
            self.running = True

    def preflight(self):
        self.wintoaster = WindowsToaster('Pomodoro App')
        self.start_timer()

    def start_timer(self):
        self.stopped = False
        self.skipped = False
        current_tab = self.tabs.index(self.tabs.select())
        FileHandling.write_pomodoros(self.pomodoros, self.max_pomodoros.get())

        if current_tab == 0:
            if int(self.pomodoros) >= int(self.max_pomodoros.get()):
                self.stopped = True

            full_seconds = 60 * 30

            while full_seconds > 0 and not self.stopped:
                minutes, seconds = divmod(full_seconds, 60)
                self.pomodoro_timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
                self.root.update()
                FileHandling.write_working(f"{minutes:02d}:{seconds:02d}", self.current_task)
                time.sleep(1)
                full_seconds -= 1

            if not self.stopped or self.skipped:
                self.pomodoros += 1
                self.pomodoro_counter_label.config(text=f"Pomodoros: {self.pomodoros}/{self.max_pomodoros.get()}")
                if self.pomodoros % 3 == 0:
                    self.tabs.select(2)
                    self.windows_toast(f"Pomodoro {self.pomodoros}/{self.max_pomodoros.get()}", "Long Break")
                else:
                    self.tabs.select(1)
                    self.windows_toast(f"Pomodoro {self.pomodoros}/{self.max_pomodoros.get()}", "Short Break")
                self.start_timer()

        elif current_tab == 1:
            full_seconds = 60 * 10
            while full_seconds > 0 and not self.stopped:
                minutes, seconds = divmod(full_seconds, 60)
                self.short_break_timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
                self.root.update()
                FileHandling.write_break(f"{minutes:02d}:{seconds:02d}")
                time.sleep(1)
                full_seconds -= 1
            if not self.stopped or self.skipped:
                self.tabs.select(0)
                self.windows_toast("Short Break", f"Pomodoro {self.pomodoros}/{self.max_pomodoros.get()}")
                self.start_timer()

        elif current_tab == 2:
            full_seconds = 60 * 20
            while full_seconds > 0 and not self.stopped:
                minutes, seconds = divmod(full_seconds, 60)
                self.long_break_timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
                self.root.update()
                FileHandling.write_long_break(f"{minutes:02d}:{seconds:02d}")
                time.sleep(1)
                full_seconds -= 1

            if not self.stopped or self.skipped:
                self.tabs.select(0)
                self.windows_toast("Long Break", f"Pomodoro {self.pomodoros}/{self.max_pomodoros.get()}")
                self.start_timer()
        
        else:
            print("Invalid timer ID")


    def reset_clock(self):
        self.stopped = True
        self.skipped = False
        self.pomodoros = 0
        self.pomodoro_timer_label.config(text="30:00")
        self.short_break_timer_label.config(text="10:00")
        self.long_break_timer_label.config(text="20:00")
        self.pomodoro_counter_label.config(text=f"Pomodoros: 0/{self.max_pomodoros.get()}")
        self.running = False

        FileHandling.write_pomodoros(self.pomodoros, self.max_pomodoros.get())

        current_tab = self.tabs.index(self.tabs.select())
        if current_tab == 0:
            FileHandling.write_working(f"30:00", self.current_task)
        elif current_tab == 1:
            FileHandling.write_break(f"10:00")
        elif current_tab == 2:
            FileHandling.write_long_break(f"20:00")


    def skip_clock(self):
        current_tab = self.tabs.index(self.tabs.select())
        if current_tab == 0:
            self.pomodoro_timer_label.config(text="30:00")
        elif current_tab == 1:
            self.short_break_timer_label.config(text="10:00")
        elif current_tab == 2:
            self.long_break_timer_label.config(text="20:00")

        self.stopped = True
        self.skipped = True

    def windows_toast(self, stage, next_stage):
        toast = ToastImageAndText1()
        toast.SetBody(f"{stage} Complete, Moving onto the next stage: {next_stage}")
        toast.SetImage("icon.ico")
        self.wintoaster.show_toast(toast)

PomodoroTimer()