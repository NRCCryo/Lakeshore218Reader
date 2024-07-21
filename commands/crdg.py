import logging

def query_celsius_reading(controller, input_channel):
    response = controller.send_command(f'CRDG? {input_channel}')
    return parse_temperature_response(response)

def parse_temperature_response(response):
    print(f"Attempting to parse response: {response}")  # Debug output for parsing
    if response.startswith('+') or response.startswith('-'):
        try:
            temperature = float(response)
            print(f"Parsed temperature: {temperature}")  # Debug output for parsed temperature
            return temperature
        except ValueError:
            print(f"Error converting response to float: {response}")
            logging.error(f"Error converting response to float: {response}")
            return None
    else:
        print(f"Unexpected response format: {response}")
        logging.error(f"Unexpected response format: {response}")
        return None
