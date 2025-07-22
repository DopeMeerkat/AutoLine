import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import collections
import cv2
import itertools

# Get dirname from command line arguments
if len(sys.argv) > 1:
    dirname = sys.argv[1]
else:
    print("Usage: python makeMasks_new.py <dirname>")
    print("Please provide a directory name as an argument.")
    sys.exit(1)

# Create output directory for masks in current working directory
masks_dir = os.path.join(os.getcwd(), f"{os.path.basename(dirname)}_masks")
if not os.path.exists(masks_dir):
    os.makedirs(masks_dir)
    print(f"Created masks directory: {masks_dir}")
else:
    print(f"Using existing masks directory: {masks_dir}")

groupnames = {
    '1': 'mineral',
    '2': 'ac',
    '3': 'calcein',
    '4': 'trap',
    '5': 'dapi',
    '6': 'ap',
    '7': 'edu',
    '8': 'cfo',
    '9': 'sfo',
}

# Function to extract the number prefix from filenames like '1a.png', '2b.png', etc.
def get_number_prefix(filename):
    match = re.match(r'(\d+)[a-fA-F]', filename)
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
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((5, 5), np.uint8)
            
            # Erode to remove small noise
            eroded_mask = cv2.erode(mask, kernel, iterations=2)
            # Dilate to restore the main shape
            dilated_mask = cv2.dilate(eroded_mask, kernel, iterations=3)
            
            # Find contours to get the largest connected component
            contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Sort contours by area (largest first)
                sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                # Create a new mask with only the largest contour
                clean_mask = np.zeros_like(mask)
                cv2.drawContours(clean_mask, [sorted_contours[0]], 0, 255, -1)
                
                # Use the clean mask for further processing
                mask = clean_mask
            
            # Check the number of white pixels in the cleaned mask
            white_pixels = np.count_nonzero(mask)
            total_pixels = mask.shape[0] * mask.shape[1]
            white_percentage = (white_pixels / total_pixels) * 100
            
            # Check top and bottom row pixels
            top_row = mask[0, :]
            bottom_row = mask[-1, :]
            top_white = np.count_nonzero(top_row)
            bottom_white = np.count_nonzero(bottom_row)
            top_percentage = (top_white / mask.shape[1]) * 100
            bottom_percentage = (bottom_white / mask.shape[1]) * 100
            
            # Get the group name from the dictionary or use the prefix if not found
            group_name = groupnames.get(prefix, f"group_{prefix}")
            
            # should_save = True
            should_save = (white_percentage >= 1 and 
                          top_percentage < 50 and 
                          bottom_percentage < 50)
            
            if should_save:
                # Save the mask with group name prefix in the single masks directory
                mask_filename = f"{group_name}_{file1.split('.')[0]}_{file2.split('.')[0]}.png"
                mask_path = os.path.join(masks_dir, mask_filename)
                cv2.imwrite(mask_path, mask)
                print(f"    Saved mask to {mask_path} (White: {white_percentage:.2f}%, Top: {top_percentage:.2f}%, Bottom: {bottom_percentage:.2f}%)")
            else:
                # Explain why the mask was skipped
                reason = []
                if white_percentage < 2:
                    reason.append(f"overall white percentage too low ({white_percentage:.2f}%)")
                if top_percentage >= 5:
                    reason.append(f"too many white pixels in top row ({top_percentage:.2f}%)")
                if bottom_percentage >= 5:
                    reason.append(f"too many white pixels in bottom row ({bottom_percentage:.2f}%)")
                
                print(f"    Skipping mask for {file1} and {file2} - {', '.join(reason)}")
            
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

# After processing all groups, handle special mask renaming
print("\nProcessing special mask renaming...")

# Dictionary to store masks by group with their white percentages
masks_by_group = collections.defaultdict(list)

