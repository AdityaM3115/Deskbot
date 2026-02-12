import re
import webbrowser
from logger import log_info
from system_control import (
    open_application,
    close_active_window,
    open_system_folder,
    open_custom_folder
)


# ---------------- SAFE HELPERS ----------------
def sanitize_text(text):
    # Allow only letters, numbers, and spaces
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    return cleaned.strip()


def open_generic_website(site_name):
    site_name = sanitize_text(site_name)

    if not site_name:
        return "Invalid website name."

    url = f"https://www.{site_name}.com"
    log_info(f"Opening website: {url}")
    webbrowser.open(url)
    return f"Opening {site_name}."


def open_youtube_search(query):
    query = sanitize_text(query)

    if not query:
        return "Invalid search query."

    search_query = query.replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={search_query}"
    log_info(f"Opening YouTube search: {query}")
    webbrowser.open(url)
    return f"Searching {query} on YouTube."


def open_spotify_search(query):
    query = sanitize_text(query)

    if not query:
        return "Invalid song name."

    search_query = query.replace(" ", "%20")
    url = f"https://open.spotify.com/search/{search_query}"
    log_info(f"Opening Spotify search: {query}")
    webbrowser.open(url)
    return f"Playing {query} on Spotify."


# ---------------- MAIN HANDLER ----------------
def handle_app_command(lower_input):

    # CLOSE ACTIVE WINDOW
    if re.search(r"close\s+(window|app)?", lower_input):
        log_info("Closing active window.")
        return close_active_window()

    # OPEN SYSTEM FOLDER
    match = re.search(r"open\s+(desktop|downloads)", lower_input)
    if match:
        log_info(f"Opening system folder: {match.group(1)}")
        return open_system_folder(match.group(1))

    # OPEN CUSTOM FOLDER
    match = re.search(r"open\s+folder\s+(\w+)", lower_input)
    if match:
        log_info(f"Opening custom folder: {match.group(1)}")
        return open_custom_folder(match.group(1))

    # OPEN APPLICATION
    match = re.search(r"(open|launch|start)\s+(chrome|notepad|calculator|explorer)", lower_input)
    if match:
        log_info(f"Opening application: {match.group(2)}")
        return open_application(match.group(2))

    # SPOTIFY PLAY
    match = re.search(r"play\s+(.+)\s+on\s+spotify", lower_input)
    if match:
        query = match.group(1)
        return open_spotify_search(query)

    # YOUTUBE SEARCH
    match = re.search(r"open\s+(.+)\s+in\s+youtube", lower_input)
    if match:
        query = match.group(1)
        return open_youtube_search(query)

    # GENERIC WEBSITE (must stay last)
    match = re.search(r"open\s+([a-zA-Z0-9]+)", lower_input)
    if match:
        site = match.group(1)

        if site not in [
            "desktop", "downloads",
            "chrome", "notepad", "calculator", "explorer"
        ]:
            return open_generic_website(site)

    return "Application, website, or folder not recognized."
