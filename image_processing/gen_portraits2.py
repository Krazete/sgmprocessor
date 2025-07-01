import os
import re
import json
import UnityPy
from PIL import Image
from image_processing import file
from image_processing.gen_moves import get_mask
from image_processing.gen_portraits4stanley import gen_stanley

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
    with open('image_processing/input/portrait_cid.json', 'r') as fp:
        cid = json.load(fp)
    with open('image_processing/input/portrait_vid.json', 'r') as fp:
        vid = json.load(fp)
        missing_vid = set(vid.keys())
    masks = get_masks()

    cid_suffixes = '|'.join([id.split(' ')[-1] for id in cid])
    vid_pattern = re.compile('(?:{})_(.+)_PortraitMarquee_'.format(cid_suffixes))

    dir_input = 'image_processing/input/portrait'
    dir_output = 'image_processing/output/portrait'

    file.mkdir('image_processing/output')
    file.mkdir(dir_output)

    for character in os.listdir(dir_input):
        directory = os.path.join(dir_input, character)
        if os.path.isdir(directory):
            mask = masks[re.sub(r'\W|_', '', character)]
            for filename, im in file.iter_img(directory):
                stems = re.findall(vid_pattern, filename)
                if len(stems):
                    variant = re.sub(r'\W|_', '', stems[0])
                    file.mkdir(os.path.join(dir_output, cid[character]))
                    apply_mask(im, mask)
                    scale = 300 / im.height
                    scaled_portrait = im.resize((int(dim * scale) for dim in im.size), Image.Resampling.LANCZOS)
                    palettized_portrait = scaled_portrait.convert('P', colors=128)
                    palettized_portrait.save(os.path.join(dir_output, cid[character], vid[variant] + '.png'))
                    if vid[variant] == 'rCopy':
                        palettized_portrait.save(os.path.join(dir_output, cid[character], vid[variant] + '_.png'))
                    missing_vid.remove(variant)
                else:
                    print('No variant detected in filename:', filename)
    
    if missing_vid:
        print('Missing Variants:')
        for variant in missing_vid:
            print(variant)
    else:
        print('Complete.')
    
    gen_stanley()
