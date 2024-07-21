import tkinter as tk
import customtkinter as ctk
import itertools
import threading
from tkinter import messagebox
from data.calculation_window import CalculationWindow
from data.data_processing import DataProcessor
from data.data_evaluation import DataEvaluator
from data.csv.dump_csv_sqlite import dump_csv_to_sqlite
from data.temperature_buffer import temperature_buffer
import logging


class CryocoolerMonitorGUI:
    def __init__(self, controller):
        self.controller = controller
        self.master = ctk.CTk()
        self.master.title("Cryocooler Monitoring")

        self.processor = DataProcessor(unit=self.controller.unit)
        self.in_memory_data = {"coldhead1": [], "coldhead2": []}

        self.temp_unit_var = tk.StringVar(value=self.controller.unit)

        self.create_widgets()
        self.create_popups()
        self.update_gui_data()

    def create_widgets(self):
        self.create_coldhead_form(0)
        self.create_coldhead_form(1)

        unit_frame = ctk.CTkFrame(self.master)
        unit_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ctk.CTkLabel(unit_frame, text="Select Temperature Unit:").pack(anchor='w', padx=10)
        self.radio_kelvin = ctk.CTkRadioButton(unit_frame, text="Kelvin (K)", variable=self.temp_unit_var, value='K',
                                               command=self.update_unit)
        self.radio_kelvin.pack(anchor='w', padx=10)
        self.radio_celsius = ctk.CTkRadioButton(unit_frame, text="Celsius (C)", variable=self.temp_unit_var, value='C',
                                                command=self.update_unit)
        self.radio_celsius.pack(anchor='w', padx=10)

        self.btn_start = ctk.CTkButton(self.master, text="Start Collection", command=self.start_collection)
        self.btn_start.grid(row=3, column=0, pady=10, padx=5, sticky='ew')
        self.btn_stop = ctk.CTkButton(self.master, text="Stop Collection", command=self.stop_collection,
                                      state=tk.DISABLED)
        self.btn_stop.grid(row=3, column=1, pady=10, padx=5, sticky='ew')
        self.btn_test_com = ctk.CTkButton(self.master, text="Test COM Port", command=self.test_com_port)
        self.btn_test_com.grid(row=4, column=0, pady=10, padx=5, sticky='ew')
        self.btn_dump_csv = ctk.CTkButton(self.master, text="Dump CSV", command=self.dump_csv)
        self.btn_dump_csv.grid(row=4, column=1, pady=10, padx=5, sticky='ew')
        self.btn_open_calc = ctk.CTkButton(self.master, text="Open Calculation Window",
                                           command=self.open_calculation_window)
        self.btn_open_calc.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky='ew')

    def create_coldhead_form(self, row):
        frame = ctk.CTkFrame(self.master)
        frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        frame.grid_propagate(False)
        frame.configure(width=1000, height=300)

        serial_var_label = ctk.StringVar(value="Serial: Not Set")
        serial_label = ctk.CTkLabel(frame, textvariable=serial_var_label, anchor="w",
                                    font=("default_theme", 22, "bold"), text_color="blue")
        serial_label.pack(fill="x", padx=10, pady=2)

        entry_serial_var = ctk.StringVar()
        entry_serial = ctk.CTkEntry(frame, textvariable=entry_serial_var, placeholder_text="Enter Serial Number")
        entry_serial.pack(fill="x", padx=10, pady=2)
        button_serial = ctk.CTkButton(frame, text="Submit Serial",
                                      command=lambda: self.submit_serial(entry_serial_var.get(), row, serial_var_label))
        button_serial.pack(fill="x", padx=10, pady=2)

        font_settings = ("default_theme", 22, "bold")
        text_color = "black"

        label_1st_stage = ctk.CTkLabel(frame, text="1st Stage: N/A", anchor="w", font=font_settings,
                                       text_color=text_color)
        label_1st_stage.pack(fill="x", padx=10, pady=2)

        label_2nd_stage = ctk.CTkLabel(frame, text="2nd Stage: N/A", anchor="w", font=font_settings,
                                       text_color=text_color)
        label_2nd_stage.pack(fill="x", padx=10, pady=2)

        label_state = ctk.CTkLabel(frame, text="State: N/A", anchor="w", font=font_settings, text_color=text_color)
        label_state.pack(fill="x", padx=10, pady=2)

        if row == 0:
            self.serial_label_1 = serial_var_label
            self.temp_label_1 = label_1st_stage
            self.temp_label_2 = label_2nd_stage
            self.state_label_1 = label_state
        else:
            self.serial_label_2 = serial_var_label
            self.temp_label_3 = label_1st_stage
            self.temp_label_4 = label_2nd_stage
            self.state_label_2 = label_state

        self.state_change_label = ctk.CTkLabel(self.master, text="", anchor="w")
        self.state_change_label.grid(row=3 + row, column=0, padx=10, pady=10)

    def open_calculation_window(self):
        data_evaluator = DataEvaluator(unit=self.controller.unit)
        CalculationWindow(data_evaluator, temperature_buffer)

    def submit_serial(self, serial, row, serial_var_label):
        serial_var_label.set(f"Serial: {serial}")
        if row == 0:
            self.controller.serial_numbers["coldhead1"] = serial
        else:
            self.controller.serial_numbers["coldhead2"] = serial

    def create_popup(self, coldhead_name):
        coldhead_index = 1 if coldhead_name == "coldhead1" else 2

        def create_tooltip(widget, get_tooltip_text):
            def on_enter(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip_text = get_tooltip_text()
                tooltip_label = tk.Label(tooltip, text=tooltip_text, bg="lightyellow", fg="black", borderwidth=1,
                                         relief="solid")
                tooltip_label.pack()
                x = widget.winfo_rootx() + 20
                y = widget.winfo_rooty() + widget.winfo_height() + 20
                tooltip.geometry(f"+{x}+{y}")
                widget.tooltip = tooltip

            def on_leave(event):
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                    del widget.tooltip

            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        def get_temp_tooltip_text(stage_index):
            def tooltip_text():
                data_key = f'coldhead{coldhead_index}'
                recent_data = list(
                    itertools.islice(self.in_memory_data[data_key], max(0, len(self.in_memory_data[data_key]) - 60),
                                     len(self.in_memory_data[data_key])))
                if not recent_data:
                    return "No data available"
                temps = [data[stage_index] for data in recent_data]
                min_temp, max_temp = min(temps), max(temps)
                avg_temp = sum(temps) / len(temps)
                trend = "Stable"
                if len(recent_data) > 120:
                    first_half_avg = sum(temps[:60]) / 60
                    second_half_avg = sum(temps[60:]) / 60
                    trend = "Rising" if second_half_avg > first_half_avg else "Falling" if second_half_avg < first_half_avg else "Stable"
                return f"Min: {min_temp} K, Max: {max_temp} K, Avg: {avg_temp:.2f} K, Trend: {trend}"

            return tooltip_text

        popup = ctk.CTkToplevel(self.master)
        popup.title(f"{coldhead_name} Information")
        popup.geometry("400x300")

        font_settings = ("default_theme", 24, "bold")
        text_color = "red"

        label_title = ctk.CTkLabel(popup, text=coldhead_name.capitalize(), font=font_settings, text_color=text_color)
        label_title.pack(pady=10)

        label_serial = ctk.CTkLabel(popup, text="Serial: Not Set", font=("default_theme", 18))
        label_serial.pack(pady=5)

        label_1st_stage = ctk.CTkLabel(popup, text="1st Stage: N/A", font=("default_theme", 18))
        label_1st_stage.pack(pady=5)

        label_2nd_stage = ctk.CTkLabel(popup, text="2nd Stage: N/A", font=("default_theme", 18))
        label_2nd_stage.pack(pady=5)

        label_state = ctk.CTkLabel(popup, text="State: N/A", font=("default_theme", 18))
        label_state.pack(pady=5)

        if coldhead_index == 1:
            self.popup_label_serial_1 = label_serial
            self.popup_temp_label_1 = label_1st_stage
            self.popup_temp_label_2 = label_2nd_stage
            self.popup_state_label_1 = label_state
        else:
            self.popup_label_serial_2 = label_serial
            self.popup_temp_label_3 = label_1st_stage
            self.popup_temp_label_4 = label_2nd_stage
            self.popup_state_label_2 = label_state

    def create_popups(self):
        self.create_popup("coldhead1")
        self.create_popup("coldhead2")

    def update_gui_data(self):
        self.in_memory_data["coldhead1"] = self.processor.get_latest_data("coldhead1")
        self.in_memory_data["coldhead2"] = self.processor.get_latest_data("coldhead2")

        if self.in_memory_data["coldhead1"]:
            latest_coldhead1 = self.in_memory_data["coldhead1"][-1]
            self.temp_label_1.configure(text=f"1st Stage: {latest_coldhead1[1]:.2f} {self.controller.unit}")
            self.temp_label_2.configure(text=f"2nd Stage: {latest_coldhead1[2]:.2f} {self.controller.unit}")
            self.state_label_1.configure(text=f"State: {latest_coldhead1[3]}")
            self.serial_label_1.set(f"Serial: {self.controller.serial_numbers['coldhead1']}")

            self.popup_temp_label_1.configure(text=f"1st Stage: {latest_coldhead1[1]:.2f} {self.controller.unit}")
            self.popup_temp_label_2.configure(text=f"2nd Stage: {latest_coldhead1[2]:.2f} {self.controller.unit}")
            self.popup_state_label_1.configure(text=f"State: {latest_coldhead1[3]}")
            self.popup_label_serial_1.configure(text=f"Serial: {self.controller.serial_numbers['coldhead1']}")

        if self.in_memory_data["coldhead2"]:
            latest_coldhead2 = self.in_memory_data["coldhead2"][-1]
            self.temp_label_3.configure(text=f"1st Stage: {latest_coldhead2[1]:.2f} {self.controller.unit}")
            self.temp_label_4.configure(text=f"2nd Stage: {latest_coldhead2[2]:.2f} {self.controller.unit}")
            self.state_label_2.configure(text=f"State: {latest_coldhead2[3]}")
            self.serial_label_2.set(f"Serial: {self.controller.serial_numbers['coldhead2']}")

            self.popup_temp_label_3.configure(text=f"1st Stage: {latest_coldhead2[1]:.2f} {self.controller.unit}")
            self.popup_temp_label_4.configure(text=f"2nd Stage: {latest_coldhead2[2]:.2f} {self.controller.unit}")
            self.popup_state_label_2.configure(text=f"State: {latest_coldhead2[3]}")
            self.popup_label_serial_2.configure(text=f"Serial: {self.controller.serial_numbers['coldhead2']}")

        self.master.after(1000, self.update_gui_data)

    def update_data(self, coldhead, temperatures, state, serial_number):
        if coldhead == 'coldhead1':
            self.temp_label_1.configure(text=f"1st Stage: {temperatures[0]:.2f} {self.controller.unit}")
            self.temp_label_2.configure(text=f"2nd Stage: {temperatures[1]:.2f} {self.controller.unit}")
            self.state_label_1.configure(text=f"State: {state}")
            self.serial_label_1.set(f"Serial: {serial_number}")

            self.popup_temp_label_1.configure(text=f"1st Stage: {temperatures[0]:.2f} {self.controller.unit}")
            self.popup_temp_label_2.configure(text=f"2nd Stage: {temperatures[1]:.2f} {self.controller.unit}")
            self.popup_state_label_1.configure(text=f"State: {state}")
            self.popup_label_serial_1.configure(text=f"Serial: {serial_number}")
        else:
            self.temp_label_3.configure(text=f"1st Stage: {temperatures[0]:.2f} {self.controller.unit}")
            self.temp_label_4.configure(text=f"2nd Stage: {temperatures[1]:.2f} {self.controller.unit}")
            self.state_label_2.configure(text=f"State: {state}")
            self.serial_label_2.set(f"Serial: {serial_number}")

            self.popup_temp_label_3.configure(text=f"1st Stage: {temperatures[0]:.2f} {self.controller.unit}")
            self.popup_temp_label_4.configure(text=f"2nd Stage: {temperatures[1]:.2f} {self.controller.unit}")
            self.popup_state_label_2.configure(text=f"State: {state}")
            self.popup_label_serial_2.configure(text=f"Serial: {serial_number}")

    def update_unit(self):
        self.controller.unit = self.temp_unit_var.get()
        self.processor.unit = self.temp_unit_var.get()

    def start_collection(self):
        self.disable_controls()
        threading.Thread(target=self.controller.start_collection, daemon=True).start()

    def stop_collection(self):
        self.enable_controls()
        self.controller.stop_collection()

    def disable_controls(self):
        logging.info("Disabling controls.")
        self.btn_start.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.NORMAL)
        self.btn_test_com.configure(state=tk.DISABLED)
        self.btn_dump_csv.configure(state=tk.DISABLED)
        self.radio_kelvin.configure(state=tk.DISABLED)
        self.radio_celsius.configure(state=tk.DISABLED)

    def enable_controls(self):
        logging.info("Enabling controls.")
        self.btn_start.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self.btn_test_com.configure(state=tk.NORMAL)
        self.btn_dump_csv.configure(state=tk.NORMAL)
        self.radio_kelvin.configure(state=tk.NORMAL)
        self.radio_celsius.configure(state=tk.NORMAL)

    def test_com_port(self):
        try:
            self.controller.send_command("*IDN?")
            messagebox.showinfo("Info", "COM port is working correctly.")
        except Exception as e:
            messagebox.showerror("Error", f"COM port test failed: {e}")

    def dump_csv(self):
        try:
            log_file = dump_csv_to_sqlite(log_filename='dump_log_master.csv')
            messagebox.showinfo("Info", f"CSV dump completed successfully. Log file updated: {log_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during CSV dump: {e}")
