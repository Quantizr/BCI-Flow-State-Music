import socket
import json
import signal
import sys
from datetime import datetime

def signal_handler(sig, frame):
    print('Closing the connection...')
    sock.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Set up the UDP socket
UDP_IP = "127.0.0.1"  # Replace with the appropriate IP address if needed
UDP_PORT = 12345  # Replace with the appropriate port number if needed

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    data_dict = json.loads(data.decode())

    if data_dict["type"] == "bandPower":
        band_power_data = data_dict["data"]
        num_channels = len(band_power_data)

        # Calculate channel averages [delta, theta, alpha, beta, gamma]
        channel_averages = []
        for i in range(5):
            channel_sum = sum(row[i] for row in band_power_data)
            channel_avg = channel_sum / num_channels
            channel_averages.append(channel_avg)

        avg_theta = channel_averages[1]
        avg_alpha = channel_averages[2]

        # Calculate theta/alpha ratio
        theta_alpha_ratio = avg_theta / avg_alpha if avg_alpha != 0 else float('inf')

        # Get the timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # Log the data
        log_entry = {
            "timestamp": timestamp,
            "band_power_data": band_power_data,
            "channel_averages": channel_averages,
            "num_channels": num_channels,
            "avg_theta": avg_theta,
            "avg_alpha": avg_alpha,
            "theta_alpha_ratio": theta_alpha_ratio
        }

        print(json.dumps(log_entry, indent=4))
        print()