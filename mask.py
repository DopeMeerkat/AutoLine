import pandas as pd
import os
import numpy as np
from PIL import Image

cwd = os.getcwd()

# filename = os.path.join(cwd, 'images', 'CCC_K10_F3_L1_crop')
filenames = ['CCC_K10_F3_L1_crop','CCC_K10_F3_L2_crop','CCC_K10_F3_L3_crop']
# linedefs = {
#     'Germinal_zone': ('01_SOGUL.npy', 'GZM.npy'),
#     'Columnar_zone': ('GZM.npy', 'CZM.npy'),
#     'Prehypertrophic_zone': ('CZM.npy', '07_D0CML.npy'),
#     'Hypertrophic_zone': ('07_D0CML.npy', '08_SOGCB.npy'),
#     'Preostegenic_Metaphyseal_zone': ('08_SOGCB.npy', '12_C5MUL.npy'),
#     'Osteogenic_Metaphyseal_zone': ('12_C5MUL.npy', '13_DPUML.npy'),
# }

# No averages
linedefs = {
    'Germinal_zone': ('01_SOGUL.npy', '02_C5GLL.npy'),
    'Columnar_zone': ('02_C5GLL.npy', '05_TRPUL.npy'),
    'Prehypertrophic_zone': ('05_TRPUL.npy', '07_D0CML.npy'),
    'Hypertrophic_zone': ('07_D0CML.npy', '08_SOGCB.npy'),
    'Preostegenic_Metaphyseal_zone': ('08_SOGCB.npy', '12_C5MUL.npy'),
    'Osteogenic_Metaphyseal_zone': ('12_C5MUL.npy', '13_DPUML.npy'),
}


def create_mask(filename, linedefs):
    # Create masks directory if it doesn't exist
    masks_dir = os.path.join(filename, 'masks')
    if not os.path.exists(masks_dir):
        os.mkdir(masks_dir)
    
    # Define the function for line detection once
    def get_line_y(line):
        # If RGBA, check alpha channel, else assume all pixels are visible
        if line.shape[2] == 4:
            mask = (line[:, :, 3] != 0)  # Any non-transparent pixel
        else:
            # For RGB, consider any non-black pixel as part of the line
            mask = ~((line[:, :, 0] == 0) & (line[:, :, 1] == 0) & (line[:, :, 2] == 0))
        y_indices = np.full(line.shape[1], -1, dtype=int)
        for x in range(line.shape[1]):
            y = np.where(mask[:, x])[0]
            if y.size > 0:
                y_indices[x] = y[0]  # Take the first visible pixel in this column
        return y_indices

    # Process each zone defined in linedefs
    for zone_name, (line1_name, line2_name) in linedefs.items():
        print(f"Processing {zone_name}...")
        
        # Load line data
        line1path = os.path.join(filename, 'LineData', line1_name)
        line2path = os.path.join(filename, 'LineData', line2_name)
        
        # Make sure files have .npy extension
        if not line1path.endswith('.npy'):
            line1path += '.npy'
        if not line2path.endswith('.npy'):
            line2path += '.npy'
        
        line1 = np.load(line1path)
        line2 = np.load(line2path)
        
        y1 = get_line_y(line1)
        y2 = get_line_y(line2)
        
        # Create an RGBA mask, initially all transparent
        mask = np.zeros((line1.shape[0], line1.shape[1], 4), dtype=np.uint8)
        
        for x in range(mask.shape[1]):
            y_start = y1[x]
            y_end = y2[x]
            if y_start == -1 or y_end == -1:
                continue
            y_min = min(y_start, y_end)
            y_max = max(y_start, y_end)
            # Set pixels in the range to white with full opacity [255, 255, 255, 255]
            mask[y_min:y_max+1, x] = [255, 255, 255, 255]

        # Save the mask with zone name
        full_image_pil = Image.fromarray(mask, 'RGBA')
        mask_filename = f"{zone_name}.png"
        full_image_pil.save(os.path.join(masks_dir, mask_filename), format='PNG', dpi=(300, 300))
        np.save(os.path.join(masks_dir, f"{zone_name}.npy"), mask)
        
        print(f"Saved mask for {zone_name}")


# create_mask(filename, linedefs)

for filename in filenames:
    create_mask(os.path.join(cwd, 'images', filename), linedefs)

