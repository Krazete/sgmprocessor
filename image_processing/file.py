import os
from PIL import Image

def iter_img(directory, show_error=False):
    'Generate all valid image files from given directory.'
    for filename in os.listdir(directory):
        try:
            im = Image.open(os.path.join(directory, filename))
            yield filename, im
        except Exception as message:
            if show_error:
                print('Error opening {}: {}.'.format(filename, message))

def mkdir(directory):
    'Create directory unless it already exists.'
    if not os.path.exists(directory):
        os.mkdir(directory)
