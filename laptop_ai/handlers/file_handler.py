import re
from logger import log_info
from file_control import (
    create_folder,
    create_file,
    rename_file_keep_extension,
    rename_folder,
    copy_file_keep_extension,
    move_file_keep_extension
)


def handle_file_command(lower_input):

    # CREATE FILE
    match = re.search(r"create\s+(text|word|excel)\s+file\s+(?:called\s+|named\s+)?(\w+)", lower_input)
    if match:
        log_info(f"Creating file: {match.group(2)} ({match.group(1)})")
        return create_file(match.group(1), match.group(2))

    # CREATE FOLDER
    match = re.search(r"create\s+folder\s+(?:called\s+|named\s+)?(\w+)", lower_input)
    if match:
        log_info(f"Creating folder: {match.group(1)}")
        return create_folder(match.group(1))

    # RENAME FILE
    match = re.search(r"rename\s+file\s+(\w+)\s+to\s+(\w+)", lower_input)
    if match:
        log_info(f"Renaming file: {match.group(1)} to {match.group(2)}")
        return rename_file_keep_extension(match.group(1), match.group(2))

    # RENAME FOLDER
    match = re.search(r"rename\s+folder\s+(\w+)\s+to\s+(\w+)", lower_input)
    if match:
        log_info(f"Renaming folder: {match.group(1)} to {match.group(2)}")
        return rename_folder(match.group(1), match.group(2))

    # COPY FILE
    match = re.search(r"copy\s+file\s+(\w+)", lower_input)
    if match:
        log_info(f"Copying file: {match.group(1)}")
        return copy_file_keep_extension(match.group(1))

    # MOVE FILE
    match = re.search(r"move\s+file\s+(\w+)", lower_input)
    if match:
        log_info(f"Moving file: {match.group(1)}")
        return move_file_keep_extension(match.group(1))

    return "File command not recognized."
