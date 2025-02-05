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
            filenames[int(file[0:2])] = file

linenames = {}
for _, _, files in os.walk(os.path.join(dir, 'LineData')):
    for file in files:
        if file.endswith('.npy'):
            linenames[int(file[0:2])] = file
        

# print(filenames.keys())
# print(linenames.keys())


new_columns = []
for index, row in df.iterrows():
    for col in df.columns:
        if col != 'ZoneID' and row[col] != 0:
            zoneID = str(row[0])
            zoneID = zoneID.replace('\t', '')
            new_columns.append(zoneID + '_' + col.replace('\t', ''))

    upperline , lowerline = '', ''
    try: 
        int(row['Upper_Line'])
    except:
        pass
        # print(row['Upper_Line'].strip())    

    try: 
        int(row['Lower_Line'])
    except:
        lowerline = row['Lower_Line'].strip()
        print(lowerline)
        if '+' in lowerline:
            sectionName = lowerline.split('=')[1]
            sectionName.strip()
            lines = lowerline.split('=')[0].split('+')
            linedata = []
            for line in lines:
                try:
                    linedata.append(np.load(os.path.join(dir, 'LineData', linenames[int(line.strip())])))
                except:
                    print(f'Line {int(line.strip())} not found')
                    break
            print(linedata[0].shape)
            x = list(range(1,linedata[0].shape[1]))
            y = np.zeros(linedata[0].shape)


            # for i in x:
            #     line1Y = np.where(line1[: ,i] == 1)[0]
            #     line2Y = np.where(line2[: ,i] == 1)[0]
            #     # print(line1Y.size, line2Y.size)
            #     if line1Y.size != 0 and line2Y.size != 0:
            #         # print(i)
            #         avg = (np.median(line1Y) + np.median(line2Y))/2
            #         y[int(avg)][i] = 1
            #         # print(y[i][x])
            #     y = cv2.dilate(y, kernel=np.ones((7,7), np.uint8))
            #     lines = line1+line2

            #     f, (ax1,ax2) = plt.subplots(2, 1, sharex=True, figsize=(6,10))
            #     ax1.imshow(lines, origin='upper', aspect='auto')
            #     ax2.imshow(y, aspect='auto')
            #     plt.show()



# # Create a new DataFrame with the new columns
# new_df = pd.DataFrame(columns=new_columns)

# # Save the new DataFrame to a new CSV file
# new_df.to_csv('new_template.csv', index=False)



