# ESP32 SerialSync

This project provides a Python script to monitor a directory for file changes and upload modified files to an ESP32 board. It also maintains a serial terminal connection to the ESP32 for interacting with the REPL. It is most useful when run from a terminal in VSCode while doing your development work. It provides a seamless way of testing code in a similar manner to other IDEs that work with more modern CircuitPy devices.

## Features

- Monitors a specified directory for file changes.
- Attempts to mirror these changes to the ESP32 board using `mpremote`.
- All the while maintains a serial terminal connection for interacting with the ESP32 REPL.

## Requirements

- Python 3.x
- `pyserial`
- `watchdog`
- `mpremote`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/oddomatik/ESP32-SerialSync.git
    cd ESP32-SerialSync
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
python serialsync.py -d ~/<directory to monitor> -p /dev/<serial device>
