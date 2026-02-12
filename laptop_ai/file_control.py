import os
import shutil


# ---------------- SAFE DIRECTORIES ----------------
def get_safe_directories():
    home = os.path.expanduser("~")

    return {
        "desktop": [
            os.path.join(home, "Desktop"),
            os.path.join(home, "OneDrive", "Desktop")
        ],
        "downloads": [
            os.path.join(home, "Downloads"),
            os.path.join(home, "OneDrive", "Downloads")
        ]
    }


def resolve_safe_path(location_name):
    safe_dirs = get_safe_directories()
    location_name = location_name.lower()

    if location_name in safe_dirs:
        for path in safe_dirs[location_name]:
            if os.path.exists(path):
                return path

    return None


# ---------------- CREATE FILE ----------------
def create_file(file_type, file_name, location="desktop"):
    EXTENSIONS = {
        "text": ".txt",
        "word": ".docx",
        "excel": ".xlsx"
    }

    if file_type not in EXTENSIONS:
        return "Unsupported file type."

    base_path = resolve_safe_path(location)
    if not base_path:
        return "Invalid location."

    full_name = file_name + EXTENSIONS[file_type]
    target_path = os.path.join(base_path, full_name)

    try:
        with open(target_path, "w") as f:
            f.write("")
        return f"{file_type} file {full_name} created in {location}."
    except Exception as e:
        return f"File creation failed: {str(e)}"


# ---------------- CREATE FOLDER ----------------
def create_folder(folder_name, location="desktop"):
    base_path = resolve_safe_path(location)
    if not base_path:
        return "Invalid location."

    target_path = os.path.join(base_path, folder_name)

    try:
        os.makedirs(target_path, exist_ok=True)
        return f"Folder {folder_name} created in {location}."
    except Exception as e:
        return f"Folder creation failed: {str(e)}"


# ---------------- FIND FILE WITH ANY EXTENSION ----------------
def find_file_with_extension(base_path, name_without_ext):
    for file in os.listdir(base_path):
        name, ext = os.path.splitext(file)
        if name.lower() == name_without_ext.lower():
            return file
    return None


# ---------------- RENAME FILE ----------------
def rename_file_keep_extension(old_name, new_name):
    safe_dirs = get_safe_directories()

    for location in safe_dirs:
        base_path = resolve_safe_path(location)
        if not base_path:
            continue

        existing_file = find_file_with_extension(base_path, old_name)
        if existing_file:
            name, ext = os.path.splitext(existing_file)

            old_path = os.path.join(base_path, existing_file)
            new_filename = new_name + ext
            new_path = os.path.join(base_path, new_filename)

            try:
                os.rename(old_path, new_path)
                return f"Renamed {existing_file} to {new_filename}."
            except Exception as e:
                return f"Rename failed: {str(e)}"

    return "File not found."


# ---------------- RENAME FOLDER ----------------
def rename_folder(old_name, new_name):
    safe_dirs = get_safe_directories()

    for location in safe_dirs:
        base_path = resolve_safe_path(location)
        if not base_path:
            continue

        old_path = os.path.join(base_path, old_name)
        new_path = os.path.join(base_path, new_name)

        if os.path.exists(old_path) and os.path.isdir(old_path):
            try:
                os.rename(old_path, new_path)
                return f"Renamed folder {old_name} to {new_name}."
            except Exception as e:
                return f"Folder rename failed: {str(e)}"

    return "Folder not found."


# ---------------- COPY FILE ----------------
def copy_file_keep_extension(file_name, destination="downloads"):
    safe_dirs = get_safe_directories()

    for location in safe_dirs:
        base_path = resolve_safe_path(location)
        if not base_path:
            continue

        existing_file = find_file_with_extension(base_path, file_name)
        if existing_file:
            source_path = os.path.join(base_path, existing_file)

            destination_path = resolve_safe_path(destination)
            if not destination_path:
                return "Invalid destination."

            try:
                shutil.copy(source_path, destination_path)
                return f"Copied {existing_file} to {destination}."
            except Exception as e:
                return f"Copy failed: {str(e)}"

    return "File not found."


# ---------------- MOVE FILE ----------------
def move_file_keep_extension(file_name, destination="downloads"):
    safe_dirs = get_safe_directories()

    for location in safe_dirs:
        base_path = resolve_safe_path(location)
        if not base_path:
            continue

        existing_file = find_file_with_extension(base_path, file_name)
        if existing_file:
            source_path = os.path.join(base_path, existing_file)

            destination_path = resolve_safe_path(destination)
            if not destination_path:
                return "Invalid destination."

            try:
                shutil.move(source_path, destination_path)
                return f"Moved {existing_file} to {destination}."
            except Exception as e:
                return f"Move failed: {str(e)}"

    return "File not found."
