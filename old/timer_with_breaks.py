import tkinter as tk

TIMER_DURATION_SECONDS = 5
BREAK_DURATION_SECONDS = 2
MAX_CYCLES = 4

def start_timer():
    global current_cycle
    current_cycle = 1
    start_button.place_forget()  # Remove the start button
    test_interval_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)  # Place the test interval label
    test_interval_label.config(text=f"Test Interval {current_cycle}")
    timer_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)  # Place the timer label
    countdown(TIMER_DURATION_SECONDS)  # Start the countdown with the global duration

def countdown(seconds):
    global current_cycle
    if seconds <= 0:
        if current_cycle == MAX_CYCLES:
            timer_label.config(text="Congratulations!\nYou have completed the Musical Flow State Test!")
            continue_button.place_forget()  # Remove the continue button
            test_interval_label.place_forget()
        else:
            timer_label.config(text="Time's Up:\nTake a Break")
            break_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)  # Place the break label
            break_label.config(text=f"{BREAK_DURATION_SECONDS // 60:02d}:{BREAK_DURATION_SECONDS % 60:02d}")
            continue_button.config(state=tk.DISABLED, fg="gray")  # Disable and grey out the continue button
            continue_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)  # Place the continue button
            break_countdown(BREAK_DURATION_SECONDS)
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        timer_label.config(text=f"{minutes:02d}:{remaining_seconds:02d}")
        root.after(1000, countdown, seconds - 1)

def break_countdown(seconds):
    if seconds <= 0:
        break_label.place_forget()  # Remove the break label
        continue_button.config(state=tk.NORMAL, fg="black")  # Enable and ungrey the continue button
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        break_label.config(text=f"{minutes:02d}:{remaining_seconds:02d}")
        root.after(1000, break_countdown, seconds - 1)

def on_continue():
    global current_cycle
    current_cycle += 1
    test_interval_label.config(text=f"Test Interval {current_cycle}")
    break_label.place_forget()  # Remove the break label
    continue_button.place_forget()  # Remove the continue button
    countdown(TIMER_DURATION_SECONDS)  # Start the next countdown

# Set up the main window
root = tk.Tk()
root.title("Timer")
root.geometry("400x300")  # Set the window size

# Create a start button
start_button = tk.Button(root, text="Start", command=start_timer)
start_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Place the start button in the middle

# Create a label to display the test interval
test_interval_label = tk.Label(root, text="", font=("Arial", 16))

# Create a label to display the timer
timer_label = tk.Label(root, text="", font=("Arial", 24), wraplength=300)

# Create a label to display the break timer
break_label = tk.Label(root, text="", font=("Arial", 18), fg="gray", wraplength=300)

# Create a continue button
continue_button = tk.Button(root, text="Continue", command=on_continue, state=tk.DISABLED, fg="gray")

root.mainloop()