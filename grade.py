#!/usr/local/bin/python3

import argparse
import numpy as np
from PIL import Image, ImageDraw

def hough(imgPix):
    rows = imgPix.shape[0]
    columns = imgPix.shape[1]
    diag = np.sqrt(rows ** 2 + columns ** 2)
    thetaArr = range(0, 91)
    rhoArr = range(0, int(diag))
    hough_mat = np.zeros((len(rhoArr), len(thetaArr)))
    for i in range(rows):
        for j in range(columns):
            if imgPix[i, j] == 0:
                for theta in thetaArr:
                    rho = (j * np.cos(np.deg2rad(theta))) + (i * np.sin(np.deg2rad(theta)))
                    hough_mat[int(rho), theta] += 1
    return hough_mat

def drawLines(lines):
    x = []
    y = []
    for rho, theta in lines:
        cos_val = np.cos(np.deg2rad(theta))
        sin_val = np.sin(np.deg2rad(theta))
        x0 = cos_val * rho
        y0 = sin_val * rho
        if theta <= 2:
            y_set = set(y)
            curr_set = set(range(int(x0) - 22, int(x0) + 22))
            if len(y_set.intersection(curr_set)) > 0:
                continue
            y.append(x0)
        if theta >= 88:
            x_set = set(x)
            curr_set = set(range(int(y0) - 12, int(y0) + 12))
            if len(x_set.intersection(curr_set)) > 0:
                continue
            x.append(y0)
    return x, y

def getLines(mat):
    tuple_list = []
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            tuple_list.append((mat[i, j], i, j))
    sorted_tuples = sorted(tuple_list, key=lambda tup: tup[0], reverse=True)
    count_horizon = 39
    count_verticle = 30
    lines = []
    hor_theta = -100
    vert_theta = -100
    for tpl in sorted_tuples:
        if count_horizon > 0 or count_verticle > 0:
            if tpl[2] <= 2 and count_verticle > 0:
                count_verticle -= 1
                if vert_theta < 0:
                    vert_theta = tpl[2]
                lines.append((tpl[1], vert_theta))
            elif tpl[2] >= 88 and count_horizon > 0:
                count_horizon -= 1
                if hor_theta < 0:
                    hor_theta = tpl[2]
                lines.append((tpl[1], hor_theta))
    return lines

def binary(img):
    imgPix = np.array(img)
    imgPix[imgPix > 50] = 255
    imgPix[imgPix <= 50] = 0
    return Image.fromarray(imgPix)

def detectMarkedAnswers(img, x, y):
    x = np.sort(x).astype('uint16')
    y = np.sort(y).astype('uint16')
    
    i = 0
    size = len(x) - 1
    while i < size:
        if i%2 == 0 and x[i+1] - x[i] < 25:
            x = np.delete(x, i+1)
            size -= 1
            continue
        elif i%2 == 1 and x[i+1] - x[i] < 5:
            x = np.delete(x, i+1)
            size -= 1
            continue
        else:
            i += 1
    
    j = 0
    size = len(y) - 1
    while j < size:
        if j%2 == 0 and y[j+1] - y[j] < 24:
            y = np.delete(y, j+1)
            size -= 1
            continue
        elif j%2 == 1 and y[j+1] - y[j] < 24:
            y = np.delete(y, j+1)
            size -= 1
            continue
        else:
            j += 1
            
    imgPix = np.array(img)
    areaSum = []
    for i in range(len(x) - 1):
        for j in range(len(y) - 1):
            subMat = np.array(imgPix[x[i]:x[i + 1], y[j]:y[j + 1]])
            matAve = int(np.sum(subMat)/subMat.size)
            areaSum.append((x[i], x[i + 1], y[j], y[j + 1], matAve))
    return areaSum, x, y

def colorBox(fileName, areaSum, x, y, colOffset):
    img = Image.open(fileName).convert('RGB')
    draw = ImageDraw.Draw(img)
    imgArr = np.array(img)
    x.sort()
    y.sort()
    sorted_boxes = sorted(areaSum, key=lambda val: val[4], reverse=False) 
    for i in range(len(sorted_boxes)):
        if i > 0 and sorted_boxes[i][4] - sorted_boxes[i-1][4] > 30:
            break
        else:
            box = sorted_boxes[i]
            vertIdx = int(np.where(x == box[1])[0])
            horIdx = int(np.where(y == box[3])[0])
            markedAns = optionDict[horIdx]
            markedQue = int((vertIdx+1)/2) + 29 * colOffset
            responses[markedQue].append(markedAns)
            draw.line((box[2],box[1],box[3],box[1]), fill = (0,255,0), width = 5)
            draw.line((box[2],box[0],box[3],box[0]), fill = (0,255,0), width = 5)
            draw.line((box[2],box[0],box[2],box[1]), fill = (0,255,0), width = 5)
            draw.line((box[3],box[0],box[3],box[1]), fill = (0,255,0), width = 5)
    imgArr = np.array(img)
    return imgArr, sorted_boxes

