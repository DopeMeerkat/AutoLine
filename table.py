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
        # print(lowerline)
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

            x = list(range(1,linedata[0].shape[1]))
            y = np.zeros(linedata[0].shape)
            
            # for i in range(600):#x:
            for i in x:
                # print(i)
                avg = 0
                skip = False
                for line in linedata:
                    lineY = np.where(line[: ,i] > 0)[0]
                    # print(lineY)
                    if lineY.size != 0:
                        avg += np.median(lineY)
                    else:
                        skip = True
                        break
                    
                if skip:
                    continue

                avg = avg/len(linedata)
                y[int(avg)][i] = 1

            y = cv2.dilate(y, kernel=np.ones((7,7), np.uint8))

            # f, (ax1,ax2) = plt.subplots(2, 1, sharex=True, figsize=(6,10))
            # allLines=linedata[0]
            # for line in linedata[1:]:
            #     allLines+=line
            # ax1.imshow(allLines, origin='upper', aspect='auto')
            # ax2.imshow(y, aspect='auto')
            # plt.show()

            im = np.zeros((linedata[0].shape[0], linedata[0].shape[1],4))
            im = y*255
            # im[:, :, 3] = y*255
            cv2.imwrite(os.path.join(dir, 'LineImages', sectionName +'.png'), im)
            np.save(os.path.join(dir, 'LineData', sectionName +'.npy'), y)



# # Create a new DataFrame with the new columns
# new_df = pd.DataFrame(columns=new_columns)

# # Save the new DataFrame to a new CSV file
# new_df.to_csv('new_template.csv', index=False)



