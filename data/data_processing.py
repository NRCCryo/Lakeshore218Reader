import csv
from collections import deque
from datetime import datetime
import logging

class DataProcessor:
    def __init__(self, batch_size=10, unit='K'):
        self.batch_size = batch_size
        self.unit = unit
        self.in_memory_data = {"coldhead1": deque(maxlen=60), "coldhead2": deque(maxlen=60)}

    def save_data(self, coldhead, data):
        self.in_memory_data[coldhead].append(data)
        logging.info(f"Data saved for {coldhead}: {data}")
        logging.info(f"Current in_memory_data for {coldhead}: {list(self.in_memory_data[coldhead])}")
        if len(self.in_memory_data[coldhead]) >= self.batch_size:
            date_str = datetime.now().strftime('%Y-%m-%d')
            serial_number = data[-1]
            filename = f"{date_str}-Coldhead{serial_number}.csv"
            headers = ['Time', f'Stage 1 Temp ({self.unit})', f'Stage 2 Temp ({self.unit})', 'State', 'Serial Number']
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if csvfile.tell() == 0:
                    writer.writerow(headers)
                writer.writerows(self.in_memory_data[coldhead])
            self.in_memory_data[coldhead].clear()
            logging.info(f"in_memory_data for {coldhead} cleared after saving to CSV.")

    def get_latest_data(self, coldhead):
        logging.info(f"Retrieving latest data for {coldhead}: {list(self.in_memory_data[coldhead])}")
        return list(self.in_memory_data[coldhead])
