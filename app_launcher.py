import threading
from laptop_ai import assistant
import gui


def start_assistant():
    assistant.main(gui.update_gui_state,)

if __name__ == "__main__":
    threading.Thread(target=start_assistant, daemon=True).start()
    gui.root.mainloop()
