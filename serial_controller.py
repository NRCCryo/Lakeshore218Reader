# serial_controller.py
import serial
import time
import threading
import queue
import logging

from commands import query_kelvin_reading, query_celsius_reading
from data.data_evaluation import DataEvaluator
from data.data_processing import DataProcessor
from gui import CryocoolerMonitorGUI, MainInputController
from data.csv.dump_csv_sqlite import dump_csv_to_sqlite
from data.temperature_buffer import temperature_buffer
from tkinter import TclError


# Configure logging
logging.basicConfig(filename='temperature_log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class LakeShore218SerialController:
    def __init__(self, port='COM5', unit='K', baudrate=9600, parity=serial.PARITY_ODD, bytesize=serial.SEVENBITS, stopbits=serial.STOPBITS_ONE, timeout=1):
        self.controller = MainInputController(port, baudrate, parity, bytesize, stopbits, timeout)
        self.command_queue = queue.Queue()
        self.lock = threading.Lock()
        self.unit = unit
        self.evaluator = DataEvaluator(unit)
        self.processor = DataProcessor(unit=unit)
        self.serial_numbers = {"coldhead1": "1111", "coldhead2": "2222"}  # Example serial numbers
        self.gui = CryocoolerMonitorGUI(self)
        self.collecting = threading.Event()

    def close(self):
        self.controller.close()

    def send_command(self, command):
        with self.lock:
            response = self.controller.send_command(command)
            return response

    def query_enabled_inputs(self):
        enabled_inputs = []
        for i in range(1, 9):
            if self.controller.check_input_status(i):
                enabled_inputs.append(i)
        return enabled_inputs

    def log_data(self):
        start_time = time.time()
        if self.unit == 'K':
            temperatures = {
                'coldhead1': [query_kelvin_reading(self.controller, 1), query_kelvin_reading(self.controller, 2)],
                'coldhead2': [query_kelvin_reading(self.controller, 5), query_kelvin_reading(self.controller, 6)]
            }
        else:
            temperatures = {
                'coldhead1': [query_celsius_reading(self.controller, 1), query_celsius_reading(self.controller, 2)],
                'coldhead2': [query_celsius_reading(self.controller, 5), query_celsius_reading(self.controller, 6)]
            }

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        for coldhead, temps in temperatures.items():
            if None not in temps:
                serial_number = self.serial_numbers[coldhead]
                temperature_buffer.add_data(timestamp, temps[0], temps[1], serial_number)  # Add data to the buffer
                logging.info(f"Data added to buffer: ({timestamp}, {temps[0]}, {temps[1]}, {serial_number})")
                data = self.evaluator.evaluate_data(timestamp, temps, serial_number)
                self.processor.save_data(coldhead, data)  # Save processed data to DataProcessor
                self.update_gui_safe(coldhead, temps, data[3], serial_number)  # Update the GUI
                logging.info(f'{coldhead}: {temps}')
                print(f'Logged {coldhead}: {temps}')
            else:
                logging.error(f'Error reading data for {coldhead}')
                print(f'Error reading data for {coldhead}')

        total_time = time.time() - start_time
        logging.info(f'Total execution time: {total_time:.2f} seconds')
        print(f'Total execution time: {total_time:.2f} seconds')

    def update_gui_safe(self, coldhead, temps, state, serial_number):
        try:
            self.gui.master.after(0, self.gui.update_data, coldhead, temps, state, serial_number)
        except TclError as e:
            logging.error(f"GUI update error: {e}")

    def enable_input(self, input_channel):
        self.controller.enable_input(input_channel)

    def disable_input(self, input_channel):
        self.controller.disable_input(input_channel)

    def command_processor(self):
        while True:
            command = self.command_queue.get()
            if command == 'exit':
                break
            self.send_command(command)

    def start_command_processor(self):
        threading.Thread(target=self.command_processor, daemon=True).start()

    def collection_loop(self):
        logging.info("Starting data collection loop.")
        self.collecting.set()
        try:
            while self.collecting.is_set():
                self.log_data()
                time.sleep(0.417)  # Approximately 2.4 times per second
        except Exception as e:
            logging.error(f"Exception in collection loop: {e}")
        finally:
            self.collecting.clear()
            logging.info("Data collection loop has ended.")

    def start_collection(self):
        self.start_command_processor()
        threading.Thread(target=self.collection_loop, daemon=True).start()

    def stop_collection(self):
        logging.info("Stopping data collection.")
        self.collecting.clear()

    def dump_data_to_csv_and_db(self):
        try:
            log_file = dump_csv_to_sqlite(log_filename='dump_log_master.csv')
            print(f"CSV dump completed successfully. Log file updated: {log_file}")
        except Exception as e:
            print(f"An error occurred during CSV dump: {e}")
            logging.error(f"An error occurred during CSV dump: {e}")

if __name__ == '__main__':
    port = 'COM5'
    controller = LakeShore218SerialController(port)
    controller.gui.master.mainloop()
