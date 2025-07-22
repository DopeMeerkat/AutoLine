import os
import re
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import collections
import cv2
import itertools

dirname = 'CCC_K10_F1_L1_AlexTress'
# Create output directory for masks
masks_dir = os.path.join(dirname, 'masks')
if not os.path.exists(masks_dir):
    os.makedirs(masks_dir)

groupnames = {
    '1': 'mineral',
    '2': 'ap',
    '3': 'three',
    '4': 'BP',
    '5': 'CP',
    '6': 'DP',
    '7': 'EP',
}

# Function to extract the number prefix from filenames like '1a.png', '2b.png', etc.
def get_number_prefix(filename):
    match = re.match(r'(\d+)[a-zA-Z]', filename)
    if match:
        return match.group(1)
    return None

# Dictionary to hold groups of files with the same number prefix
file_groups = collections.defaultdict(list)

# Loop through all files in the directory
print(f"Scanning directory: {dirname}")
for filename in os.listdir(dirname):
    # Skip directories and non-image files
    file_path = os.path.join(dirname, filename)
    if os.path.isdir(file_path):
        continue
    
    # Check if it matches our pattern (number followed by letter)
    number_prefix = get_number_prefix(filename)
    if number_prefix:
        file_groups[number_prefix].append(filename)

# Process each group and create masks for each combination
for prefix, files in sorted(file_groups.items(), key=lambda x: int(x[0])):
    print(f"Processing Group {prefix}:")
    files = sorted(files)
    
    # Get all combinations of 2 files within this group
    file_combinations = list(itertools.combinations(files, 2))
    print(f"  Found {len(file_combinations)} combinations")
    
    # Create output directory for this group
    group_masks_dir = os.path.join(masks_dir, f"group_{prefix}")
    if not os.path.exists(group_masks_dir):
        os.makedirs(group_masks_dir)
    
    # Process each combination
    for i, (file1, file2) in enumerate(file_combinations):
        print(f"  Processing combination {i+1}/{len(file_combinations)}: {file1} and {file2}")
        
        # Load images
        img1_path = os.path.join(dirname, file1)
        img2_path = os.path.join(dirname, file2)
        
        img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
        
        if img1 is None or img2 is None:
            print(f"    Error loading images: {img1_path} or {img2_path}")
            continue
            
        try:
            # Find non-zero regions in both images
            _, img1_range = np.where(img1 > 0)
            _, img2_range = np.where(img2 > 0)
            
            if len(img1_range) == 0 or len(img2_range) == 0:
                print(f"    Error: One of the images has no non-zero pixels")
                continue
                
            # Find common x-range
            min_x = max(min(img1_range), min(img2_range))
            max_x = min(max(img1_range), max(img2_range))
            
            # Create modified versions that only have the common x-range
            img1_mod = np.zeros(img1.shape)
            img2_mod = np.zeros(img2.shape)
            img1_mod[:, min_x:max_x] = img1[:, min_x:max_x]
            img2_mod[:, min_x:max_x] = img2[:, min_x:max_x]
            
            # Create mask where img1 > img2
            mask = np.zeros(img1.shape)
            mask = np.where(img1_mod - img2_mod > 0, 255, 0).astype(np.uint8)
            
            # Check the number of white pixels in the mask
            white_pixels = np.count_nonzero(mask)
            total_pixels = mask.shape[0] * mask.shape[1]
            white_percentage = (white_pixels / total_pixels) * 100
            
            # Filter masks: only save if between 5% and 20% of the image is white
            if 1 <= white_percentage <= 100:
                # Save the mask
                mask_filename = f"mask_{file1.split('.')[0]}_{file2.split('.')[0]}.png"
                mask_path = os.path.join(group_masks_dir, mask_filename)
                cv2.imwrite(mask_path, mask)
                print(f"    Saved mask to {mask_path} (White pixels: {white_percentage:.2f}%)")
            else:
                print(f"    Skipping mask for {file1} and {file2} - white percentage: {white_percentage:.2f}% is outside filter range (5-20%)")
            
            print(f"    Saved mask to {mask_path}")
            
            # Optional: Display the mask (uncomment if needed)
            # plt.figure(figsize=(10, 5))
            # plt.subplot(1, 3, 1)
            # plt.imshow(img1, 'gray')
            # plt.title(file1)
            # plt.subplot(1, 3, 2)
            # plt.imshow(img2, 'gray')
            # plt.title(file2)
            # plt.subplot(1, 3, 3)
            # plt.imshow(mask, 'gray')
            # plt.title('Mask')
            # plt.tight_layout()
            # plt.show()
            
        except Exception as e:
            print(f"    Error processing combination: {e}")
            continue



 