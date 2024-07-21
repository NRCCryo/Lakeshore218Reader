from .krdg import query_kelvin_reading, parse_temperature_response as parse_temperature_response_krdg
from .crdg import query_celsius_reading, parse_temperature_response as parse_temperature_response_crdg

# Re-export for ease of access
__all__ = [
    "query_kelvin_reading",
    "parse_temperature_response_krdg",
    "query_celsius_reading",
    "parse_temperature_response_crdg"
]
