from pathlib import Path
import pandas as pd 
from typing import List, Tuple, Union
from tqdm import tqdm
from collections import defaultdict
def find_unprocessed_files(batch_name: str) -> List[Path]:
    raw_dir = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches") / batch_name / "raws"
    raw_imgs = list(raw_dir.rglob("*.ARW"))

    batch_developed = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches") / batch_name / "developed-images"
    developed_imgs = sorted(batch_developed.glob("*.jpg"))
    developed_img_stems = {img.stem for img in developed_imgs}

    unprocessed_files = [img for img in raw_imgs if img.stem not in developed_img_stems]
    return unprocessed_files

def get_batches() -> List[str]:
    batch_dir = Path("/mnt/research-projects/r/raatwell/longterm_images3/field-batches")
    batches = [d.name for d in batch_dir.iterdir() if d.is_dir()]
    return batches


def get_unprocessed_batches() -> List[Tuple[str, Path, int]]:
    """
    Returns a list of tuples (batch_name, parent_folder, number_of_unprocessed_files_in_that_folder)
    for all unprocessed .ARW files grouped by parent folder.
    """
    batches = get_batches()  # You should already have this function
    unprocessed_batches = []

    for batch in tqdm(batches, desc="Processing batches"):
        unprocessed_files = find_unprocessed_files(batch)
        if unprocessed_files:
            # Group by parent directory
            parent_folder_map = defaultdict(list)
            for img in unprocessed_files:
                parent_folder_map[img.parent].append(img)

            for parent, files in parent_folder_map.items():
                unprocessed_batches.append((batch, parent.name, len(files)))

    return unprocessed_batches
def create_pandas_df(unprocessed_batches: List[Tuple[str, Union[List[str], set], int]]) -> pd.DataFrame:
    """
    Convert list of (batch_name, subfolders, image_count) into a DataFrame.
    Ensures subfolders are ordered (converted to lists).
    """
    # Convert sets to lists

    df = pd.DataFrame(unprocessed_batches, columns=["batch", "sub_folder", "images"])

    return df

if __name__ == "__main__":
    
    """
    # Check if the script is being run directly"""

    # Get the unprocessed batches
    unprocessed_batches = get_unprocessed_batches()
    # Create a pandas DataFrame
    df = create_pandas_df(unprocessed_batches)
    df.to_csv("unprocessed_batches.csv", index=False)