import tkinter as tk
import customtkinter as ctk
import logging
from data.data_processing import DataProcessor
from data.data_evaluation import DataEvaluator
from data.temperature_buffer import temperature_buffer


class CalculationWindow:
    def __init__(self, data_evaluator, buffer):
        self.data_evaluator = data_evaluator
        self.buffer = buffer
        self.master = ctk.CTkToplevel()
        self.master.title("Calculation Window")

        self.create_widgets()
        self.perform_calculations()

    def create_widgets(self):
        self.result_text = ctk.CTkTextbox(self.master)
        self.result_text.pack(expand=True, fill='both')

        self.calc_button = ctk.CTkButton(self.master, text="Perform Calculations", command=self.perform_calculations)
        self.calc_button.pack()

    def perform_calculations(self):
        data = self.buffer.get_data()
        logging.info(f"Data from buffer: {data}")

        if not data:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No data available.")
            return

        # Ensure the serial number is preserved
        evaluated_data = [(entry[0], *self.data_evaluator.evaluate_data(entry[0], entry[1:], ""), entry[-1]) for entry in data]
        logging.info(f"Evaluated data: {evaluated_data}")

        result = self.calculate_statistics(evaluated_data)
        logging.info(f"Calculated statistics: {result}")

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        print(result)  # Debug output to verify if the result is being calculated

    def calculate_statistics(self, evaluated_data):
        if not evaluated_data:
            return "No data available for calculations."

        stats = {'coldhead1': {'stage1': [], 'stage2': []}, 'coldhead2': {'stage1': [], 'stage2': []}}

        for data in evaluated_data:
            if data[-1] == '1111':  # coldhead1
                stats['coldhead1']['stage1'].append(data[2])
                stats['coldhead1']['stage2'].append(data[3])
            elif data[-1] == '2222':  # coldhead2
                stats['coldhead2']['stage1'].append(data[2])
                stats['coldhead2']['stage2'].append(data[3])

        def calc_stats(temps):
            if not temps:
                return {'min': float('inf'), 'max': float('-inf'), 'avg': 0, 'std_dev': 0}
            temps = [float(temp) for temp in temps]
            min_temp = min(temps)
            max_temp = max(temps)
            avg_temp = sum(temps) / len(temps)
            variance = sum((t - avg_temp) ** 2 for t in temps) / len(temps)
            std_dev = variance ** 0.5
            return {'min': min_temp, 'max': max_temp, 'avg': avg_temp, 'std_dev': std_dev}

        coldhead1_stats = {
            'stage1': calc_stats(stats['coldhead1']['stage1']),
            'stage2': calc_stats(stats['coldhead1']['stage2'])
        }

        coldhead2_stats = {
            'stage1': calc_stats(stats['coldhead2']['stage1']),
            'stage2': calc_stats(stats['coldhead2']['stage2'])
        }

        return (
            f"Coldhead1:\n1st Stage:\n Min: {coldhead1_stats['stage1']['min']:.2f} K\n Max: {coldhead1_stats['stage1']['max']:.2f} K\n Avg: {coldhead1_stats['stage1']['avg']:.2f} K\n Std Dev: {coldhead1_stats['stage1']['std_dev']:.2f} K\n"
            f"2nd Stage:\n Min: {coldhead1_stats['stage2']['min']:.2f} K\n Max: {coldhead1_stats['stage2']['max']:.2f} K\n Avg: {coldhead1_stats['stage2']['avg']:.2f} K\n Std Dev: {coldhead1_stats['stage2']['std_dev']:.2f} K\n\n"
            f"Coldhead2:\n1st Stage:\n Min: {coldhead2_stats['stage1']['min']:.2f} K\n Max: {coldhead2_stats['stage1']['max']:.2f} K\n Avg: {coldhead2_stats['stage1']['avg']:.2f} K\n Std Dev: {coldhead2_stats['stage1']['std_dev']:.2f} K\n"
            f"2nd Stage:\n Min: {coldhead2_stats['stage2']['min']:.2f} K\n Max: {coldhead2_stats['stage2']['max']:.2f} K\n Avg: {coldhead2_stats['stage2']['avg']:.2f} K\n Std Dev: {coldhead2_stats['stage2']['std_dev']:.2f} K\n")

if __name__ == '__main__':
    data_evaluator = DataEvaluator(unit='K')
    window = CalculationWindow(data_evaluator, temperature_buffer)
    window.master.mainloop()
