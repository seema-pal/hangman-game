import os
import shutil
from pathlib import Path
from datetime import datetime

# Safe test folder: original Downloads files will not be touched
BASE_DIR = Path(__file__) .parent
TARGET_DIR = BASE_DIR / "organizer_test"
LOG_FILE = BASE_DIR / "organizer_log.txt"

# File extension to folder mapping
EXTENSION_MAP = {
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".py": "code",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".html": "Code",
    ".css": "Code",
    ".js": "Code",
}

def get_unique_path(destination):
    """Avoid overwriting a file with the same name."""
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 1

    while True:
        new_path = destination.with_name(
            f"{stem}_{counter}{suffix}"
        )
        if not new_path.exists():
            return new_path
        counter += 1

def log_message(message):
    """Print and save each log entry."""
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n")

def organize_files():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    moved = 0
    skipped = 0
    errors = 0

    log_message("\n" + "=" * 45)
    log_message("FILE ORGANIZER STARTED")
    log_message(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log_message(f"Target folder: {TARGET_DIR}")
    log_message("=" * 45)

    try:
        with os.scandir(TARGET_DIR) as entries:
            files = [
                entry for entry in entries
                if entry.is_file(follow_symlinks=False)
            ]
    except PermissionError:
        log_message("ERROR: Permission denied accessing folder.")
        return
    except OSError as error:
        log_message(f"ERROR: {error}")
        return

    for entry in files:
        source = Path(entry.path)
        extension = source.suffix.lower()

        category = EXTENSION_MAP.get(extension, "Others")
        category_dir = TARGET_DIR / category

        try:
            category_dir.mkdir(parents=True, exist_ok=True)
            destination = get_unique_path(category_dir / source.name)

            shutil.move(str(source), str(destination))
            moved += 1
            log_message(
                f"MOVED: {source.name} -> "
                f"{category}/{destination.name}"
            )

        except PermissionError:
            errors += 1
            log_message(f"ERROR: Permission denied: {source.name}")

        except (OSError, shutil.Error) as error:
            errors += 1
            log_message(f"ERROR: {source.name}: {error}")

    log_message("\n" + "-" * 45)
    log_message("ORGANIZATION SUMMARY")
    log_message(f"Files moved: {moved}")
    log_message(f"Files skipped: {skipped}")
    log_message(f"Errors: {errors}")
    log_message(f"Log saved to: {LOG_FILE}")
    log_message("-" * 45)

if __name__ == "__main__":
    print("Organizer program started!")
    organize_files()