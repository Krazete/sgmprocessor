import os
from itertools import combinations
from PIL import ImageChops
from image_processing import file

if __name__ == '__main__':
    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/masks')
    file.mkdir('image_processing/output/masks/raw')
    file.mkdir('image_processing/output/masks/thin')

    p = {}

    capture = 'image_processing/input/Art Capture'
    for character in os.listdir(capture):
        p.setdefault(character, [])
        directory = os.path.join(capture, character)
        if os.path.isdir(directory):
            # p = None
            # k = None
            for filename, im in file.iter_img(directory):
                if '_PortraitMarquee_' in filename:
                    p[character].append(im)
            #         if not p or not k:
            #             p = im
            #             k = im
            #         p = ImageChops.lighter(p, im)
            #         k = ImageChops.screen(k, im)
            # p.save('image_processing/output/masks/raw/' + character + '.png')
            # k.save('image_processing/output/masks/thin/' + character + '.png')




lor = None
land = None
for a, b in combinations(p['Peacock'], 2):
    bina = i.convert('1', dither=False)
    binb = j.convert('1', dither=False)
    aorb = ImageChops.logical_or(bina, binb)
    aandb = ImageChops.logical_and(bina, binb)
    if not lor or not land:
        lor = aorb
        land = aandb
    else:
        lor = ImageChops.lighter(lor, aorb)
        land = ImageChops.lighter(land, aandb)
lor.save('image_processing/output/masks/raw/Peacock.png')
land.save('image_processing/output/masks/raw/Peacock2.png')
