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
    def __init__(self, timer_app):
        super().__init__()
        self.stop_event = threading.Event()
        self.band_powers = []
        self.theta_alpha_ratios = []
        self.timestamps = []
        self.theta_values = []
        self.alpha_values = []
        self.detailed_log_file = None
        self.timer_app = timer_app

    def run(self):
        self.start_udp_listener()

    def start_udp_listener(self):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 12345

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
                self.detailed_log_file.close()

    def process_band_power_data(self, data_dict):
        band_power_data = data_dict["data"]
        num_channels = len(band_power_data)

        channel_averages = [sum(row[i] for row in band_power_data) / num_channels for i in range(5)]
        avg_theta = channel_averages[1]
        avg_alpha = channel_averages[2]

        self.timestamps.append(datetime.now())
        self.theta_values.append(avg_theta)
        self.alpha_values.append(avg_alpha)

        theta_alpha_ratio = avg_theta / avg_alpha if avg_alpha != 0 else float('inf')

        self.band_powers.append(channel_averages)
        self.theta_alpha_ratios.append(theta_alpha_ratio)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_entry = {
            "timestamp": timestamp,
            "test_interval": self.timer_app.current_cycle,
            "current_genre": self.timer_app.music_player.current_genre,
            "current_song": self.timer_app.music_player.current_song,
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

class MusicPlayer:
    def __init__(self, timer_app):
        self.timer_app = timer_app
        self.current_genre = None
        self.current_song = None
        self.used_genres = []
        self.played_songs = []

    def play_music(self, current_cycle):
        available_genres = [genre for genre in os.listdir(MUSIC_FOLDER) if genre not in self.used_genres]
        if available_genres:
            self.current_genre = random.choice(available_genres)
            self.used_genres.append(self.current_genre)
            print(f"Test {current_cycle}: {self.current_genre}")
            mixer.init()
            genre_folder = os.path.join(MUSIC_FOLDER, self.current_genre)
            songs = [os.path.join(genre_folder, song) for song in os.listdir(genre_folder)]
            random.shuffle(songs)
            self.played_songs = []
            self.play_song(songs)
        else:
            print(f"Test {current_cycle}: All Genres Have Been Played")

    def play_song(self, songs):
        if songs and self.timer_app.timer_running:
            song = songs.pop(0)
            self.current_song = os.path.splitext(os.path.basename(song))[0]
            print(self.current_song)
            mixer.music.load(song)
            mixer.music.play()
            self.played_songs.append(self.current_song)
            song_duration = mixer.Sound(song).get_length()
            remaining_time = self.timer_app.get_remaining_time()
            if remaining_time > song_duration:
                self.root.after(int(song_duration * 1000), self.play_song, songs)


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.current_cycle = 1
        self.udp_listener = UDPListener(self)
        self.timer_running = False
        self.remaining_time = 0
        self.music_player = MusicPlayer(self)

        self.root.title("Timer")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_timer)
        self.start_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.test_interval_label = tk.Label(self.root, text="", font=("Arial", 16))
        self.timer_label = tk.Label(self.root, text="", font=("Arial", 24), wraplength=300)
        self.break_label = tk.Label(self.root, text="", font=("Arial", 18), fg="gray", wraplength=300)
        self.continue_button = tk.Button(self.root, text="Continue", command=self.on_continue, state=tk.DISABLED, fg="gray")

    def start_timer(self):
        self.current_cycle = 1
        self.music_player.used_genres = []
        self.start_button.place_forget()
        self.test_interval_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        self.test_interval_label.config(text=f"Test Interval {self.current_cycle}")
        self.timer_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        print("Test 1: None")
        self.countdown(TIMER_DURATION_SECONDS)
        self.udp_listener.start()

    def countdown(self, seconds):
        self.timer_running = True
        self.remaining_time = seconds
        if seconds <= 0:
            self.timer_running = False
            self.remaining_time = 0
            self.udp_listener.stop()
            self.udp_listener.join()
            self.create_summary_log()
            self.create_graph()
            if self.current_cycle != 1:
                mixer.music.stop()
            if self.current_cycle == MAX_CYCLES:
                self.timer_label.config(text="Congratulations!\nYou have completed the Musical Flow State Test!")
                self.continue_button.place_forget()
                self.test_interval_label.place_forget()
            else:
                self.timer_label.config(text="Time's Up:\nTake a Break")
                self.break_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
                self.break_label.config(text=f"{BREAK_DURATION_SECONDS // 60:02d}:{BREAK_DURATION_SECONDS % 60:02d}")
                self.continue_button.config(state=tk.DISABLED, fg="gray")
                self.continue_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
                self.break_countdown(BREAK_DURATION_SECONDS)
        else:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            self.timer_label.config(text=f"{minutes:02d}:{remaining_seconds:02d}")
            self.remaining_time = seconds
            self.root.after(1000, self.countdown, seconds - 1)

    def get_remaining_time(self):
        return self.remaining_time
    
    def break_countdown(self, seconds):
        if seconds <= 0:
            self.break_label.place_forget()
            self.continue_button.config(state=tk.NORMAL, fg="black")
        else:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            self.break_label.config(text=f"{minutes:02d}:{remaining_seconds:02d}")
            self.root.after(1000, self.break_countdown, seconds - 1)
    
    def on_continue(self):
        self.current_cycle += 1
        self.test_interval_label.config(text=f"Test Interval {self.current_cycle}")
        self.break_label.place_forget()
        self.continue_button.place_forget()
        self.countdown(TIMER_DURATION_SECONDS)
        self.music_player.play_music(self.current_cycle)
    
    def create_summary_log(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        summary_log_file_path = os.path.join("logs", f"{timestamp}_summary_log.txt")
    
        with open(summary_log_file_path, "w") as summary_log_file:
            summary_log_file.write(f"Test Interval {self.current_cycle}:\n")
            summary_log_file.write(f"Genre: {self.music_player.used_genres[-1] if self.current_cycle > 1 else 'None'}\n")
            summary_log_file.write(f"Played Songs: {', '.join(self.music_player.played_songs) if self.current_cycle > 1 else 'None'}\n\n")

            num_samples = len(self.udp_listener.band_powers)
            if num_samples > 0:
                avg_band_powers_whole = [sum(x[i] for x in self.udp_listener.band_powers) / num_samples for i in range(5)]
                summary_log_file.write(f"Average Band Powers (Duration: {TIMER_DURATION_SECONDS} seconds):\n")
                summary_log_file.write(json.dumps(avg_band_powers_whole) + "\n\n")
    
            if num_samples > 0:
                start_index = num_samples // 3
                end_index = 2 * start_index
                avg_band_powers_middle = [sum(x[i] for x in self.udp_listener.band_powers[start_index:end_index]) / (end_index - start_index) for i in range(5)]
                summary_log_file.write("Average Band Powers (Middle Third):\n")
                summary_log_file.write(json.dumps(avg_band_powers_middle) + "\n\n")
    
            if len(self.udp_listener.theta_alpha_ratios) > 0:
                avg_theta_alpha_whole = sum(self.udp_listener.theta_alpha_ratios) / len(self.udp_listener.theta_alpha_ratios)
                summary_log_file.write(f"Average Theta/Alpha Ratio (Duration: {TIMER_DURATION_SECONDS} seconds):\n")
                summary_log_file.write(str(avg_theta_alpha_whole) + "\n\n")
    
            if len(self.udp_listener.theta_alpha_ratios) > 0:
                avg_theta_alpha_middle = sum(self.udp_listener.theta_alpha_ratios[start_index:end_index]) / (end_index - start_index)
                summary_log_file.write("Average Theta/Alpha Ratio (Middle Third):\n")
                summary_log_file.write(str(avg_theta_alpha_middle) + "\n\n")
    
    def create_graph(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        graph_file_path = os.path.join("logs", f"{timestamp}_graph.png")

        start_time = self.udp_listener.timestamps[0]
        seconds_since_start = [(t - start_time).total_seconds() for t in self.udp_listener.timestamps]

        plt.figure(figsize=(10, 6))
        plt.plot(seconds_since_start, self.udp_listener.theta_values, label='Theta', color='blue')
        plt.plot(seconds_since_start, self.udp_listener.alpha_values, label='Alpha', color='green')
        plt.plot(seconds_since_start, self.udp_listener.theta_alpha_ratios, label='Theta/Alpha Ratio', color='red')

        plt.xlabel('Time (seconds)')
        plt.ylabel('Value')
        plt.title('Theta, Alpha, and Theta/Alpha Ratio Over Time')
        plt.legend()
        plt.grid(True)
        plt.savefig(graph_file_path)
        plt.close()

    def on_closing(self):
        mixer.quit()
        if self.udp_listener.is_alive():
            self.udp_listener.stop()
            self.udp_listener.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()