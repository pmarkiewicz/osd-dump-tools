from time import time


def time_to_milliseconds(input_time: time) -> int:
    milliseconds = (input_time.hour * 3600 + input_time.minute * 60 + input_time.second) * 1000 + input_time.microsecond / 1000
    return int(milliseconds)
