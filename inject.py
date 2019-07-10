#!/usr/bin/env python3

import argparse
from PIL import Image
import numpy as np


def encrypt(imageFile, ansFile, outFile):
    img = Image.open(imageFile).convert('L')
    ans = open(ansFile)
    imgPix = np.array(img)
    ansArr = []
    barCode = []

    for line in ans:
        ansArr.append(line.rstrip('\n').split(' ')[1])

    for question in ansArr:
        bitArr = ''
        for answers in question:
            bitArr += format(ord(answers), '08b')
        bitArr = bitArr.ljust(40, '0')
        bitArr = bitArr.replace('0', 'x').replace('1', '0').replace('x', '1')
        bitArr = ''.join([bit*5 for bit in bitArr])
        for i in range(20):
            barCode.append(bitArr)
        for i in range(5):
            barCode.append(''.ljust(200, '1'))

    barCode = ''.join(barCode)
    barCodeArr = np.array(list(barCode)).reshape(2125, 200)
    barCodeArr = barCodeArr.astype('uint8')
    barCodeArr[barCodeArr == 1] = 255
    imgPix[:2125, :200] = barCodeArr[:2125, :200]
    newImg = Image.fromarray(imgPix)
    newImg.save(outFile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inject encoded answer data into a blank OMR sheet")
    parser.add_argument("input_form", type=str,
                        help="The blank form which is to be used for injecting the answers")
    parser.add_argument("ans_text", type=str,
                        help="text i/p file contatining the answers")
    parser.add_argument("out_file", type=str,
                        help="Output image file contatining OMR sheet with encoded answers")

    FLAGS, unparsed = parser.parse_known_args()
    input_form, ans_text, op_file = FLAGS.input_form, FLAGS.ans_text, FLAGS.out_file

    encrypt(input_form, ans_text, op_file)
