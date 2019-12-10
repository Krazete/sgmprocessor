import os
from subprocess import run
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

def save_gif(frames, path, delay=0, show_error=True):
    'Save frames as GIF and attempt to compress results with Gifsicle.'
    frames[0].save(path, save_all=True, append_images=frames[1:], transparency=0, disposal=2, duration=delay, loop=0)
    try:
        run(['gifsicle', path, '-o', path])
    except Exception as message:
        if show_error:
            print('Could not optimize {}: {}.'.format(path, message))

def mkdir(directory):
    'Create directory unless it already exists.'
    if not os.path.exists(directory):
        os.mkdir(directory)
