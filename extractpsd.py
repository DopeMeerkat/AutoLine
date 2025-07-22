import os
import sys
import numpy as np
from psd_tools import PSDImage
from PIL import Image
# from tkinter import Tk
# from tkinter.filedialog import askopenfilename

if __name__ == '__main__':
    cwd = os.getcwd()
    
    # Check if filename is provided as command line argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        # Check if the provided path is absolute or relative
        if not os.path.isabs(filename):
            filename = os.path.join(cwd, filename)
    else:
        print("Usage: python extractpsd.py <psd_filename>")
        print("Please provide a PSD filename as an argument.")
        sys.exit(1)
        
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        sys.exit(1)
    
    dirname = os.path.dirname(filename)
    folder = os.path.join(dirname, os.path.basename(filename)[:-4])
    if not os.path.exists(folder):
        os.mkdir(folder)

    psd = PSDImage.open(filename)
    psd_width, psd_height = psd.size
    for layer in psd:
        # if layer.offset != (0, 0):
        #     print(layer.name)
        #     layer_image = layer.composite().convert('RGBA')
        #     full_image = np.zeros((psd_height, psd_width, 4), dtype=np.uint8)
        #     full_image_pil = Image.fromarray(full_image, 'RGBA')
        #     full_image_pil.paste(layer_image, layer.offset, layer_image)
        #     data = np.array(full_image_pil)

        #     full_image_pil.save(os.path.join(layersDir, '%s.png' % layer.name), format='PNG', dpi=(300, 300))
        #     np.save(os.path.join(dataDir, '%s.npy' % layer.name), data)
    # else:
        print(f"Layer: {layer.name}")
        
        # More detailed debugging information
        parent_visible = True
        if hasattr(layer, 'parent') and layer.parent is not None:
            parent_visible = layer.parent.visible
            print(f"  Parent: {layer.parent.name}, Visible: {parent_visible}")
        
        print(f"  Layer properties: Visible={layer.visible}, Parent Visible={parent_visible}, Opacity={layer.opacity if hasattr(layer, 'opacity') else 'N/A'}")
        print(f"  Offset={layer.offset}, Size={layer.size}")
        print(f"  Blend Mode={layer._record.blend_mode if hasattr(layer._record, 'blend_mode') else 'N/A'}")
        print(f"  Has Mask: {hasattr(layer, 'mask') and layer.mask is not None}")
        print(f"  Is Clipping: {hasattr(layer, 'clip') and layer.clip}")
        print(f"  Layer Kind: {type(layer).__name__}")
        layer.opacity = 255
        
        # Try to get the layer image
        try:
            layer_image = layer.composite().convert('RGBA')
            print(f"  Image size: {layer_image.size}, Mode: {layer_image.mode}")
            
            # Check if image is empty/transparent
            data_check = np.array(layer_image)
            non_zero = np.count_nonzero(data_check[:,:,3])
            print(f"  Non-transparent pixels: {non_zero}")
            if non_zero > 0:
                # print("  Warning: Layer image is completely transparent, skipping.")
                # continue
                
                full_image = np.zeros((psd_height, psd_width, 4), dtype=np.uint8)
                full_image_pil = Image.fromarray(full_image, 'RGBA')
                full_image_pil.paste(layer_image, layer.offset, layer_image)
                data = np.array(full_image_pil)
                full_image_pil = Image.fromarray(data, 'RGBA')

                full_image_pil.save(os.path.join(folder, '%s.png' % layer.name), format='PNG', dpi=(300, 300))

        except Exception as e:
            print(f"  Error compositing layer: {e}")
        # full_image_pil = Image.fromarray(data, 'RGBA')

        # full_image_pil.save(os.path.join(folder, '%s.png' % layer.name), format='PNG', dpi=(300, 300))
