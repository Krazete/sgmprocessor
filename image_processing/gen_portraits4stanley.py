import os
import re
import json
from PIL import Image
from image_processing import file

def gen_stanley():
    with open('image_processing/input/portrait_cid.json', 'r') as fp:
        cid = json.load(fp)
    with open('image_processing/input/portrait_vid.json', 'r') as fp:
        vid = json.load(fp)

    cid_suffixes = '|'.join([id.split(' ')[-1] for id in cid])
    vid_pattern = re.compile('(?:{})_(.+)_PortraitMarquee_'.format(cid_suffixes))

    dir_input = 'image_processing/input/portrait'
    dir_output = 'image_processing/output/stanley'

    file.mkdir('image_processing/output')
    file.mkdir(dir_output)

    for character in os.listdir(dir_input):
        directory = os.path.join(dir_input, character)
        if os.path.isdir(directory):
            for filename, im in file.iter_img(directory):
                stems = re.findall(vid_pattern, filename)
                if len(stems):
                    variant = re.sub(r'\W|_', '', stems[0])
                    file.mkdir(os.path.join(dir_output, cid[character]))
                    scale = 150 / im.height
                    scaled_portrait = im.resize((int(dim * scale) for dim in im.size), Image.Resampling.LANCZOS)
                    palettized_portrait = scaled_portrait.convert('P', colors=128)
                    palettized_portrait.save(os.path.join(dir_output, cid[character], vid[variant] + '.png'))
                    if vid[variant] == 'rCopy':
                        palettized_portrait.save(os.path.join(dir_output, cid[character], vid[variant] + '_.png'))
