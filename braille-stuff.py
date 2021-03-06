# constants, but I get they are not caps...
asciiYDots = 4
asciiXDots = 2
from PIL import Image
import argparse
import math
import numpy as np

# main source code I am replicating. Find here:
# https://lachlanarthur.github.io/Braille-ASCII-Art/dist/index.js


# https://stackoverflow.com/questions/14681609/create-a-2d-list-out-of-1d-list
# usuage (list of 1d elements, n elements per line )
# 2x2 matrix is the_data = [1,2,3,4] n = 2
def to_matrix(the_data, n):
    return [the_data[i:i+n] for i in range(0, len(the_data), n)]


# requires rgb or rgba images
# https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil

def image_data_to_braille(rgb_array):
    threshold = int(150)
    # The original author used subarrays in this function.
    # I am taking a slightly different method, because the rbga values are in a
    # tuple. hence why I do not need to get another subarray
    # A GREAT READ
    # I did not know anything about braille until this project
    # https://en.wikipedia.org/wiki/Braille_Patterns
    if len(rgb_array) == 4 and len(rgb_array[0]) == 2:
        dots = [rgb_array[0][0], rgb_array[1][0], rgb_array[2][0], rgb_array[0][1], rgb_array[1][1], rgb_array[2][1], rgb_array[3][0], rgb_array[3][1]]
        # print(*dots)
    else:
        return str(chr(0x2800))
    #     dots = dots
    #         .map(([r, g, b, a]) => (r + g + b) / 3)
    #         .map(grey => +(grey < threshold));
    for i in range(len(dots)):
        dots[i] = '1' if dots[i] >= threshold else '0'
    # now we do some more vodoo magic
    # actually quite clever technique of binary representation of braille
    # again, see https://en.wikipedia.org/wiki/Braille_Patterns
    # braille starts at 0x2800 or 10240
    dots.reverse()
    # print(''.join(dots))
    return str(chr(0x2800 + int(''.join(dots),2)))

    # return String.fromCharCode(10240 + parseInt(dots.reverse().join(''), 2));
    # return ''

def parse_image(image, asciiWidth):
    # necessary to have both r,g,b for this particular algorithm
    rgb_pixels = image.convert('L')
    # .getdata()
    # print (list(rgb_pixels))
    width, height = rgb_pixels.size
    
    # new image height. Want to proportionately make the image fit the screen
    asciiHeight = math.ceil( asciiWidth * asciiXDots * ( height / width ) / asciiYDots )
    # print (asciiHeight, asciiWidth)
    width = asciiWidth * asciiXDots
    height = asciiHeight * asciiYDots
    rgb_pixels = rgb_pixels.resize((width,height)).getdata()
    # conversion of a 1d array to 2d array
    two_d_array = to_matrix(list(rgb_pixels), width)

    # now time for the magic
    finished_image = []
    
    # want to make small subsets of the image. i.e. section the image in asciiHeight*asciiWidth
    # sections.
    # . .
    # . .
    # . .
    # . .
    temp  = np.array(two_d_array)
    for y in range(0,height, asciiYDots):
        line_of_braille = ''
        for x in range(0,width,asciiXDots):
            # want to get that subsection now. starting in corner (x,y) to (width,height).
            # in our case we want asciiXDots width, and asciiYDots height
            # referencing: https://stackoverflow.com/questions/38049214/how-to-obtain-a-subarray-in-python-3
            # print ([i[3:6] for i in a[0:2]])
            # I got the array indices by trial and error with a debugger. I am sure there is a more
            # theoretical approach, but I recommend trial and error.
            # we want to get a subset of the image. We can easily use a package like numpy, but
            # relying on numpy makes the project dependencies huge.
            # array_s = [sub[asciiXDots:asciiYDots] for sub in two_d_array[x:y+asciiYDots]]
            # print(image_data_to_braille([sub[asciiXDots:asciiYDots] for sub in two_d_array[x:y+asciiYDots]]))
            line_of_braille += image_data_to_braille(temp[y:min(y+asciiYDots,height),x:min(x+asciiXDots,width)])
            # image_data_to_braille([sub[asciiXDots:asciiYDots] for sub in two_d_array[x:y+asciiYDots]])
            # print(len(two_d_array[x:y+asciiYDots]))
            # exit(1)
            # print (two_d_array[x:y+asciiYDots])
            # print([sub[asciiXDots:asciiYDots] for sub in two_d_array[x:y+asciiYDots]])
            # exit(1)
            # line_of_braille += image_data_to_braille([sub[asciiXDots:asciiYDots] for sub in two_d_array[x:y+asciiYDots]])
            # line_of_braille += image_data_to_braille([sub[asciiXDots:asciiYDots] for sub in two_d_array[x:y+asciiYDots]])
        finished_image.append(line_of_braille)
        print(line_of_braille)
    # print(finished_image)
    return finished_image

if __name__ == '__main__':
    # https://github.com/FranciscoMoretti/asciify-color/blob/master/asciify.py
    # eventually I will add this feature. For now, I use direct input from command line.
    #     import urllib.request
    # try:
    #     if sys.argv[1].startswith('http://') or sys.argv[1].startswith('https://'):
    #         urllib.request.urlretrieve(sys.argv[1], "asciify.jpg")
    #         path = "asciify.jpg"
    #     else:
    #         path = sys.argv[1]
    # urllib.request.urlretrieve(image,'image.jpg')

    # https://github.com/itszn/Image-To-Braille/blob/master/braille.py
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument('file', help='The image file to render')
        
        args = ap.parse_args()
        filename = args.file
        # intentionally not converting to a 2d array here. If someone, or myself, wants to
        # add a 1d array functionality, great! I am sticking with 2d arrays right now. 
        with Image.open(filename, 'r') as img:
            # default asciiWidth I found online. Aparently over 500 gets laggy
            new_img = parse_image(img, 100)
            # print (new_img)
    except Exception as e:
        print('Exiting with exception', str(e))
