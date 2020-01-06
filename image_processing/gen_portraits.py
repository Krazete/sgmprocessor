import os
import re
from PIL import Image, ImageOps, ImageChops
from image_processing import file
from image_processing.portrait_ids import fid, vid

if __name__ == '__main__':
    pattern = re.compile('_(.+)_PortraitMarquee_')
    scale = 3 / 10

    dir_shadow = 'image_processing/input/mask/shadow'
    dir_color = 'image_processing/input/mask/color'
    dir_portrait = 'image_processing/output/portrait'

    file.mkdir('image_processing/output')
    file.mkdir(dir_portrait)

    capture = 'image_processing/input/Art Capture'
    for character in os.listdir(capture):
        directory = os.path.join(capture, character)
        if os.path.isdir(directory):
            # load masks
            shadow = Image.open(os.path.join(dir_shadow, character + '.png'))
            color = Image.open(os.path.join(dir_color, character + '.png'))
            # get mask alpha channels
            s = shadow.convert('LA').getchannel(1)
            c = color.convert('LA').getchannel(1)
            for filename, im in file.iter_img(directory):
                stems = re.findall(pattern, filename)
                if len(stems):
                    # mask colors with c and mask alpha with s
                    portrait = ImageChops.subtract(im, ImageOps.invert(c).convert('RGBA'))
                    portrait.putalpha(s)
                    scaled_portrait = portrait.resize((int(dim * scale) for dim in portrait.size))
                    # save with ids instead of names
                    variant = re.sub('[^a-zA-Z0-9 -_!]', '_', stems[0])
                    file.mkdir(os.path.join(dir_portrait, fid[character]))
                    scaled_portrait.save(os.path.join(dir_portrait, fid[character], vid[variant] + '.png'))
