# NEMO: AI-Assisted DeskBot

An AI assistant that works alongside you on your PC. You control apps, files, and tasks in natural language, by voice or through a desktop window. A Raspberry Pi companion bot connects to the laptop.

Research paper: [ieeexplore.ieee.org/document/11702064](https://ieeexplore.ieee.org/document/11702064)

## Features

- Natural-language and voice control of apps, files, and tasks (Gemini)
- Speech input and spoken replies
- Desktop GUI that shows the assistant's state
- Laptop and Raspberry Pi components that communicate with each other
- TODO: confirm and list gesture mode, focus management, and reminders

## Project structure

| Path | Description |
| --- | --- |
| `app_launcher.py` | Entry point: starts the assistant in a background thread and opens the GUI |
| `gui.py` | Desktop window; shows the assistant's current state |
| `laptop_ai/` | Assistant logic that runs on the laptop |
| `pi_bot/` | Code that runs on the Raspberry Pi |
| `communication/` | Messaging between the laptop and the Pi |
| `test_speech.py` | Microphone and speech-recognition check |
| `requirements.txt` | Pinned Python dependencies |

TODO: add one line per file inside `laptop_ai/`, `pi_bot/`, and `communication/`.

## Requirements

- Windows 10 or 11 (the project uses `pywin32` and `comtypes`)
- Python 3.10 or later
- A working microphone and speakers
- A Google Gemini API key
- TODO: Raspberry Pi model, OS, and any hardware (display, motors, camera)

## Install

```bash
git clone https://github.com/AdityaM3115/Deskbot.git
cd Deskbot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configure

Create a `.env` file in the project folder (it is git-ignored, so your key stays private):

```
GEMINI_API_KEY=your-key-here
```

TODO: confirm the exact variable name the code reads.

## Run

```bash
python test_speech.py     # check your microphone first
python app_launcher.py    # start the assistant and the GUI
```

TODO: add the commands to start the Pi side and its network settings.

## Example commands

TODO: list 3 to 5 real commands the assistant handles.

## Limitations

- Windows only.
- Speech recognition needs an internet connection.
- TODO: note supported commands and network assumptions.
