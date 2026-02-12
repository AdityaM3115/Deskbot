def classify_command(text):
    """
    Classifies user input into:
    - app
    - file
    - utility
    - exit
    - ai
    """

    text = text.lower().strip()

    # ---------------- EXIT COMMANDS ----------------
    if text in ["exit", "quit", "stop", "shutdown"]:
        return "exit"

    # ---------------- APP COMMANDS ----------------
    app_actions = ["open", "launch", "start", "close"]
    app_names = ["chrome", "notepad", "calculator", "explorer"]

    if any(action in text for action in app_actions):
        if any(app in text for app in app_names):
            return "app"

    # ---------------- FILE COMMANDS ----------------
    file_phrases = [
        "create file",
        "create folder",
        "make folder",
        "rename file",
        "rename folder",
        "move file",
        "copy file"
    ]

    if any(phrase in text for phrase in file_phrases):
        return "file"

    # ---------------- UTILITY COMMANDS ----------------
    # Timer
    if any(word in text for word in ["set timer", "start timer"]):
        return "utility"

    # Stopwatch
    if any(word in text for word in ["start stopwatch", "stop stopwatch", "reset stopwatch"]):
        return "utility"

    # Reminder
    if "remind me" in text:
        return "utility"

    # ---------------- SYSTEM CONTROL (Future Safe Placeholder) ----------------
    if any(word in text for word in ["scroll", "volume", "mute", "screenshot"]):
        return "system"

    # ---------------- DEFAULT ----------------
    return "ai"
