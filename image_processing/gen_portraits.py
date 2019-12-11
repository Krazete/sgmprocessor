import os
from PIL import Image, ImageOps
from image_processing import file

if __name__ == '__main__':
    shadow = 'image_processing/input/shadow'
    color = 'image_processing/input/color'

    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/portrait')

    capture = 'image_processing/input/Art Capture'
    for character in os.listdir(capture):
        directory = os.path.join(capture, character)
        if os.path.isdir(directory):
            for filename, im in file.iter_img(directory):
                if '_PortraitMarquee_' in filename:
                    im.save('image_processing/output/portrait/' + filename)
