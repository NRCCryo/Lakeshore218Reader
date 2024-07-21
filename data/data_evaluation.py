class DataEvaluator:
    def __init__(self, unit='K'):
        self.unit = unit

    def evaluate_state_transitions(self, current_state, temperature_data):
        temp_stage1, temp_stage2 = temperature_data[:2]

        if self.unit == 'K':
            over_temp_threshold1 = 77 * 1.10
            over_temp_threshold2 = 20 * 1.10
            no_load_threshold1 = 30 * 1.10
            no_load_threshold2 = 8 * 1.10
            load_min_stage1 = 65
            load_max_stage1 = 77 * 1.10
            load_min_stage2 = 15
            load_max_stage2 = 20 * 1.10
        else:  # Assuming unit is 'C'
            over_temp_threshold1 = 77 * 1.10 - 273.15
            over_temp_threshold2 = 20 * 1.10 - 273.15
            no_load_threshold1 = 30 * 1.10 - 273.15
            no_load_threshold2 = 8 * 1.10 - 273.15
            load_min_stage1 = 65 - 273.15
            load_max_stage1 = 77 * 1.10 - 273.15
            load_min_stage2 = 15 - 273.15
            load_max_stage2 = 20 * 1.10 - 273.15

        new_state = current_state

        if current_state in ["Idle", "Cooldown"]:
            if temp_stage1 < 290 and temp_stage2 < 290:
                new_state = "Cooldown"
            if temp_stage1 <= no_load_threshold1 and temp_stage2 <= no_load_threshold2:
                new_state = "No Load"
        elif current_state == "No Load":
            if load_min_stage1 <= temp_stage1 <= load_max_stage1 and load_min_stage2 <= load_max_stage2:
                new_state = "Load"
        elif current_state == "Load":
            if temp_stage1 > over_temp_threshold1 or temp_stage2 > over_temp_threshold2:
                new_state = "Over Temp"
        elif current_state == "Over Temp":
            if load_min_stage1 <= temp_stage1 <= load_max_stage1 and load_min_stage2 <= load_max_stage2:
                new_state = "Load"
            elif temp_stage1 <= no_load_threshold1 and temp_stage2 <= no_load_threshold2:
                new_state = "No Load"

        return new_state

    def evaluate_data(self, timestamp, temps, serial_number):
        state = self.evaluate_state_transitions("Idle", temps)  # Example of evaluating from "Idle"
        return [timestamp, temps[0], temps[1], state, serial_number]
