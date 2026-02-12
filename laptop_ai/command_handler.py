def classify_command(text):
    text = text.lower().strip()

    # Exit
    if text in ["exit", "quit", "stop", "shutdown"]:
        return "exit"

    # App commands
    if text.startswith("open") or " open " in text:
        return "app"

    if "close" in text:
        return "app"

    # File commands
    if (
        "create" in text and "file" in text
    ) or "create folder" in text \
       or "rename file" in text \
       or "rename folder" in text \
       or "copy file" in text \
       or "move file" in text:
        return "file"

    # Utility commands (future)
    if "timer" in text or "stopwatch" in text or "remind me" in text:
        return "utility"

    return "ai"
