from pathlib import Path
import random
import cv2
import argparse

import matplotlib.pyplot as plt

def inspect_images(root_dir, batch_name):
    image_dir = Path(root_dir, batch_name, "developed-images") 
    
    # Get a list of all image files in the directory
    image_files = [f for f in image_dir.glob("*.jpg")]

    # Randomly select 10 images
    selected_images = random.sample(image_files, 10)

    # Create a figure to display the images
    fig, axes = plt.subplots(2, 5, figsize=(12, 6))

    # Iterate over the selected images and display them
    for i, image_file in enumerate(selected_images):
        print(f"Parsing image {i + 1} of {len(selected_images)}")
        # Read the image
        image_path = image_dir / image_file
        image = cv2.imread(str(image_path))
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
    parser = argparse.ArgumentParser(description='Image inspection script')
    parser.add_argument('--root_dir', default="/mnt/research-projects/r/raatwell/longterm_images3/field-batches/", help='Batch to inspect')
    parser.add_argument('batch_name', help='Batch to inspect')
    args = parser.parse_args()
    inspect_images(args.root_dir, args.batch_name)
