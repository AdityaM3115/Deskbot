import re

def classify_command(user_input):

    lower_input = user_input.lower()

    # -------- FILE COMMANDS --------
    if any(word in lower_input for word in ["create", "rename", "copy", "move"]):
        return "file"

    # -------- SPOTIFY --------
    if re.search(r"play\s+.+\s+on\s+spotify", lower_input):
        return "app"

    # -------- YOUTUBE --------
    if re.search(r"open\s+.+\s+in\s+youtube", lower_input):
        return "app"

    # -------- GENERAL APP COMMANDS --------
    if any(word in lower_input for word in ["open", "launch", "start", "close"]):
        return "app"

    # -------- UTILITY COMMANDS --------
    if any(word in lower_input for word in [
        "timer", "remind", "stopwatch",
        "calculate", "time", "date"
    ]):
        return "utility"

    # -------- FALLBACK --------
    return "ai"
