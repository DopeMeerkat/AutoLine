import os
import sys
import numpy as np
from psd_tools import PSDImage
from PIL import Image
from tkinter import Tk
from tkinter.filedialog import askopenfilename

if __name__ == '__main__':
    Tk().withdraw()
    cwd = os.getcwd()
    filename = askopenfilename(initialdir=cwd, title="Select PSD file", filetypes=[("PSD files", "*.psd")])
    if not filename:
        print("No file selected.")
        sys.exit(1)
    
    filename = os.path.join(cwd, filename)
    
    dirname = os.path.dirname(filename)
    folder = os.path.join(dirname, os.path.basename(filename)[:-4])
    layersDir = os.path.join(os.path.join(folder, 'LineImages'))
    
    referenceDir = os.path.join(os.path.join(folder, 'ReferenceImages'))
    dataDir = os.path.join(os.path.join(folder, 'LineData'))
    if not os.path.exists(folder):
        os.mkdir(folder)
        os.mkdir(layersDir)
        os.mkdir(dataDir)
        os.mkdir(os.path.join(os.path.join(folder, 'Records')))
        os.mkdir(referenceDir)

    psd = PSDImage.open(filename)
    psd_width, psd_height = psd.size
    for layer in psd:
        if layer.offset != (0, 0):
            print(layer.name)
            layer_image = layer.composite().convert('RGBA')
            full_image = np.zeros((psd_height, psd_width, 4), dtype=np.uint8)
            full_image_pil = Image.fromarray(full_image, 'RGBA')
            full_image_pil.paste(layer_image, layer.offset, layer_image)
            data = np.array(full_image_pil)

            # remove all black pixels from line shapes
            black_pixels = (data[:, :, :3] == [0, 0, 0]).all(axis=-1)
            data[black_pixels] = [0, 0, 0, 0]

            # Convert all non-black and non-transparent pixels to red
            non_black_non_transparent_pixels = ~black_pixels & (data[:, :, 3] != 0)
            data[non_black_non_transparent_pixels, :3] = [255, 0, 0]

            # Iterate through data horizontally and fill in a red pixel with the most recent y value
            for x in range(data.shape[1]):
                last_y = None
                for y in range(data.shape[0]):
                    if non_black_non_transparent_pixels[y, x]:
                        last_y = y
                    elif last_y is not None:
                        data[last_y, x, :3] = [255, 0, 0]
                        data[last_y, x, 3] = 255

            full_image_pil = Image.fromarray(data, 'RGBA')

            full_image_pil.save(os.path.join(layersDir, '%s.png' % layer.name), format='PNG', dpi=(300, 300))
            np.save(os.path.join(dataDir, '%s.npy' % layer.name), data)
        else:
            print(layer.name)
            layer_image = layer.composite().convert('RGBA')
            full_image = np.zeros((psd_height, psd_width, 4), dtype=np.uint8)
            full_image_pil = Image.fromarray(full_image, 'RGBA')
            full_image_pil.paste(layer_image, layer.offset, layer_image)
            data = np.array(full_image_pil)
            full_image_pil = Image.fromarray(data, 'RGBA')

            full_image_pil.save(os.path.join(layersDir, '%s.png' % layer.name), format='PNG', dpi=(300, 300))
