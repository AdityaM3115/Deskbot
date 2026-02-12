import subprocess
import os
import webbrowser
import pyautogui


# ---------------- SAFE APPLICATION WHITELIST ----------------
APP_WHITELIST = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "explorer": "explorer.exe"
}


# ---------------- OPEN APPLICATION ----------------
def open_application(app_name):
    app_name = app_name.lower()

    if app_name not in APP_WHITELIST:
        return "Application not allowed."

    try:
        subprocess.Popen(APP_WHITELIST[app_name])
        return f"{app_name} opened successfully."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"


# ---------------- CLOSE ACTIVE WINDOW ----------------
def close_active_window():
    try:
        pyautogui.hotkey("alt", "f4")
        return "Closed active window."
    except Exception as e:
        return f"Failed to close window: {str(e)}"


# ---------------- OPEN WEBSITE ----------------
def open_website(site_name):
    site_name = site_name.lower()

    WEBSITE_MAP = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "gmail": "https://mail.google.com"
    }

    if site_name in WEBSITE_MAP:
        webbrowser.open(WEBSITE_MAP[site_name])
        return f"Opening {site_name}."

    if "." in site_name:
        webbrowser.open("https://" + site_name)
        return f"Opening {site_name}."

    return None


# ---------------- SAFE SYSTEM FOLDERS ----------------
def open_system_folder(folder_name):
    folder_name = folder_name.lower()
    home = os.path.expanduser("~")

    possible_paths = {
        "desktop": [
            os.path.join(home, "Desktop"),
            os.path.join(home, "OneDrive", "Desktop")
        ],
        "downloads": [
            os.path.join(home, "Downloads"),
            os.path.join(home, "OneDrive", "Downloads")
        ]
    }

    if folder_name in possible_paths:
        for path in possible_paths[folder_name]:
            if os.path.exists(path):
                os.startfile(path)
                return f"Opening {folder_name} folder."

    return None


# ---------------- OPEN CUSTOM FOLDER (AI CREATED ON DESKTOP ONLY) ----------------
def open_custom_folder(folder_name):
    folder_name = folder_name.strip()
    home = os.path.expanduser("~")

    possible_desktop_paths = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "OneDrive", "Desktop")
    ]

    for desktop_path in possible_desktop_paths:
        target_path = os.path.join(desktop_path, folder_name)

        if os.path.exists(target_path) and os.path.isdir(target_path):
            os.startfile(target_path)
            return f"Opening folder {folder_name}."

    return None
