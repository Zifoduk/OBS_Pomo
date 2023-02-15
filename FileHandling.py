import os

DATA_FOLDER = os.path.expanduser('~/Pomo')

def check_data_folder():
    try:
        os.mkdir(DATA_FOLDER)
    except FileExistsError as e:
        pass
    except Exception as e:
        print(e)

def write_working(time, current_task):
    write("timer", time)
    write("task", current_task.get())

def write_break(time):
    write("timer", time)
    write("task", "break")

def write_long_break(time):
    write("timer", time)
    write("task", "long break")

def write_pomodoros(counter, max_counter):
    write("pomodoros", f"Timer: {counter}/{max_counter}")

def write(filename, text):
    check_data_folder()
    with open(f"{DATA_FOLDER}\{filename}.txt", "w") as file:
        file.write(text)