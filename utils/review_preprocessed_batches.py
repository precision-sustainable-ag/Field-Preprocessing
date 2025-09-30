import random
from pathlib import Path

import cv2
import matplotlib.pyplot as plt

ROOT_DIR = "temp_data"

def inspect_images(batch_name):
    image_dir = Path(ROOT_DIR, batch_name, "developed-images")     
    # Get a list of all image files in the directory
    image_files = [f for f in image_dir.glob("*.jpg")]
    # Randomly select 10 images
    selected_images = random.sample(image_files, min(len(image_files), 10))

    # Create a figure to display the images
    fig, axes = plt.subplots(2, 5, figsize=(12, 6))

    # Iterate over the selected images and display them
    for i, image_file in enumerate(selected_images):
        print(f"Parsing image {i + 1} of {len(selected_images)}")
        # Read the image
        image = cv2.imread(str(image_file))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Display the image
        ax = axes[i // 5, i % 5]
        ax.imshow(image)
        ax.axis('off')
    
    fig.suptitle(batch_name, fontsize=14, fontweight='bold')
    
    # Adjust the spacing between subplots
    plt.subplots_adjust(wspace=0.01, hspace=0.0001)
    
    # Save the figure with the name of the batch
    reviewed_batches = Path("reviewed_batches")
    reviewed_batches.mkdir(exist_ok=True)
    output_file = Path(reviewed_batches, f'{batch_name}.png')
    print("Saving figure to ", output_file)
    plt.savefig(output_file, bbox_inches='tight', dpi=200)
    print("Done saving figure.")

if __name__ == '__main__':
    inspect_images("batch_name")