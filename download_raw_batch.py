#import cv2
#import numpy as np
#from PIL import Image
#import imageio
#import glob
#import ntpath
#import time
import os
from pathlib import Path
import shutil
#from scipy import ndimage
#from skimage.measure import label   
import sys
import subprocess
from typing import List
from tqdm import tqdm
#import json
#import pandas as pd
#from detectclass import YoloDetectClass
#from concurrent.futures import ThreadPoolExecutor
#import signal

#executor = ThreadPoolExecutor(max_workers=16)
#futures = []

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))


assert (len(sys.argv) > 1)
    
batch_name = sys.argv[1]


def download_from_azure(batch_name):
    export_dir = "/home/psa_images/temp_data/field_data/"# + str(batch_name)
    os.makedirs(export_dir, exist_ok=True)
    exe_command = f"/home/psa_images/field_tools/azcopy copy \
        'https://weedsimagerepo.blob.core.windows.net/field-batches/{batch_name}/?sp=rl&st=2024-05-05T08:29:37Z&se=2025-05-05T16:29:37Z&spr=https&sv=2022-11-02&sr=c&sig=7QENpF2Km7R90NuK6guUSULYR9PlB6xhqylupWBZF2M%3D' \
        {export_dir} \
        --recursive \
        --overwrite=false"
        
    print(exe_command)
    try:
        # Run the rawtherapee command
        #subprocess.run(['/bin/bash', '-i', '-c', exe_command])
        #process_id = subprocess.run(exe_command, shell=True, check=True)
        process_id = subprocess.run(exe_command, shell=True, check=True)
        #subprocess.check_output(['/home/psa_images/semifield_tools/azcopy', 'copy', export_dir, 'https://weedsimagerepo.blob.core.windows.net/semifield-developed-images/?sp=racwl&st=2022-09-01T14:14:56Z&se=2024-09-02T04:14:56Z&sv=2021-06-08&sr=c&sig=KQRwEkoPFhHaq2OMpLiqxfkYLjaJso4Nje2MLHdmwJg%3D', '--recursive', '--overwrite=true'])
        print("")
    except Exception as e:
        raise e
    #os.killpg(os.getpgid(process_id.pid), signal.SIGKILL)
    #process_id.wait()
    print("Raw data has been downloaded for batch " + str(batch_name))
    subprocess.call(['chmod', '-R', '777', export_dir + str(batch_name)])


def find_unprocessed_files(batch_name: str) -> List[Path]:
    raw_dir = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches") / batch_name / "raws"
    raw_imgs = list(raw_dir.rglob("*.ARW"))

    batch_developed = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches") / batch_name / "developed-images"
    developed_imgs = sorted(batch_developed.glob("*.jpg"))
    developed_img_stems = {img.stem for img in developed_imgs}

    unprocessed_files = [img for img in raw_imgs if img.stem not in developed_img_stems]
    return unprocessed_files

def download_from_nfs(batch_name):
    # Path where batch is stored in the NFS-mounted directory
    unprocessed_files = find_unprocessed_files(batch_name)

    if not unprocessed_files:
        print(f"No unprocessed files found for batch {batch_name}. Exiting.")
        return
    
    # Local path to copy data to
    export_dir = Path("/home/psa_images/temp_data/field_data", batch_name)
    export_dir.mkdir(parents=True, exist_ok=True)

    # Code to copy here

    for src_file in tqdm(unprocessed_files, desc="Copying files"):
        relative_path = src_file.relative_to(src_file.parents[2])  # preserves relative path within batch/raws/
        dest_file = export_dir / relative_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
    # Set permissions if needed
    subprocess.call(['chmod', '-R', '777', export_dir])
    print(f"Raw data has been downloaded for batch {batch_name}")

if __name__ == "__main__":
    # download_from_azure(batch_name)
    download_from_nfs(batch_name)