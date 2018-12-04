'''
Created on Nov 27, 2018

This program is to do convolution with a 1D array on an image first using a horizontal
kernel and then follwed by a vertical kernel.

To display the effects of using two seperate kernels vs one larger 2d kernel 
The outputs are OutputImageHoriz - Which is image after horizontal convolution
OutputImageFinal - which is image after vertical convolution on the resultant image of last step
@author: Harjodh
'''
import os
import sys
import numpy as np
from PIL import Image

def convolveHorizontal(rowIndex, columnIndex, pixelArray, kernel):
    left_location = columnIndex - 1
    right_location = columnIndex + 1
    pixelNewValue = 255
    if left_location < 0:
        pixelNewValue = pixelArray[rowIndex][columnIndex] * kernel[0][1]
        pixelNewValue = pixelNewValue + pixelArray[rowIndex][right_location] * kernel[0][0]
    elif right_location > len(pixelArray[0]) - 1:
        pixelNewValue = pixelArray[rowIndex][columnIndex] * kernel[0][1]
        pixelNewValue = pixelNewValue + pixelArray[rowIndex][left_location] * kernel[0][2]
    else:
        pixelNewValue = pixelArray[rowIndex][columnIndex] * kernel[0][1]
        pixelNewValue = pixelNewValue + pixelArray[rowIndex][right_location] * kernel[0][0]
        pixelNewValue = pixelNewValue + pixelArray[rowIndex][left_location] * kernel[0][2]    
    return pixelNewValue 



def convolveVertical(rowIndex, columnIndex, pixelArray, kernel):
    top_location = rowIndex - 1
    bottom_location = rowIndex + 1
    pixelNewValue = 255
    height = (np.shape(pixelArray))[0] -1 
    if top_location < 0:
        pixelNewValue = pixelArray[rowIndex][columnIndex] * kernel[1][0]
        pixelNewValue = pixelNewValue + pixelArray[bottom_location][columnIndex] * kernel[0][0]
    elif  bottom_location > height: 
        pixelNewValue = pixelArray[rowIndex][columnIndex] * kernel[1][0]
        pixelNewValue = pixelNewValue + pixelArray[top_location][columnIndex] * kernel[2][0]
    else:
        pixelNewValue = pixelArray[rowIndex][columnIndex] * kernel[1][0]
        pixelNewValue = pixelNewValue + pixelArray[bottom_location][columnIndex] * kernel[0][0]
        pixelNewValue = pixelNewValue + pixelArray[top_location][columnIndex] * kernel[2][0]    
    return pixelNewValue 
#####IMAGE PREPERATION######
# Name of the image to apply convolution to
IMAGE_NAME = "SamplePhoto.jpg"
# Get Path
path = os.path.abspath(os.path.dirname(sys.argv[0]))
# Open image for reading.
image = Image.open(path+"\\"+IMAGE_NAME, "r")
image = image.convert("I")
# Create numpy array from image.
pixelArray = np.array(image)
arr = pixelArray.copy()
KERNEL = np.array([[1/3, 1/3, 1/3]])

##FUNCTION CALL##

for rowIndex in range(image.size[1]):
    # Iterate through each column in the row.
    for columnIndex in range(image.size[0]):
        # Apply filter.
        conv = convolveHorizontal(rowIndex, columnIndex, pixelArray, KERNEL)
        arr[rowIndex][columnIndex] = conv

##########OUTPUT IMAGE1#############
imageOut = Image.fromarray(arr)
imageOut.convert("L").save(path+"\\OutputImageHoriz.png")

################################################
KERNEL = np.array([[1/3],[1/3],[1/3]]) 
##FUNCTION CALL##
#####IMAGE PREPERATION######
# Get Path
path = os.path.abspath(os.path.dirname(sys.argv[0]))
# Open image for reading.
image = Image.open(path+"\\OutputImageHoriz.png", "r")
image = image.convert("I")
# Create numpy array from image.
pixelArray = np.array(image)
arr = pixelArray.copy()

for rowIndex in range(image.size[1]):
    # Iterate through each column in the row.
    for columnIndex in range(image.size[0]):

        # Apply filter.
        conv = convolveVertical(rowIndex, columnIndex, pixelArray, KERNEL)
        arr[rowIndex][columnIndex] = conv


imageOut = Image.fromarray(arr)
imageOut.show()
imageOut.convert("L").save(path+"\\OutputImageFinal.png")
