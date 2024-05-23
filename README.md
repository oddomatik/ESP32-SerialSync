# ESP32 File Monitor

This project provides a Python script to monitor a directory for file changes and upload modified files to an ESP32 board. It also maintains a serial terminal connection to the ESP32 for interacting with the REPL.

## Features

- Monitors a specified directory for file changes.
- Uploads modified files to the ESP32 board using `mpremote`.
- Maintains a serial terminal connection for interacting with the ESP32 REPL.

## Requirements

- Python 3.x
- `pyserial`
- `watchdog`
- `mpremote`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/esp32_file_monitor.git
    cd esp32_file_monitor
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script with the following command-line arguments:

- `-d` or `--directory`: The directory to monitor for file changes.
- `-p` or `--port`: The serial port connected to the ESP32.

Example:

```bash
python monitor.py -d ~/<directory to monitor> -p /dev/<serial device>
