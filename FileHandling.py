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
    write("pomodoros", f"timer: {counter}/{max_counter}")

def write(filename, text):
    with open(f"{filename}.txt", "w") as file:
        file.write(text)