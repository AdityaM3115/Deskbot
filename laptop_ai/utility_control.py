import threading
import time
from datetime import datetime
import re

stopwatch_start_time = None


# ---------------- TIMER ----------------
def start_timer(duration_seconds, speak_function):
    def timer_thread():
        time.sleep(duration_seconds)
        speak_function("Time is up.")

    thread = threading.Thread(target=timer_thread)
    thread.daemon = True
    thread.start()

    return f"Timer set for {duration_seconds} seconds."


# ---------------- STOPWATCH ----------------
def start_stopwatch():
    global stopwatch_start_time
    stopwatch_start_time = time.time()
    return "Stopwatch started."


def stop_stopwatch():
    global stopwatch_start_time

    if stopwatch_start_time is None:
        return "Stopwatch is not running."

    elapsed = int(time.time() - stopwatch_start_time)
    stopwatch_start_time = None

    return f"Stopwatch stopped. Elapsed time: {elapsed} seconds."


# ---------------- REMINDER ----------------
def set_reminder(duration_seconds, message, speak_function):
    def reminder_thread():
        time.sleep(duration_seconds)
        speak_function(f"Reminder: {message}")

    thread = threading.Thread(target=reminder_thread)
    thread.daemon = True
    thread.start()

    return f"Reminder set for {duration_seconds} seconds."


# ---------------- CURRENT TIME ----------------
def get_current_time():
    now = datetime.now()
    return now.strftime("Current time is %I:%M %p.")


# ---------------- CURRENT DATE ----------------
def get_current_date():
    today = datetime.now()
    return today.strftime("Today is %B %d, %Y.")


# ---------------- SAFE CALCULATOR ----------------
def calculate_expression(expression):
    try:
        expression = expression.lower()

        # Replace spoken words
        expression = expression.replace("plus", "+")
        expression = expression.replace("minus", "-")
        expression = expression.replace("times", "*")
        expression = expression.replace("multiplied by", "*")
        expression = expression.replace("divided by", "/")
        expression = expression.replace("x", "*")

        # Remove unwanted characters (allow only digits and operators)
        if not re.fullmatch(r"[0-9+\-*/. ]+", expression):
            return "Invalid expression."

        # Split into tokens
        tokens = expression.split()

        # Only support simple binary operations: number operator number
        if len(tokens) == 3:
            num1 = float(tokens[0])
            operator = tokens[1]
            num2 = float(tokens[2])

            if operator == "+":
                result = num1 + num2
            elif operator == "-":
                result = num1 - num2
            elif operator == "*":
                result = num1 * num2
            elif operator == "/":
                if num2 == 0:
                    return "Cannot divide by zero."
                result = num1 / num2
            else:
                return "Unsupported operation."

            return f"The answer is {result}."

        else:
            return "Please use format: calculate 5 plus 7."

    except:
        return "I could not calculate that."
