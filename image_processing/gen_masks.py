import os
from PIL import ImageChops
from image_processing import file

def get_lightest(im):
    'Return lightest channel values and the alpha channel of an image.'
    rg = ImageChops.lighter(im.getchannel(0), im.getchannel(1))
    rgb = ImageChops.lighter(rg, im.getchannel(2))
    a = im.getchannel(3)
    return rgb, a

def get_double(im):
    'Return image with doubled intensity and a mask2 mask made from it.'
    b = ImageChops.add(im, im)
    return b, b.convert('1', dither=False)

if __name__ == '__main__':
    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/mask')
    file.mkdir('image_processing/output/mask/shadow')
    file.mkdir('image_processing/output/mask/color')

    capture = 'image_processing/input/portrait'
    for character in os.listdir(capture):
        directory = os.path.join(capture, character)
        if os.path.isdir(directory):
            mask = None
            alpha = None
            for filename, im in file.iter_img(directory):
                if '_PortraitMarquee_' in filename:
                    gray, a = get_lightest(im)
                    if not mask or not alpha:
                        mask = gray
                        alpha = a
                    else:
                        mask = ImageChops.lighter(mask, gray)
                        alpha = ImageChops.lighter(alpha, a)
            mask.putalpha(alpha)
            mask.save('image_processing/output/mask/shadow/' + character + '.png')
            mask2, alpha2 = get_double(mask)
            mask2.putalpha(alpha2)
            mask2.save('image_processing/output/mask/color/' + character + '.png')
