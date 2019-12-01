import os
from PIL import Image

def iter_img_dir(directory, show_error=False):
    'Generate all valid image files from given directory.'
    for filename in os.listdir(directory):
        try:
            im = Image.open(os.path.join(directory, filename))
            yield filename, im
        except Exception as message:
            if show_error:
                print('Error opening {}: {}.'.format(filename, message))
