# gui/input_controller.py
import serial


class LakeShore218InputController:
    def __init__(self, port, baudrate=9600, parity=serial.PARITY_ODD, bytesize=serial.SEVENBITS,
                 stopbits=serial.STOPBITS_ONE, timeout=1):
        self.ser = serial.Serial(port, baudrate=baudrate, parity=parity, bytesize=bytesize, stopbits=stopbits,
                                 timeout=timeout)

    def close(self):
        self.ser.close()

    def send_command(self, command):
        self.ser.flushInput()  # Flush any previous data in the input buffer
        self.ser.write((command + '\r\n').encode())
        response = self.ser.readline().decode().strip()
        print(f'Sent: {command}, Received: {response}')  # Debug output
        return response

    def enable_input(self, input_channel):
        command = f'INPUT {input_channel},1'
        self.send_command(command)

    def disable_input(self, input_channel):
        command = f'INPUT {input_channel},0'
        self.send_command(command)

    def check_input_status(self, input_channel):
        command = f'INPUT? {input_channel}'
        response = self.send_command(command)
        return response == '1'
