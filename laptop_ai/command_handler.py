import re

FILLER_WORDS = [
    "please", "could", "you", "kindly",
    "can", "would", "the", "a", "an"
]

SYSTEM_INTENTS = {
    "file": ["create", "rename", "copy", "move"],
    "utility": ["timer", "stopwatch", "remind", "calculate", "date", "time"],
    "app": ["open", "launch", "start", "close"]
}


def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in FILLER_WORDS]
    return words


def score_intent(words, keywords):
    score = 0
    for w in words:
        if w in keywords:
            score += 1
    return score


def classify_command(text):
    words = normalize(text)

    file_score = score_intent(words, SYSTEM_INTENTS["file"])
    utility_score = score_intent(words, SYSTEM_INTENTS["utility"])
    app_score = score_intent(words, SYSTEM_INTENTS["app"])

    max_score = max(file_score, utility_score, app_score)

    if max_score == 0:
        return "ai"

    if file_score == max_score:
        return "file"

    if utility_score == max_score:
        return "utility"

    if app_score == max_score:
        return "app"

    return "ai"
