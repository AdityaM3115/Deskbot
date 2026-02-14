import threading
from laptop_ai import assistant
import gui


def update_gui_state(state, emotion="neutral"):
    gui.bot_state = state
    gui.bot_emotion = emotion
    gui.status_label.config(text=f"Status: {state.capitalize()}")


def append_output(text):
    gui.output_box.configure(state="normal")
    gui.output_box.insert("end", text + "\n")
    gui.output_box.configure(state="disabled")
    gui.output_box.see("end")


def start_assistant():
     assistant.main(update_gui_state, append_output)

if __name__ == "__main__":
    threading.Thread(target=start_assistant, daemon=True).start()
    gui.root.mainloop()


# Run assistant in background thread
threading.Thread(target=start_assistant, daemon=True).start()

# Start GUI
gui.root.mainloop()
