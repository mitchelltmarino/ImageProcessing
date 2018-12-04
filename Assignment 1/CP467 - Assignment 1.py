import os
import sys
import numpy as np
from PIL import Image

# Name of the image to apply filter to.
IMAGE_NAME = "SamplePhoto.jpg"
# The kernel to apply the filter operation with.
# 3x3
KERNEL = np.array([
    [-1, -1, -1],
    [-1, 8, -1],
    [-1, -1, -1]
])

'''
# 5x5
KERNEL = np.array([
    [0, 0, 1, 0, 0],
    [0, 1, 2, 1, 0],
    [1, 2, -16, 2, 1],
    [0, 1, 2, 1, 0],
    [0, 0, 1, 0, 0]
])
'''

# Throw err
if KERNEL.shape[0] != KERNEL.shape[1] or KERNEL.shape[0] % 2 == 0 or KERNEL.shape[1] %2 == 0:
    print("Kernel should be of size n x n, where n is an odd number.")
    exit(0)

# The filter operation.
def filter(rowIndex, columnIndex, pixelArray, kernel):
    '''
    This function will return the result of the filter operation.
    ---
    rowIndex = The row index of the center of the filter.
    columnIndex = The column index of the center of filter.
    pixelArray = The array of pixels in an image.
    kernel = the kernel to apply for the correlation.
    '''

    # The correlation after the operation.
    correlation = 0

    # The very center of the n x n kernel.
    kernelSize = len(kernel)
    kernelCenter = int((len(kernel) - 1) / 2) 

    #print("--")

    # Top half of kernel.
    for i in range(kernelCenter):
        for j in range(kernelSize):
            # Row and column.
            row = rowIndex - kernelCenter + i
            column = columnIndex - kernelCenter + j
            #print(row, column, " : ", i, j)
            # RGB values of current index in pixelArray.
            if row < 0 or column < 0 or row >= len(pixelArray) or column >= len(pixelArray[0]):
                if assertValue(row, column, pixelArray) == None:
                    print("NONE")
                correlation += assertValue(row, column, pixelArray) * kernel[i][j]
            else:
                correlation += pixelArray[row][column] * kernel[i][j]

    # Middle Row of kernel.
    for j in range(-kernelCenter, kernelCenter+1):
        # RGB values of current index in pixelArray.
        #print(rowIndex, columnIndex+j, " : ", kernelCenter, j+kernelCenter)
        if rowIndex < 0 or columnIndex + j < 0 or rowIndex >= len(pixelArray) or columnIndex+j >= len(pixelArray[0]):
            if assertValue(rowIndex, columnIndex+j, pixelArray) == None:
                print("NONE")
            correlation += assertValue(rowIndex, columnIndex + j, pixelArray) * kernel[kernelCenter][j+kernelCenter]
        else:
            correlation += pixelArray[rowIndex][columnIndex + j] * kernel[kernelCenter][j+kernelCenter]

    # Bottom half of kernel.
    for i in range(kernelCenter+1, kernelSize):
        for j in range(kernelSize):
            # Row and column.
            row = rowIndex + i
            column = columnIndex - kernelCenter + j
            #print(row, column, " : ", i, j)
            # RGB values of current index in pixelArray.
            if row < 0 or column + j < 0 or row >= len(pixelArray) or column >= len(pixelArray[0]):
                if assertValue(row, column, pixelArray) == None:
                    print("NONE")
                correlation += assertValue(row, column, pixelArray) * kernel[i][j]
            else:
                correlation += pixelArray[row][column] * kernel[i][j]

    return correlation

def assertValue(row, column, pixelArray):

    # Width and height of the image.
    height = len(pixelArray) - 1
    width = len(pixelArray[0]) - 1

    # -- Check all four corners of the image --
    # Top left.
    if (row < 0 and column < 0):
        return pixelArray[0][0]
    # Top right.
    if (row < 0 and column > width):
        return pixelArray[0][width]
    # Bottom left.
    if (row > height and column < 0):
        return pixelArray[height][0]
    # Bottom right.
    if (row > height and column > width):
        return pixelArray[height][width]

    # -- Check edges of image, not corners --
    # Top edge.
    if (row < 0):
        return pixelArray[0][column]
    # South edge.
    if (row > height):
        return pixelArray[height][column]
    # Left edge.
    if (column < 0):
        return pixelArray[row][0]
    # Right edge.
    if (column > width):
        return pixelArray[row][width]

# Get Path
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Open image for reading.
image = Image.open(path+"\\"+IMAGE_NAME, "r")
image = image.convert("I")

# Create numpy array from image.
pixelArray = np.array(image)
#print(pixelArray)
#exit(0)

arr = pixelArray.copy()# np.zeros((image.size[1], image.size[0]))

# Iterate through each row.
for rowIndex in range(image.size[1]):
    # Iterate through each column in the row.
    for columnIndex in range(image.size[0]):
        # Apply filter.
        correlation = filter(rowIndex, columnIndex, pixelArray, KERNEL)
        #pixelArray[rowIndex][columnIndex] = correlation
        arr[rowIndex][columnIndex] = correlation

# Save ouptut image.
imageOut = Image.fromarray(arr)#.convert("1")#Image.frombuffer("I", (image.size[1] -1, image.size[0]-1))
# Show output image.
imageOut.show()
imageOut.convert("L").save(path+"\\OutputImage.png")
