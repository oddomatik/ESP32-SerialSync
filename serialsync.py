import os
import time
import subprocess
import threading
import serial
import sys
import termios
import tty
import select
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileSaveHandler(FileSystemEventHandler):
    def __init__(self, serial_port, base_path, ser, lock):
        self.serial_port = serial_port
        self.base_path = base_path
        self.ser = ser
        self.lock = lock

    def on_modified(self, event):
        if event.is_directory:
            return None

        file_path = event.src_path
        relative_path = os.path.relpath(file_path, self.base_path)
        self.upload_file(file_path, relative_path)

    def on_created(self, event):
        if event.is_directory:
            return None

        file_path = event.src_path
        relative_path = os.path.relpath(file_path, self.base_path)
        self.upload_file(file_path, relative_path)

    def on_deleted(self, event):
        if event.is_directory:
            return None

        file_path = event.src_path
        relative_path = os.path.relpath(file_path, self.base_path)
        self.delete_file(relative_path)

    def upload_file(self, file_path, relative_path):
        try:
            print(f"File modified/created: {relative_path}")

            with self.lock:
                # Close the serial connection
                if self.ser.is_open:
                    self.ser.close()
                    time.sleep(1)  # Allow some time for the device to settle

                # Upload the file to the device using mpremote
                result = subprocess.run(['mpremote', 'fs', 'cp', file_path, f':{relative_path}'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Uploaded {relative_path} to ESP32")
                else:
                    print(f"Error uploading {relative_path}: {result.stderr}")

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

        finally:
            # Reopen the serial connection
            if not self.ser.is_open:
                self.ser.open()
                time.sleep(1)  # Allow some time for the device to settle

    def delete_file(self, relative_path):
        try:
            print(f"File deleted: {relative_path}")

            with self.lock:
                # Close the serial connection
                if self.ser.is_open:
                    self.ser.close()
                    time.sleep(1)  # Allow some time for the device to settle

                # Delete the file from the device using mpremote
                result = subprocess.run(['mpremote', 'fs', 'rm', f':{relative_path}'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Deleted {relative_path} from ESP32")
                else:
                    print(f"Error deleting {relative_path}: {result.stderr}")

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

        finally:
            # Reopen the serial connection
            if not self.ser.is_open:
                self.ser.open()
                time.sleep(1)  # Allow some time for the device to settle

def start_serial_terminal(serial_port, lock, stop_event):
    ser = serial.Serial(serial_port, 115200, timeout=0.1)
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while not stop_event.is_set():
            with lock:
                if ser.is_open and ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    sys.stdout.write(data.decode('utf-8'))
                    sys.stdout.flush()

            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                with lock:
                    if ser.is_open:
                        ser.write(key.encode('utf-8'))
                        if key == '\n':
                            ser.write(b'\r')
    except Exception as e:
        print(f"Serial terminal error: {e}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        with lock:
            if ser.is_open:
                ser.close()

class TerminalManager:
    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

def main():
    parser = argparse.ArgumentParser(description="Monitor directory for changes and upload to ESP32, while maintaining a serial terminal connection.")
    parser.add_argument('-d', '--directory', type=str, required=True, help='Directory to monitor')
    parser.add_argument('-p', '--port', type=str, required=True, help='Serial port to use')
    
    args = parser.parse_args()

    serial_port = args.port
    base_path = os.path.expanduser(args.directory)

    ser = serial.Serial(serial_port, 115200, timeout=0.1)
    lock = threading.Lock()
    stop_event = threading.Event()

    event_handler = FileSaveHandler(serial_port, base_path, ser, lock)
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()

    terminal_thread = threading.Thread(target=start_serial_terminal, args=(serial_port, lock, stop_event))
    terminal_thread.daemon = True
    terminal_thread.start()

    try:
        with TerminalManager():
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        terminal_thread.join()
        observer.stop()
        observer.join()
        with lock:
            if ser.is_open:
                ser.close()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        stop_event.set()
        terminal_thread.join()
        observer.stop()
        observer.join()
        with lock:
            if ser.is_open:
                ser.close()
    finally:
        stop_event.set()
        terminal_thread.join()
        observer.stop()
        observer.join()
        with lock:
            if ser.is_open:
                ser.close()

if __name__ == "__main__":
    main()
