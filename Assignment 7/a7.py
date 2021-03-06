import os
import sys
import numpy as np
import csv
from math import sqrt
from PIL import Image
from skimage.transform import resize

# Name of the image to apply filter to.
IMAGE_NAME = "UnknownSymbol.png"

# New dimensions for the symbols.
NEW_WIDTH = 30
NEW_HEIGHT = 30

# number of zones to classify the symbol into a feature vector
ZONES = 9

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
    # Store the resized symbol, which is resized using sci-kit image library.
    symbolDict['Symbol_Image_Resized'] = resize(componentImage, (NEW_WIDTH, NEW_HEIGHT), anti_aliasing=False)


# This output array will be the output image. Initially, it is all white.
output_array = np.full((image.size[1], image.size[0]), 255)

# Add each symbol to the output image array, using the top left corner of the original location as an anchor point.
for key, symbolDict in symbolData.items():
    output_array[symbolDict['Top']:symbolDict['Top']+NEW_HEIGHT, symbolDict['Left']:symbolDict['Left']+NEW_HEIGHT]= np.copy(symbolDict['Symbol_Image_Resized'])

# Show the output image, and save it as OutputImage.png.
imageOut = Image.fromarray(output_array)
#imageOut.show()
imageOut.convert("L").save(path+"\\OutputImage.png")



'''
assignment 5 starts here
Grab feature vectors from symbolData and store in feature_array

format for feature vector: list with 9 elements, each element is a ratio
of the b/w pixels in that symbol region.

each symbol is split up into a 3x3 matrix of pixels
'''
# initialize feature_array
feature_array = np.zeros((counter.count, ZONES))

# iterate over each symbol
currentSymbol = 0
for key, symbolDict in symbolData.items():
    # we want the resized symbol
    ndarray_resized = symbolDict['Symbol_Image_Resized']
        
    # initialize sums vector to all 0's
    sums = np.zeros(ZONES, dtype=int)
    
    sqr = sqrt(ZONES)
    zone = 0 # zone represents which zone we are currently on
    div = len(ndarray_resized) / sqr # x length of each zone
    
    while zone < ZONES:
        x_mult = zone % sqr # multiply x by this to get the correct zone x index
        y_mult = zone // sqr # multiply y by this to get the correct zone y index
        
        # lower bound index
        x_min = int(div * x_mult)
        x = x_min
        y = int(div * y_mult)
        
        # upper bound index
        x_max = int(x + div)
        y_max = int(y + div)
        
        i = 0
        while y < y_max:
            # add 1 to sum at the correct symbol zone if the pixel value is not above 0
            sums[zone] += 0 if ndarray_resized[y][x] > 0 else 1
            
            x += 1
            if x == x_max:
                y += 1
                x = x_min
            
        zone += 1
        
    div2 = div*div
    #print('sums:', sums)
    # iterate through sums to get features
    for i in range(ZONES):
        feature_array[currentSymbol][i] = sums[i]/div2
    print('Unknown Feature:', feature_array[currentSymbol])
    feature_vector = feature_array[currentSymbol]
'''
Assignement 7 Starts here  --
'''
    #to calculate distance we take the euclidean distance between each of the 9 slots and add 
    #them up to give us a total distance. The feature vector which provides the smallest distance
    #will be used to classify the unknown symbol
def distance(feature_vector,feature_database):
    #first read in the existing feature file produced in previous assignment
    with open(feature_database) as f:
        array = csv.reader(f, delimiter=',')
        count = 0
        #will hold all of the caluclated distances, size 10 because feature list is 0-9
        distance_array = [0]*10
        
        for feature in array:
            position = 1#skips first value in the row 
            for value in feature_vector:
                distance_array[count] += (sqrt((float(value)-float(feature[position]))**2))
                position+=1
            count+=1
        #find the smallest distance in the array
        min_d = distance_array[0]
        min_pos = 0
        count = 0
        for d in distance_array:
            if d < min_d:
                min_d = d
                min_pos = count
            count+=1 
        print("The unknown symbol has been classified as: ", min_pos)

feature_database = (path + "\\FeatureList.txt")
distance(feature_vector, feature_database)
    
   
    