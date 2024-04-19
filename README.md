# BCI Flow State Test

This Python application is designed to test the effect of different music genres on an individual's flow state. It uses data from an EEG device to measure the theta and alpha brain waves, which are then used to calculate the theta-alpha ratio, a metric commonly associated with the flow state.

## Features

- GUI application with a user-friendly interface
- Customizable test intervals, with a Customizable break between each interval
- During the first interval, no music is played
- In the subsequent intervals, a random song from a random genre is played
- Random polynomials are generated, and the user is asked to provide the derivative
- User's answers are checked, and the number of correct answers is recorded
- Summary log files are created with various statistics from each test interval
- Graphs are generated to display the theta, alpha, and theta-alpha ratio values over time

## Requirements

- Python 3.x
- Tkinter
- Pygame
- Matplotlib
- Sympy

## Installation

1. Clone the repository:

```
git clone https://github.com/Quantizr/BCI-Flow-State-Music.git
```

2. Navigate to the project directory:

```
cd BCI-Flow-State-Music
```

3. Add your music files within the music directory, organized by genre (e.g., `music/rock`, `music/classical`, etc.). It is recommended to replace the AI Generated example music files currently in the music directory.

4. Install the required packages:

```
pip install tkinter pygame matplotlib sympy
```

## Usage

1. In the OpenBCI GUI Networking tab, set the following:
    - Protocol: `UDP`
    - IP: `127.0.0.1`
    - Port: `12345`
    - Data Type: `BandPower` (NOT `AvgBandPower`)
2. Run the application:

```
python bci_flow_state_test.py
```

3. Follow the on-screen instructions to start the Musical Flow State Test.
4. During the test intervals, find the derivative of the displayed polynomials and enter your answers.
5. After completing all test intervals, the application will generate summary log files and graphs in the `logs` directory.

## Configuration

You can adjust the following constants in the `bci_flow_state_test.py` file:

- `TIMER_DURATION_SECONDS`: Duration of each test interval (in seconds)
- `BREAK_DURATION_SECONDS`: Duration of the break between test intervals (in seconds)
- `MAX_CYCLES`: Number of test intervals (including the initial interval without music)

## License

This project is licensed under the [MIT License](LICENSE).