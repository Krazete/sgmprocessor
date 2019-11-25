import os
from PIL import Image, ImageMath

def iter_p(directory, show_error=False):
    for filename in os.listdir(directory):
        try:
            yield Image.open(os.path.join(directory, filename)), filename
        except Exception as message:
            if show_error:
                print('Error opening {}: {}.'.format(filename, message))

def dothings(im, filename, liquids):
    r = im.getchannel(0) # palette
    g = im.getchannel(1) # linework
    b = im.getchannel(2) # detail

    i = ImageMath.eval('convert((r > 0) * b - (0xFF - g), "L")', r=r, g=g, b=b)

    if len(liquids):
        liquidareas = ' + '.join('(r == {})'.format(liq) for liq in liquids)
        kkk = ImageMath.eval('convert(0xFF * (r > 0) * (1 - (' + liquidareas + ')), "L")', r=r)
        lll = ImageMath.eval('convert(0xFF * (b * (' + liquidareas + ') - 0x64) / (0xFF - 0x64), "L")', r=r, b=b)
        a = ImageMath.eval('convert(kkk + lll + (0xFF - g), "L")', kkk=kkk, lll=lll, g=g)
    else:
        a = ImageMath.eval('convert(0xFF * (r > 0) + (0xFF - g), "L")', r=r, g=g)

    i.putalpha(a)
    i.save('data/' + filename)

for im, filename in iter_p('source/Sprite'):
    if '_BB' in filename or '_SM' in filename:
        liquids = []
        if 'Beowulf_' in filename:
            liquids = [0xEC]
        elif 'Cerebella_' in filename:
            liquids = [0xB7]
        elif 'Eliza_' in filename:
            liquids = [0xED]
        elif 'Parasoul_' in filename:
            liquids = [0xCF]
        elif 'RoboFortune_' in filename:
            liquids = [0xE4, 0xD2, 0xD7, 0xDF]
        elif 'Squigly_' in filename:
            liquids = [0xCE]

        dothings(im, filename.lower(), liquids)
