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
    dataDir = os.path.join(os.path.join(folder, 'LineData'))
    if not os.path.exists(folder):
        os.mkdir(folder)
        os.mkdir(layersDir)
        os.mkdir(dataDir)

    psd = PSDImage.open(filename)
    psd_width, psd_height = psd.size
    for layer in psd:
        if layer.offset != (0, 0):
            layer_image = layer.composite().convert('RGBA')
            full_image = np.zeros((psd_height, psd_width, 4), dtype=np.uint8)
            full_image_pil = Image.fromarray(full_image, 'RGBA')
            full_image_pil.paste(layer_image, layer.offset, layer_image)
            data = np.array(full_image_pil)
            black_pixels = (data[:, :, :3] == [0, 0, 0]).all(axis=-1)
            data[black_pixels] = [0, 0, 0, 0]
            full_image_pil = Image.fromarray(data, 'RGBA')

            full_image_pil.save(os.path.join(layersDir, '%s.png' % layer.name), format='PNG', dpi=(300, 300))
            np.save(os.path.join(dataDir, '%s.npy' % layer.name), data)
