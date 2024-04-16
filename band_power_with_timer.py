import tkinter as tk
import socket
import json
import threading
import os
from datetime import datetime

TIMER_DURATION_SECONDS = 10

class UDPListener(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.band_powers = []
        self.theta_alpha_ratios = []
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

def start_timer():
    start_button.place_forget()  # Remove the start button
    timer_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Place the timer label in the middle
    countdown(TIMER_DURATION_SECONDS)  # Start the countdown with the global duration
    udp_listener.start()  # Start listening for UDP data

def countdown(seconds):
    if seconds <= 0:
        timer_label.config(text="Time's up!")
        udp_listener.stop()  # Stop listening for UDP data when time is up
        create_summary_log()
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        timer_label.config(text=f"{minutes:02d}:{remaining_seconds:02d}")
        root.after(1000, countdown, seconds - 1)


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
            summary_log_file.write(f"Average Band Powers (Middle Third):\n")
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


def on_closing():
    if udp_listener.is_alive():
        udp_listener.stop()
        udp_listener.join()
    root.destroy()

# Set up the main window
root = tk.Tk()
root.title("Timer")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create a start button
start_button = tk.Button(root, text="Start", command=start_timer)
start_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Place the start button in the middle

# Create a label to display the timer
timer_label = tk.Label(root, text="", font=("Arial", 24))

# Create UDP listener thread
udp_listener = UDPListener()

# Run the application
root.mainloop()
