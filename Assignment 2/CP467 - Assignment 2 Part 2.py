import os
import sys
import numpy as np
from PIL import Image
from skimage.transform import resize

# Name of the image to apply filter to.
IMAGE_NAME = "T3.png"

# Get path of file.
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Open image for reading.
image = Image.open(path+"\\"+IMAGE_NAME, "r")
image = image.convert("I")

# One array stores original image, the other will be used to store components of the image.
pixelArray = np.array(image)
componentArray =  np.zeros((image.size[1], image.size[0]))

# Put all values in the image as solely black or white.
for rowIndex in range(image.size[1]):
    for columnIndex in range(image.size[0]):
        if(pixelArray[rowIndex][columnIndex] > 127):
            pixelArray[rowIndex][columnIndex] = 255
        else:
            pixelArray[rowIndex][columnIndex]  = 0

class Counter(object):
    '''The counter object is to keep track of how many symbols have been found.'''
    def __init__(self):
        self.count = 0

def inBounds(coordinates, size):
    '''
    Numpy wraps around to other side of array if indices are out of bounds, this function solves that.
    - Coordinates = The coordinates in format (x, y)
    - Size = The size of array, in format (height, width)
    Returns False if index is out of bounds, returns false if index is in bounds.
    '''
    # Coordinates[0] = row.
    # Coordinates[1] = column.
    y = coordinates[0]
    x = coordinates[1]
    
    # Return false if invalid condition is met.
    if x < 0:
        return False
    elif y < 0:
        return False
    # Size[1] = width.
    elif size[1] <= x:
        return False
    # Size[0] = height.
    elif size[0] <= y:
        return False

    # Return true if no invalid conditions were met.
    return True

def connect(coordinates, counter, pixelArray, componentArray):
    '''
    Propogates a black pixels' symbol ID to neighbouring black pixels.
        - If the current pixel is black but does not have an ID, it assigns the pixel a unique ID.
        
    coordinates = The coordinates of the pixel in pixelArray.
    counter = A counter, used to keep track of # of symbols.
    pixelArray = A 2D array representing the pixels of an image.
    componentArray = A 2D array of symbol IDs, respective to the pixels in pixelArray.
    '''
    # Coordinates[0] = Row.
    # Coordinates[1] = Column.
    y = coordinates[0]
    x = coordinates[1]
    
    # Get the value of the current pixel. 
    # If it is not black, simply don't bother with it. (return)
    currValue = pixelArray[y][x]
    if currValue > 0:
        return

    # If the pixel is not part of a symbol, increment symbol counter
    if componentArray[y][x] == 0:
        counter.count = counter.count + 1
        componentArray[y][x] = counter.count

    # Assign currComponent to the symbol ID of the current pixel.
    currComponent = componentArray[y][x]

    # Examine neighbouring pixels, giving them the symbol of the current pixel if they satisfy requirements.
    for rowOffset in range(-1, 2):
        for columnOffset in range(-1, 2):
            # If conditions are met:
            # - arr[y][x] is in bounds after offsets.
            # - The neighbour pixel is not part of a symbol already.
            # - The neighbour pixel is also black.
            if inBounds((y+rowOffset, x+columnOffset), (len(pixelArray), len(pixelArray[0]))) and componentArray[y+rowOffset][x+columnOffset] != currComponent and pixelArray[y+rowOffset][x+columnOffset] == currValue:
                componentArray[y+rowOffset][x+columnOffset] = currComponent

def adjust(coordinates, counter, pixelArray, componentArray):
    '''
    Converts symbols incorrectly identified as separate to a single symbol.
        - For example, if symbols 1 and 2 are touching, they will be changed to just symbol 1.
    
    coordinates = The coordinates of the pixel in pixelArray.
    counter = A counter, used to keep track of # of symbols.
    pixelArray = A 2D array representing the pixels of an image.
    componentArray = A 2D array of symbol IDs, respective to the pixels in pixelArray.
    '''
    # Coordinates[0] = Row.
    # Coordinates[1] = Column.
    y = coordinates[0]
    x = coordinates[1]

    # Get the value of the current pixel and current symbol ID.
    currComponent = componentArray[y][x]
    currValue = pixelArray[y][x]

    # Check neighbouring pixels.
    for rowOffset in range(-1, 2):
        for columnOffset in range(-1, 2):
            # If conditions are met:
            # - arr[y][x] is in bounds after offsets.
            # - The neighbour pixel is also black.
            # - The neighbour pixel is a different symbol.
            if inBounds((y+rowOffset, x+columnOffset), (len(pixelArray), len(pixelArray[0]))) and pixelArray[y+rowOffset][x+columnOffset] == currValue and componentArray[y+rowOffset][x+columnOffset] != currComponent:
                
                # If the neighbouring pixel's symbol value is higher,
                if (componentArray[y+rowOffset][x+columnOffset] > currComponent):
                    # Replace all occurences of the nieghbouring pixel's symbol ID in componentArray  with the symbol ID of current component.
                    componentArray[componentArray == componentArray[y+rowOffset][x+columnOffset]] = currComponent
                
                # If the neighbouring pixel's symbol value is lower,
                else:
                    # Replace all occurences of the current pixel's symbol ID in component with that of the neighbour.
                    componentArray[componentArray == currComponent] = componentArray[y+rowOffset][x+columnOffset]
                    # Update currComponent to account for this change.
                    currComponent = componentArray[y+rowOffset][x+columnOffset]
                
                # There are less symbols after merging action has been taken.
                counter.count = counter.count - 1

