from collections import deque
import logging

class TemperatureBuffer:
    def __init__(self):
        self.buffer = deque(maxlen=100)  # Adjust maxlen as needed

    def add_data(self, timestamp, temp1, temp2, serial):
        self.buffer.append((timestamp, temp1, temp2, serial))
        logging.info(f"Data added to buffer: {(timestamp, temp1, temp2, serial)}")

    def get_data(self):
        return list(self.buffer)

temperature_buffer = TemperatureBuffer()
