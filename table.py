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
dir = os.path.join(cwd, 'images', 'CCC_K10_F3_L1_crop')
# print(dir)

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

# # Create a new DataFrame with the new columns
# new_df = pd.DataFrame(columns=new_columns)

# # Save the new DataFrame to a new CSV file
# new_df.to_csv('new_template.csv', index=False)



