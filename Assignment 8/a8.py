'''
Created on Dec 1, 2018

@author: Harjodh
'''
import os
import sys
import numpy as np
from PIL import Image

##First function for horizontal flip
def horizontal_flip(pixelArray, imageWidth, imageHeight):
    halfImageWidth = (imageWidth)//2
    for row in range(imageHeight):
        for col in range(halfImageWidth):
            left = pixelArray[col, row]
            right = pixelArray[imageWidth - 1 - col, row]
            pixelArray[imageWidth - 1 - col, row] = left
            pixelArray[col,row] = right
##Second function for vertical flip
def vertical_flip(pixelArray, imageWidth, imageHeight):
    halfImageHeight = (imageHeight)//2
    for col in range(halfImageHeight):
        for row in range(imageWidth):
            top = pixelArray[row,col]
            bottom = pixelArray[row, imageHeight - 1 - col]
            pixelArray[row, imageHeight - 1 - col] = top
            pixelArray[row,col] = bottom
    


#Get user input for image name and horizontal or vertical flip
direction = int(input("Horizontal(1) or Vertical (2)?: "))
IMAGE_NAME = input("Image Name and extention: ")
# Get Path
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Open image for reading.
image = Image.open(path+"\\"+IMAGE_NAME, "r")
image = image.convert("I")

# Create numpy array from image.
pixelArray = np.array(image)
arr = pixelArray.copy()
imageWidth = np.shape(pixelArray)[0]
imageHeight = np.shape(pixelArray)[1]
 
#Function calls here 
if direction == 1:
    horizontal_flip(arr, imageWidth, imageHeight)
    imageOut = Image.fromarray(arr)
    imageOut.convert("L").save(path+"\\HorizontalFlip.png")
    # Show output image.
    imageOut.show()
else:
    vertical_flip(arr, imageWidth, imageHeight)
    imageOut = Image.fromarray(arr)
    imageOut.convert("L").save(path+"\\VerticalFlip.png")
    # Show output image.
    imageOut.show()