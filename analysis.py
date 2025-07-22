import cv2
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
from scipy import stats
warnings.filterwarnings('ignore')



def getArea(line2Path, line1Path, savePath = None, customStart = None, customEnd = None):
    line1 = np.load(line1Path)
    line2 = np.load(line2Path)

    x = list(range(1,line1.shape[1]))
    # y = [0] * (line1.shape[1])
    y = np.zeros((line1.shape[1],1))
    # print(y.shape)
    for i in x:
        line1Y = np.where(line1[: ,i] == 1)[0]
        line2Y = np.where(line2[: ,i] == 1)[0]
        # print(line1Y.size, line2Y.size)
        if line1Y.size != 0 and line2Y.size != 0:
            y[i] = np.median(line1Y) - np.median(line2Y)
        else:
            y[i] = 0

    lines = line1+line2
    y[y==0] = np.nan
    yFinite = np.argwhere(np.isfinite(y)) #get indexes of non NaN to find endpoints of line

    start = yFinite[0][0] + 300
    end = yFinite[-1][0] - 300

    if customStart != None:
        start = customStart
    if customEnd != None:
        end = customEnd

    y[:start] = np.nan
    y[end:] = np.nan
    mean =  y[~np.isnan(y)].mean()
    sd =  y[~np.isnan(y)].std()


    f, (ax1,ax2) = plt.subplots(2, 1, height_ratios=[10,4], sharex=True, figsize=(6,10))
    ax1.imshow(lines.astype('uint8'), origin='upper', aspect='auto')

    
    textstr = '\n'.join((
    r'mean=%.2f' % (mean, ),
    r'SD=%.2f' % (sd, )))

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    ax2.plot(y)
    if savePath != None:
        plt.savefig(savePath)
    else:
        plt.show()
    # print('trimmed mean:', stats.trim_mean(y, 0.1) )
    return mean, sd, start, end

def getAvg(lines, linenames, sectionName):
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

    f, (ax1,ax2) = plt.subplots(2, 1, sharex=True, figsize=(6,10))
    allLines=linedata[0]
    for line in linedata[1:]:
        allLines+=line
    ax1.imshow(allLines, origin='upper', aspect='auto')
    ax2.imshow(y, aspect='auto')
    # plt.show()
    plt.savefig(os.path.join(dir, 'Records', sectionName + '_Avg.png'))

    im = np.zeros((linedata[0].shape[0], linedata[0].shape[1],4))
    im = y*255
    # im[:, :, 3] = y*255
    cv2.imwrite(os.path.join(dir, 'LineImages', sectionName +'.png'), im)
    np.save(os.path.join(dir, 'LineData', sectionName +'.npy'), y)
    return y

if __name__ == '__main__':
    getArea(r'images\CCC_K10_F3_L1_crop\LineData\08_SOGCB.npy', r'images\CCC_K10_F3_L1_crop\LineData\07_D0CML.npy')
    # OR
    # getArea('images/CCC_K10_F3_L1_crop/LineData/01_SOGUL.npy', 'images/CCC_K10_F3_L1_crop/LineData/08_SOGCB.npy')