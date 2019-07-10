#!/usr/bin/env python3

import argparse
from PIL import Image
import numpy as np


def decrypt(imageFile, outFile):
    img = Image.open(imageFile).convert("L")
    out = open(outFile, 'w')
    imgPix = np.array(img)
    subImg = imgPix[np.ix_(range(2125), range(200))]
    subImg[subImg <= 120] = 0
    subImg[subImg > 120] = 255
    
    i = 0
    ans_n = 1
    while i < 2125:
        temp = subImg[np.ix_(range(i, i+20), range(200))]
        maxStream = getMaxOccStream(temp)
        row = get8BitStream(maxStream)
        ans_char = ''.join(chr(i) for i in np.trim_zeros(np.packbits(row)))
        out.write("{} {}".format(ans_n, ans_char))
        out.write('\n')
        i += 25
        ans_n += 1
    out.close()


def getMaxOccStream(arr):
    out = []
    for i in range(arr.shape[1]):
        count = np.bincount(arr[:, i])
        out.append(np.argmax(count))
    return out


def get8BitStream(vec):
    out = []
    vec = np.array(vec)
    vec = vec / 255
    vec[vec == 0] = 5
    vec[vec == 1] = 0
    vec[vec == 5] = 1
    for i in range(40):
        subVec = vec[5*i:(5*i) + 5]
        subVec = np.array(subVec, dtype=np.int64)
        count = np.bincount(subVec)
        out.append(np.argmax(count))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract answers from a encoded image and write into a txt file")
    parser.add_argument("input_form", type=str,
                        help="OMR sheet contatining encoded answers")
    parser.add_argument("ans_text", type=str,
                        help="name of text o/p file contatining the answers")

    FLAGS, unparsed = parser.parse_known_args()
    input_form, ans_text = FLAGS.input_form, FLAGS.ans_text

    decrypt(input_form, ans_text)
