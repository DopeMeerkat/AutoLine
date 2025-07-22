import pandas as pd
import os
import sys
import csv
from tkinter import Tk
from tkinter.filedialog import askdirectory
from analysis import *

# Read the CSV file into a pandas DataFrame
cwd = os.getcwd()
df = pd.read_csv(os.path.join('template.csv'))

# Tk().withdraw()
# dir = askdirectory(initialdir=cwd, title="Select Folder")
# if not dir:
#     print("No folder selected.")
#     sys.exit(1)
dir = os.path.join(cwd, 'images', 'CCC_K10_F3_L3_crop')

def getArea(upperline, lowerline):
    x = list(range(1, upperline.shape[1]))
    y = np.zeros((upperline.shape[1],1))
    for i in x:
        line1Y = np.where(upperline[: ,i] == 1)[0]
        line2Y = np.where(lowerline[: ,i] == 1)[0]
        if line1Y.size != 0 and line2Y.size != 0:
            y[i] = np.median(line1Y) - np.median(line2Y)
        else:
            y[i] = 0

    y[y==0] = np.nan
    yFinite = np.argwhere(np.isfinite(y)) #get indexes of non NaN to find endpoints of line

    start = yFinite[0][0]
    end = yFinite[-1][0]
    y[:start] = np.nan
    y[end:] = np.nan
    mean =  abs(y[~np.isnan(y)].mean())
    sd =  y[~np.isnan(y)].std()


    # lines = upperline+lowerline
    # f, (ax1,ax2) = plt.subplots(2, 1, height_ratios=[10,4], sharex=True, figsize=(6,10))
    # ax1.imshow(lines, origin='upper', aspect='auto')
    # textstr = '\n'.join((
    # r'mean=%.2f' % (mean, ),
    # r'SD=%.2f' % (sd, )))

    # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    # ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=14,
    #         verticalalignment='top', bbox=props)

    # ax2.plot(y)
    # plt.show()

    return mean, sd


filenames = {}
for _, _, files in os.walk(os.path.join(dir, 'LineImages')):
    for file in files:
        if file.endswith('.png'):
            # print(file, file[2])
            if file[2] == '_': # if the file is named like 01_...
                filenames[int(file[0:2])] = file
            else:
                filenames[file[:-4]] = file

linenames = {}
for _, _, files in os.walk(os.path.join(dir, 'LineData')):
    for file in files:
        if file.endswith('.npy'):
            if file[2] == '_':
                linenames[int(file[0:2])] = file
            else:
                linenames[file[:-4]] = file

# print(filenames.keys())
# print(linenames.keys())


new_columns = []
for index, row in df.iterrows():
    for col in df.columns:
        if col != 'ZoneID' and row[col] != 0:
            zoneID = str(row[0])
            zoneID = zoneID.replace('\t', '')
            new_columns.append(zoneID + '_' + col.replace('\t', ''))

    upperline , lowerline = None, None
    try: # if type is str
        upperline = np.load(os.path.join(dir, 'LineData', linenames[row['Upper_Line']]))
    except:
        try:
            upperline = np.load(os.path.join(dir, 'LineData', linenames[int(row['Upper_Line'])]))
        except:
            print(f'File {row['Upper_Line'].strip()} not found')
        

    try: # if type is str
        lowerline = row['Lower_Line'].strip()
        # print(lowerline)
        sectionName = lowerline.split('=')[1]
        sectionName.strip()
        lines = lowerline.split('=')[0].split('+')
        if sectionName in linenames:
            lowerline = np.load(os.path.join(dir, 'LineData', linenames[sectionName]))
        else: lowerline = getAvg(lines, linenames, sectionName)

    except:
        try:
            lowerline = np.load(os.path.join(dir, 'LineData', linenames[int(row['Lower_Line'])]))
        except:
            print(f'File {row['Lower_Line'].strip()} not found')

    # print(row['ZoneID'], type(upperline), type(lowerline))


    # calc area
    mean, sd, left, right, = None, None, None, None
    if type(upperline) == np.ndarray and type(lowerline) == np.ndarray:
        mean, sd = getArea(upperline, lowerline)

        print(zoneID, mean, sd)


    
    

# # Create a new DataFrame with the new columns
# new_df = pd.DataFrame(columns=new_columns)

# # Save the new DataFrame to a new CSV file
# new_df.to_csv('new_template.csv', index=False)