# Counter for tracking # of symbols.
counter = Counter()
'''
Purpose of this loop:
- Identifies separate components, marking them in componentArray with a unique ID.
    - This is done by scanning over the entire image left to right, onto the next row, and so on.
    - Each time a new symbol is identified, they are marked with the current value of counter, and counter is increased by 1.
'''
# Iterate over rows, columns of the image.
for rowIndex in range(image.size[1]):
    for columnIndex in range(image.size[0]):
        connect((rowIndex, columnIndex), counter, pixelArray, componentArray)

'''
Purpose of this loop:
- Complex symbols may be mistaken as multiple symbols during the first loop.
    - This loop fixes that problem by merging neighbouring symbols.
'''
# Iterate over rows, columns of the image.
for rowIndex in range(image.size[1]):
    for columnIndex in range(image.size[0]):
        adjust((rowIndex, columnIndex), counter, pixelArray, componentArray)

# Dictionary to store information about each symbol.
symbolData = dict()

# Build the dictionary.
for componentID in np.unique(componentArray):
    if componentID != 0:
        # Top --> Top bound index in image.
        # left --> Left bound index in image.
        # right --> Right bound index in image.
        # bottom --> bottom bound index in image.
        symbolData[componentID] = {
            'Top': None,
            'Left': None,
            'Right': None,
            'Bottom': None
        }

'''
Purpose of this loop:
    - To find the smallest bounding box for each symbol.
'''
# Iterate over rows, columns of the image.
for rowIndex in range(image.size[1]):
    for columnIndex in range(image.size[0]):
        
        # Current symbol.
        symbol_ID = componentArray[rowIndex][columnIndex]

        if symbol_ID != 0:

            # Replace top bound value for the component, if needed.
            if symbolData[symbol_ID]['Top'] is None or symbolData[symbol_ID]['Top'] > rowIndex:
                symbolData[symbol_ID]['Top'] = rowIndex

            # Replace left bound value for the component, if needed.
            if symbolData[symbol_ID]['Left'] is None or symbolData[symbol_ID]['Left'] > columnIndex:
                symbolData[symbol_ID]['Left'] = columnIndex

            # Replace right bound value for the component, if needed.
            if symbolData[symbol_ID]['Right'] is None or symbolData[symbol_ID]['Right'] < columnIndex:
                symbolData[symbol_ID]['Right'] = columnIndex

            # Replace bottom bound value for the component, if needed.
            if symbolData[symbol_ID]['Bottom'] is None or symbolData[symbol_ID]['Bottom'] < rowIndex:
                symbolData[symbol_ID]['Bottom'] = rowIndex


'''
Purpose of this loop:
    - Create proper black and white levels for each component.
    - Create sub-images for each component.
    - Shrink these sub-images to desired NEW_WIDTH and NEW_HEIGHT.
'''
# Iterate over every component
for key, symbolDict in symbolData.items():
    # Get the bounding box locations.
    top = symbolDict['Top']
    left = symbolDict['Left']
    right = symbolDict['Right']
    bottom = symbolDict['Bottom']
    # Create sub-image by indexing the componentArray.
    componentImage = np.copy(componentArray[top:bottom, left:right])
    # Adjust image such that symbols are black, and everything else is white.
    componentImage[componentImage == 0] = -1
    componentImage[componentImage > 0] = 0
    componentImage[componentImage < 0] = 255
    # Store the symbol image.
    symbolDict['Symbol_Image'] = componentImage

i = 1
# Now, print # of black pixels for all the symbols.
for key, symbolDict in symbolData.items():
    # Print the number of black pixels in the image.
    black_pixels = np.count_nonzero(symbolDict['Symbol_Image'] == 0)
    print("Symbol #%d has %d black pixels." %(i, black_pixels))
    i += 1