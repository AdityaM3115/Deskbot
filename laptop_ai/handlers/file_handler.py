import re
from ..logger import log_info
from ..file_control import (
    create_folder,
    create_file,
    rename_file_keep_extension,
    rename_folder,
    copy_file_keep_extension,
    move_file_keep_extension
)

def handle_file_command(lower_input):

    lower_input = lower_input.strip()

    # CREATE FILE
    match = re.search(
        r"create\s+(?:a\s+)?(text|word|excel)\s+file\s+(?:called\s+|named\s+)?(\w+)",
        lower_input
    )
    if match:
        return create_file(match.group(1), match.group(2))

    # CREATE FOLDER
    match = re.search(
        r"create\s+(?:a\s+)?folder\s+(?:called\s+|named\s+)?(\w+)",
        lower_input
    )
    if match:
        return create_folder(match.group(1))

    # RENAME FILE
    match = re.search(
        r"rename\s+(?:file\s+)?(\w+)\s+to\s+(\w+)",
        lower_input
    )
    if match:
        return rename_file_keep_extension(match.group(1), match.group(2))

    # RENAME FOLDER
    match = re.search(
        r"rename\s+(?:folder\s+)?(\w+)\s+to\s+(\w+)",
        lower_input
    )
    if match:
        return rename_folder(match.group(1), match.group(2))

    # COPY FILE
    match = re.search(
        r"copy\s+(?:file\s+)?(\w+)",
        lower_input
    )
    if match:
        return copy_file_keep_extension(match.group(1))

    # MOVE FILE
    match = re.search(
        r"move\s+(?:file\s+)?(\w+)",
        lower_input
    )
    if match:
        return move_file_keep_extension(match.group(1))

    return "File command not recognized."