def detectAndPrintXMark(arr, x, y1, y2, cut):
    arr = arr[:,y1:y2]
    areaAve = []
    detectedX = []
    i = 0
    while i < len(x):
        areaSum = np.sum(arr[x[i]:x[i+1],10:y2-cut])
        areaSize = np.size(arr[x[i]:x[i+1],10:y2-cut])
        areaAve.append(areaSum/areaSize)
        i += 2
    maxVal = np.max(areaAve)
    i = 0
    for i in range(len(areaAve)):
        if areaAve[i] < maxVal - 5.84:
            detectedX.append(i+1)
    return detectedX

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Grading OMR sheet")
    parser.add_argument("input_form", type=str,
                        help="The blank form which is to be used for injecting the answers")
    parser.add_argument("out_file", type=str,
                        help="Output image generated after complete grading with highlighted marked answers")
    parser.add_argument("ans_text", type=str,
                        help="Output text file contatining answers detected as marked from OMR sheet")

    FLAGS, unparsed = parser.parse_known_args()
    input_form, op_file, ans_text = FLAGS.input_form, FLAGS.out_file, FLAGS.ans_text 

    print('Recognizing ', input_form, '...')
    img = Image.open(input_form).convert('L')
    img = binary(img)
    imgPixal = np.array(img)
    cuts = [(150,570),(570,1020),(1020,1460)]
    cutArr = np.ones((2035,150,3)) * 255
    responses = {}
    for i in range(1, 86):
        responses[i] = []
    
    optionDict = {1:'A', 3:'B', 5:'C', 7:'D', 9:'E'}
    colOffset = 0
    s = []
    start = 0
    markX = []
    
    colImg = Image.open(input_form).convert('RGB')
    colImgArr = np.array(colImg)
    
    for cut in cuts:
        imgPix = imgPixal[650:, cut[0]:cut[1]]
        xcords = []
        ycords = []
        
        pixArr1 = imgPix[15:495]
        mat1 = hough(pixArr1)
        lines1 = getLines(mat1)
        x1, y1 = drawLines(lines1)
        x11 = np.array(x1) + 665
        y11 = np.array(y1) + cut[0]
        xcords += sorted(x11.tolist())
        ycords += sorted(y11.tolist())
        
        pixArr2 = imgPix[495:972]
        mat2 = hough(pixArr2)
        lines2 = getLines(mat2)
        x2, y2 = drawLines(lines2)
        x21 = np.array(x2) + 1145
        y21 = np.array(y2) + cut[0]
        xcords += sorted(x21.tolist())
            
        pixArr3 = imgPix[972:1430]
        mat3 = hough(pixArr3)
        lines3 = getLines(mat3)
        x3, y3 = drawLines(lines3)
        x31 = np.array(x3) + 1622
        y31 = np.array(y3) + cut[0]
        xcords += sorted(x31.tolist())
        
        areaSum, xcords, ycords = detectMarkedAnswers(img, xcords, ycords)
        arr, s = colorBox(input_form, areaSum, xcords, ycords, colOffset)
        detectedX = detectAndPrintXMark(imgPixal, xcords, start, ycords[0], 57)
        for que in detectedX:
            markX.append(que + (29 * colOffset))
        colImgArr[np.ix_(range(665,2080),range(cut[0],cut[1]),range(3))] = arr[np.ix_(range(665,2080),range(cut[0],cut[1]),range(3))]
        
        colOffset += 1
        cutImage = Image.fromarray(imgPixal). convert('RGB')
        cutArray = np.array(cutImage)
        start = max(ycords)
    
    im = Image.fromarray(colImgArr.astype('uint8'))
    im.save(op_file)
    
    out = open(ans_text, 'w')
    for que in responses:
        out.write(str(que) + ' ' + ''.join(np.sort(responses[que])))
        if que in markX:
            out.write(' x')
        out.write('\n')
    out.close()
