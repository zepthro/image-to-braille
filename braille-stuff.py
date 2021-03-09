from PIL import Image
import argparse
import math

ASCIIYDOTS = 4
ASCIIXDOTS = 2
THRESHOLD = int(150)

# main source code I am replicating. Find here:
# https://lachlanarthur.github.io/Braille-ASCII-Art/dist/index.js


# https://stackoverflow.com/questions/14681609/create-a-2d-list-out-of-1d-list
# usuage (list of 1d elements, n elements per line )
# 2x2 matrix is the_data = [1,2,3,4] n = 2
def to_matrix(the_data, n):
    return [the_data[i:i+n] for i in range(0, len(the_data), n)]


# requires grayscale images
# https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil

def image_data_to_braille(rgb_array):
    # The original author used subarrays in this function.
    # I am taking a slightly different method than the original author, because the rgb_array is grayscale. 
    # Hence, why I do not need to get another subarray
    # A GREAT READ: https://en.wikipedia.org/wiki/Braille_Patterns
    # I did not know anything about braille until this project
    # The following line sets up the 4x2 array the wiki article mentions
    dots = [rgb_array[0][0], rgb_array[1][0], rgb_array[2][0], rgb_array[0][1], rgb_array[1][1], rgb_array[2][1], rgb_array[3][0], rgb_array[3][1]]
    # make the image a binary value for each gray scale value
    # if you want an inverted image, you flip dots >= threshold to dots < threshold
    # or simply not(...)
    # or the bitwise not operator on the result
    for i in range(len(dots)):
        dots[i] = '1' if dots[i] >= THRESHOLD else '0'
    # now we do some more vodoo magic
    # actually quite clever technique of binary representation of braille
    # again, see https://en.wikipedia.org/wiki/Braille_Patterns
    # braille starts at hex(0x2800) or int(10240)
    dots.reverse()
    return str(chr(0x2800 + int(''.join(dots),2)))

def parse_image(image, asciiWidth):
    # necessary to have a gray scaled image. Can do this with a conversion
    # or simply finding the average of (r,g,b) per pixel value
    rgb_pixels = image.convert('L')
    width, height = rgb_pixels.size
    
    # new image height. Want to proportionately make the image fit the screen
    # not sure the exact conversion calculation here.
    asciiHeight = math.ceil( asciiWidth * ASCIIXDOTS * ( height / width ) / ASCIIYDOTS )
    # want equal number of asciiDots. i.e. 4x2 array
    width = asciiWidth * ASCIIXDOTS
    height = asciiHeight * ASCIIYDOTS
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
    for y in range(0,height, ASCIIYDOTS):
        line_of_braille = ''
        for x in range(0,width,ASCIIXDOTS):
            # want to get that subsection now. starting in corner (x,y) to (width,height).
            # in our case we want ASCIIXDOTS width, and ASCIIYDOTS height
            # referencing: https://stackoverflow.com/questions/38049214/how-to-obtain-a-subarray-in-python-3
            # print ([i[3:6] for i in a[0:2]])
            # I got the array indices by trial and error with a debugger. I am sure there is a more
            # theoretical approach, but I recommend trial and error.
            # we want to get a subset of the image. We can easily use a package like numpy, but
            # relying on numpy makes the project dependencies huge.
            line_of_braille += image_data_to_braille([sub[x:x+ASCIIXDOTS] for sub in two_d_array[y:y+ASCIIYDOTS]])

        finished_image.append(line_of_braille)
    return finished_image

if __name__ == '__main__':
    import requests
    # Some of my code references: https://github.com/itszn/Image-To-Braille/blob/master/braille.py
    # Feel free to give it a read
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument('file', help='The image file to render')
        ap.add_argument('-t', required=False, help='How dark you want the pixels before recognizing. Default is 150.',
        default=150, type=int, choices=range(0,256), metavar='[0-255]')

        args = ap.parse_args()
        filename = args.file
        THRESHOLD = args.t
        # intentionally not converting to a 2d array here. If someone, or myself, wants to
        # add a 1d array functionality, great! I am sticking with 2d arrays right now. 
        # check if we need to open a file, or a url
        # https://github.com/FranciscoMoretti/asciify-color/blob/master/asciify.py
        # https://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python

        with Image.open(filename, 'r') if not(filename.startswith('http://') or filename.startswith('https://')) else Image.open(requests.get(filename, stream=True).raw) as img:
            # default asciiWidth I found online. Aparently over 500 gets laggy
            new_img = parse_image(img, 100)
            print (*new_img, sep='\n')
    except Exception as e:
        print('Exiting with exception', str(e))
