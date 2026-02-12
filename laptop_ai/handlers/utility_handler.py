import re
from logger import log_info
from utility_control import (
    start_timer,
    start_stopwatch,
    stop_stopwatch,
    set_reminder,
    get_current_time,
    get_current_date,
    calculate_expression
)


def handle_utility_command(lower_input):

    # TIMER
    match = re.search(r"set\s+timer\s+(\d+)\s*(seconds|second|minutes|minute)?", lower_input)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        duration = number * 60 if unit and "minute" in unit else number
        log_info(f"Timer set for {duration} seconds.")
        return start_timer(duration)

    # REMINDER
    match = re.search(r"remind\s+me\s+in\s+(\d+)\s*(seconds|second|minutes|minute)\s+to\s+(.+)", lower_input)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        message = match.group(3)
        duration = number * 60 if "minute" in unit else number
        log_info(f"Reminder set for {duration} seconds: {message}")
        return set_reminder(duration, message)

    # STOPWATCH
    if "start stopwatch" in lower_input:
        log_info("Stopwatch started.")
        return start_stopwatch()

    if "stop stopwatch" in lower_input:
        log_info("Stopwatch stopped.")
        return stop_stopwatch()

    # TIME & DATE
    if "time" in lower_input:
        return get_current_time()

    if "date" in lower_input:
        return get_current_date()

    # CALCULATOR
    match = re.search(r"calculate\s+(.+)", lower_input)
    if match:
        expression = match.group(1)
        log_info(f"Calculator expression: {expression}")
        return calculate_expression(expression)

    return "Utility command not recognized."
