import argparse
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description="Copy field batches to temp_data")
parser.add_argument("--username", required=True)

# batch_exts = parser.parse_args().batch_extension
user = parser.parse_args().username


def get_batch_exts():
    with open("/home/weedsci/Documents/Field-Preprocessing/batches_to_download.csv", "r") as f:
        lines = f.readlines()
    batch_exts = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) >= 2:
            batch_ext = f"{parts[0]}/raws/{parts[1]}"
            batch_exts.append(batch_ext)
    return batch_exts

for batch_ext in get_batch_exts():
    print(f"Processing batch: {batch_ext}")
    source_dir = Path(f"{user}@sunny.ece.ncsu.edu:/mnt/research-projects/r/raatwell/longterm_images3/field-batches/{batch_ext}")
    dest_dir = Path(f"temp_data/new_batches/{batch_ext}").parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Syncing from {source_dir} to {dest_dir}...")
    subprocess.run([
        "rsync",
        "-avz",
        "--progress",
        str(source_dir),
        str(dest_dir)
    ])
