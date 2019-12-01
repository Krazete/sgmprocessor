import os
from PIL import Image, ImageChops

def iter_p(directory, show_error=False):
    for filename in os.listdir(directory):
        try:
            yield Image.open(os.path.join(directory, filename)), filename
        except Exception as message:
            if show_error:
                print('Error opening {}: {}.'.format(filename, message))

if __name__ == '__main__':
    bigder = 'source/Art Capture'
    for dirname in os.listdir(bigder):
        directory = os.path.join(bigder, dirname)
        if os.path.isdir(directory):
            p = None
            k = None
            for im, filename in iter_p(directory):
                if '_PortraitMarquee_' in filename:
                    if not p or not k:
                        p = im
                        k = im
                    p = ImageChops.lighter(p, im)
                    k = ImageChops.screen(k, im)
            p.save('data/masks/raw/' + dirname + '.png')
            k.save('data/masks/thin/' + dirname + '.png')
