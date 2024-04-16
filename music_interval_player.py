import tkinter as tk
import os
import random
from pygame import mixer

TIMER_DURATION_SECONDS = 60
BREAK_DURATION_SECONDS = 5
MAX_CYCLES = 4

MUSIC_FOLDER = "music"

def start_timer():
    global current_cycle, used_genres
    current_cycle = 1
    used_genres = []
    start_button.place_forget()
    test_interval_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
    test_interval_label.config(text=f"Test Interval {current_cycle}")
    timer_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    print("Test 1: None") # no music during Test 1
    countdown(TIMER_DURATION_SECONDS)

def play_music():
    global current_genre
    available_genres = [genre for genre in os.listdir(MUSIC_FOLDER) if genre not in used_genres]
    if available_genres:
        current_genre = random.choice(available_genres)
        used_genres.append(current_genre)
        print(f"Test {current_cycle}: {current_genre}")
        mixer.init()
        genre_folder = os.path.join(MUSIC_FOLDER, current_genre)
        songs = [os.path.join(genre_folder, song) for song in os.listdir(genre_folder)]
        random.shuffle(songs)
        play_song(songs)
    else:
        print(f"Test {current_cycle}: All Genres Have Been Played")

def play_song(songs):
    if songs:
        song = songs.pop(0)
        print(os.path.splitext(os.path.basename(song))[0])
        mixer.music.load(song)
        mixer.music.play()
        root.after(int(mixer.Sound(song).get_length() * 1000), play_song, songs)

def countdown(seconds):
    global current_cycle
    if seconds <= 0:
        if (current_cycle != 1):
            mixer.music.stop()
        if current_cycle == MAX_CYCLES:
            timer_label.config(text="Congratulations!\nYou have completed the Musical Flow State Test!")
            continue_button.place_forget()
            test_interval_label.place_forget()
        else:
            timer_label.config(text="Time's Up:\nTake a Break")
            break_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
            break_label.config(text=f"{BREAK_DURATION_SECONDS // 60:02d}:{BREAK_DURATION_SECONDS % 60:02d}")
            continue_button.config(state=tk.DISABLED, fg="gray")
            continue_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
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
    play_music()
    countdown(TIMER_DURATION_SECONDS)  # Start the next countdown

def on_closing():
    mixer.quit()
    root.destroy()

# Set up the main window
root = tk.Tk()
root.title("Timer")
root.geometry("400x300")
root.protocol("WM_DELETE_WINDOW", on_closing)  # Add this line

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