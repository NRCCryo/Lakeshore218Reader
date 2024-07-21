import csv
import logging

class CSVCapture:
    def __init__(self, filename, unit='K', batch_size=10):
        self.filename = filename
        self.unit = unit
        self.batch_size = batch_size
        self.data_batch = []
        self.headers = ['Time', f'Stage 1 Temp ({unit})', f'Stage 2 Temp ({unit})', 'State', 'Serial Number']
        self.ensure_headers()

    def ensure_headers(self):
        try:
            with open(self.filename, 'r', newline='') as file:
                reader = csv.reader(file)
                headers = next(reader)
                if headers != self.headers:
                    raise ValueError("Headers do not match")
        except (FileNotFoundError, ValueError, StopIteration):
            with open(self.filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def add_data(self, data):
        self.data_batch.append(data)
        if len(self.data_batch) >= self.batch_size:
            self.save_to_csv()
            self.data_batch.clear()

    def save_to_csv(self):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.data_batch)

    def log_data(self, data):
        logging.info(f'Logging data: {data}')
        self.add_data(data)
        logging.debug(f'Current batch size: {len(self.data_batch)}')
