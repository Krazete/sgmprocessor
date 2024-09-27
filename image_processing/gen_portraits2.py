import os
import re
import UnityPy
from PIL import Image, ImageChops, ImageMath
from image_processing import file
from image_processing.gen_moves import get_mask
from image_processing.portrait_ids import fid, vid

def get_masks():
    palettizedimages = UnityPy.load('image_processing/input/palettizedimages')
    masks = {}
    for key in palettizedimages.container:
        obj = palettizedimages.container[key].read()
        if '_Portrait' in obj.name:
            character = obj.name.split('_')[0]
            masks[character] = get_mask(obj.image, character)
    return masks

def apply_mask(im, mask):
    mask_size = (296, 354) # because black dahlia has a nonstandard mask.size
    scaled_mask = mask.resize((int(dim * 7 / 3) for dim in mask_size), Image.Resampling.LANCZOS)
    a = Image.new('L', im.size)
    a.paste(scaled_mask, (2, 66))
    im.putalpha(a)

if __name__ == '__main__':
    masks = get_masks()

    nonalphanumeric = re.compile('[^a-zA-Z0-9]')
    fid_suffixes = '|'.join([id.split(' ')[-1] for id in fid])
    vid_pattern = re.compile('(?:{})_(.+)_PortraitMarquee_'.format(fid_suffixes))

    dir_input = 'image_processing/input/portrait'
    dir_output = 'image_processing/output/portrait'

    file.mkdir('image_processing/output')
    file.mkdir(dir_output)

    for character in os.listdir(dir_input):
        directory = os.path.join(dir_input, character)
        if os.path.isdir(directory):
            mask = masks[re.sub(nonalphanumeric, '', character)]
            for filename, im in file.iter_img(directory):
                stems = re.findall(vid_pattern, filename)
                if len(stems):
                    variant = re.sub(nonalphanumeric, '', stems[0])
                    file.mkdir(os.path.join(dir_output, fid[character]))
                    apply_mask(im, mask)
                    scale = 300 / im.height
                    scaled_portrait = im.resize((int(dim * scale) for dim in im.size), Image.Resampling.LANCZOS)
                    palettized_portrait = scaled_portrait.convert('P')
                    palettized_portrait.save(os.path.join(dir_output, fid[character], vid[variant] + '.png'))
                else:
                    print('No variant detected in filename:', filename)
