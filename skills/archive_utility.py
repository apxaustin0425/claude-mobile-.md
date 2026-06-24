import os
import zipfile
from datetime import datetime


def backup_and_clean(target_dir, output_zip_name):
    """Scan a directory, bundle text/log/json/md files, compress into a timestamped archive."""
    if not os.path.exists(target_dir):
        return f"Error: Target directory '{target_dir}' does not exist."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_zip = f"{output_zip_name}_{timestamp}.zip"

    try:
        count = 0
        with zipfile.ZipFile(final_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(target_dir):
                # skip hidden dirs and the output zip itself
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for file in files:
                    if file.endswith((".txt", ".log", ".json", ".md")):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, target_dir)
                        zipf.write(file_path, arcname)
                        count += 1
        size_kb = os.path.getsize(final_zip) // 1024
        return f"[OK] {final_zip} — {count} files, {size_kb} KB"
    except Exception as e:
        return f"[FAIL] {e}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Archive text/log/json/md files from a directory.")
    parser.add_argument("target_dir", nargs="?", default=".", help="Directory to archive (default: .)")
    parser.add_argument("--name", default="workspace_backup", help="Output zip base name")
    args = parser.parse_args()

    print(backup_and_clean(args.target_dir, args.name))
