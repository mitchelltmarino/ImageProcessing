import os
import sys
import numpy as np
from PIL import Image

# Name of the image to apply filter to.
IMAGE_NAME = "Eye.jpg"

# Get Path
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Open image for reading.
image = Image.open(path+"\\"+IMAGE_NAME, "r")
image = image.convert("I")

# Create numpy array from image.
pixelArray = np.array(image)
#print(pixelArray)
#exit(0)

arr = pixelArray.copy()

# Iterate through each row.
for rowIndex in range(image.size[1]):
    # Iterate through each column in the row.
    for columnIndex in range(image.size[0]):
        #Threshold for greyscale to be B/W
        if(arr[rowIndex][columnIndex] > 127):
            arr[rowIndex][columnIndex] = 255
        else:
            arr[rowIndex][columnIndex]  = 0

# Save ouptut image.
imageOut = Image.fromarray(arr)
# Show output image.
imageOut.show()
imageOut.convert("L").save(path+"\\Eye.png")