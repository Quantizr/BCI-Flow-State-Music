import tkinter as tk
import os
import random
from pygame import mixer
import socket
import json
import threading
from datetime import datetime
import matplotlib.pyplot as plt

TIMER_DURATION_SECONDS = 10
BREAK_DURATION_SECONDS = 2
MAX_CYCLES = 4

MUSIC_FOLDER = "music"

class UDPListener(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.band_powers = []
        self.theta_alpha_ratios = []
        self.timestamps = []
        self.theta_values = []
        self.alpha_values = []
        self.detailed_log_file = None

    def run(self):
        self.start_udp_listener()

    def start_udp_listener(self):
        UDP_IP = "127.0.0.1"  # Replace with the appropriate IP address if needed
        UDP_PORT = 12345  # Replace with the appropriate port number if needed

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((UDP_IP, UDP_PORT))

            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            detailed_log_file_path = os.path.join(log_dir, f"{timestamp}_detailed_log.txt")
            self.detailed_log_file = open(detailed_log_file_path, "w")

            while not self.stop_event.is_set():
                data, _ = sock.recvfrom(1024)
                data_dict = json.loads(data.decode())

                if data_dict["type"] == "bandPower":
                    self.process_band_power_data(data_dict)

            if self.detailed_log_file:
                self.detailed_log_file.close()  # Close the detailed log file when the thread ends

    def process_band_power_data(self, data_dict):
        band_power_data = data_dict["data"]
        num_channels = len(band_power_data)

        # Calculate channel averages [delta, theta, alpha, beta, gamma]
        channel_averages = [sum(row[i] for row in band_power_data) / num_channels for i in range(5)]
        avg_theta = channel_averages[1]
        avg_alpha = channel_averages[2]

        # Save data for graph plotting
        self.timestamps.append(datetime.now())
        self.theta_values.append(avg_theta)
        self.alpha_values.append(avg_alpha)
        
        # Calculate theta/alpha ratio
        theta_alpha_ratio = avg_theta / avg_alpha if avg_alpha != 0 else float('inf')

        self.band_powers.append(channel_averages)
        self.theta_alpha_ratios.append(theta_alpha_ratio)

        # Write to detailed log file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_entry = {
            "timestamp": timestamp,
            "band_power_data": band_power_data,
            "channel_averages": channel_averages,
            "num_channels": num_channels,
            "avg_theta": avg_theta,
            "avg_alpha": avg_alpha,
            "theta_alpha_ratio": theta_alpha_ratio
        }
        self.detailed_log_file.write(json.dumps(log_entry) + "\n")
        self.detailed_log_file.flush()

    def stop(self):
        self.stop_event.set()


def create_summary_log():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    summary_log_file_path = os.path.join("logs", f"{timestamp}_summary_log.txt")

    with open(summary_log_file_path, "w") as summary_log_file:
        # Calculate average band powers across the whole duration
        num_samples = len(udp_listener.band_powers)
        if num_samples > 0:
            avg_band_powers_whole = [sum(x[i] for x in udp_listener.band_powers) / num_samples for i in range(5)]
            summary_log_file.write(f"Average Band Powers (Duration: {TIMER_DURATION_SECONDS} seconds):\n")
            summary_log_file.write(json.dumps(avg_band_powers_whole) + "\n\n")

        # Calculate average band powers across the middle third
        if num_samples > 0:
            start_index = num_samples // 3
            end_index = 2 * start_index
            avg_band_powers_middle = [sum(x[i] for x in udp_listener.band_powers[start_index:end_index]) / (end_index - start_index) for i in range(5)]
            summary_log_file.write("Average Band Powers (Middle Third):\n")
            summary_log_file.write(json.dumps(avg_band_powers_middle) + "\n\n")

        # Calculate average theta/alpha ratio across the whole duration
        if len(udp_listener.theta_alpha_ratios) > 0:
            avg_theta_alpha_whole = sum(udp_listener.theta_alpha_ratios) / len(udp_listener.theta_alpha_ratios)
            summary_log_file.write(f"Average Theta/Alpha Ratio (Duration: {TIMER_DURATION_SECONDS} seconds):\n")
            summary_log_file.write(str(avg_theta_alpha_whole) + "\n\n")

        # Calculate average theta/alpha ratio across the middle third
        if len(udp_listener.theta_alpha_ratios) > 0:
            avg_theta_alpha_middle = sum(udp_listener.theta_alpha_ratios[start_index:end_index]) / (end_index - start_index)
            summary_log_file.write("Average Theta/Alpha Ratio (Middle Third):\n")
            summary_log_file.write(str(avg_theta_alpha_middle) + "\n\n")

def create_graph():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    graph_file_path = os.path.join("logs", f"{timestamp}_graph.png")

    # Convert timestamps to seconds relative to the start time
    start_time = udp_listener.timestamps[0]
    seconds_since_start = [(t - start_time).total_seconds() for t in udp_listener.timestamps]

    plt.figure(figsize=(10, 6))
    
    print(len(udp_listener.timestamps))
    print(len(udp_listener.theta_values))

    # Plot theta, alpha, theta/alpha ratio values
    plt.plot(seconds_since_start, udp_listener.theta_values, label='Theta', color='blue')
    plt.plot(seconds_since_start, udp_listener.alpha_values, label='Alpha', color='green')
    plt.plot(seconds_since_start, udp_listener.theta_alpha_ratios, label='Theta/Alpha Ratio', color='red')

    plt.xlabel('Time (seconds)')
    plt.ylabel('Value')
    plt.title('Theta, Alpha, and Theta/Alpha Ratio Over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig(graph_file_path)
    plt.close()

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
    udp_listener.start()  # Start listening for UDP data

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
        udp_listener.stop()  # Stop listening for UDP data when time is up
        create_summary_log()
        create_graph()
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
    if udp_listener.is_alive():
        udp_listener.stop()
        udp_listener.join()
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

# Create UDP listener thread
udp_listener = UDPListener()

root.mainloop()