# Scan the masks directory and organize masks by group
for filename in os.listdir(masks_dir):
    if not filename.endswith('.png'):
        continue
        
    # Extract group name and file references from filename
    parts = filename.split('_')
    if len(parts) < 3:
        continue
        
    group_name = parts[0]
    # Extract the image names without extensions (e.g., "2a", "2f")
    img1_ref = parts[1]
    img2_ref = parts[2].split('.')[0]
    
    mask_path = os.path.join(masks_dir, filename)
    
    # Read the mask to calculate the white percentage
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        print(f"  Warning: Could not read mask file {filename}")
        continue
        
    white_pixels = np.count_nonzero(mask)
    total_pixels = mask.shape[0] * mask.shape[1]
    white_percentage = (white_pixels / total_pixels) * 100
    
    # Store the mask info
    masks_by_group[group_name].append({
        'filename': filename,
        'white_percentage': white_percentage,
        'img1_ref': img1_ref,
        'img2_ref': img2_ref
    })

# Process each group to find and rename special masks
for group_name, masks in masks_by_group.items():
    # Track which masks we'll keep
    masks_to_keep = set()
    
    if len(masks) == 1:
        # For groups with only a single mask, rename it to {groupname}.png
        single_mask = masks[0]
        old_path = os.path.join(masks_dir, single_mask['filename'])
        new_name = f"{group_name}.png"
        new_path = os.path.join(masks_dir, new_name)
        
        print(f"  Group {group_name}: Single mask - renaming {single_mask['filename']} to {new_name}")
        
        # Rename the file
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(old_path, new_path)
        
        # Add this to masks we're keeping
        masks_to_keep.add(new_name)
        
    else:
        # For groups with multiple masks
        print(f"  Processing group {group_name} with {len(masks)} masks")
        
        # Sort masks by white percentage (highest first)
        sorted_masks = sorted(masks, key=lambda x: x['white_percentage'], reverse=True)
        
        # The mask with highest white percentage becomes the "low" mask
        low_mask = sorted_masks[0]
        old_low_path = os.path.join(masks_dir, low_mask['filename'])
        new_low_name = f"{group_name}.png"
        new_low_path = os.path.join(masks_dir, new_low_name)
        
        print(f"    Renaming {low_mask['filename']} to {new_low_name} (white: {low_mask['white_percentage']:.2f}%)")
        
        # Rename the file
        if os.path.exists(new_low_path):
            os.remove(new_low_path)
        os.rename(old_low_path, new_low_path)
        
        # Add to masks we're keeping
        masks_to_keep.add(new_low_name)
        
        # Find a second mask that shares the same upper line as the "low" mask
        # The "low" mask uses img1_ref as the upper line
        upper_line = low_mask['img1_ref']
        
        # Find masks that share the same upper line but are different from the "low" mask
        high_candidates = []
        for mask in masks:
            if mask['img1_ref'] == upper_line and mask['filename'] != low_mask['filename']:
                high_candidates.append(mask)
        
        if high_candidates:
            # If we found candidates, use the one with highest white percentage as "high"
            high_mask = sorted(high_candidates, key=lambda x: x['white_percentage'], reverse=True)[0]
            old_high_path = os.path.join(masks_dir, high_mask['filename'])
            new_high_name = f"{group_name}_high.png"
            new_high_path = os.path.join(masks_dir, new_high_name)
            
            print(f"    Renaming {high_mask['filename']} to {new_high_name} (white: {high_mask['white_percentage']:.2f}%)")
            
            # Rename the file
            if os.path.exists(new_high_path):
                os.remove(new_high_path)
            os.rename(old_high_path, new_high_path)
            
            # Add to masks we're keeping
            masks_to_keep.add(new_high_name)
        else:
            print(f"    Could not find a suitable high mask that shares upper line {upper_line}")
    
    # Remove all other masks in this group that aren't in our keep list
    for filename in os.listdir(masks_dir):
        if filename.startswith(f"{group_name}_") and filename not in masks_to_keep:
            # This is a mask from this group that we don't want to keep
            file_to_remove = os.path.join(masks_dir, filename)
            print(f"    Removing excess mask: {filename}")
            os.remove(file_to_remove)

print("\nSpecial mask renaming complete!")
