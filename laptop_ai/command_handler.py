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

    # -------- EXIT --------
    if text in ["exit", "quit", "stop", "shutdown"]:
        return "exit"

    # -------- OPEN / CLOSE (App Layer) --------
    if text.startswith("open") or " open " in text:
        return "app"

    if "close" in text:
        return "app"

    # -------- FILE --------
    if any(phrase in text for phrase in [
        "create file",
        "create folder",
        "make folder",
        "rename file",
        "rename folder",
        "move file",
        "copy file"
    ]):
        return "file"

    # -------- UTILITY --------
    if any(phrase in text for phrase in [
        "set timer",
        "start timer",
        "start stopwatch",
        "stop stopwatch",
        "reset stopwatch"
    ]):
        return "utility"

    if "remind me" in text:
        return "utility"

    # -------- DEFAULT --------
    return "ai"
