from image_processing import file
from PIL import ImageMath

def petrify_sprite(im, spectral_ids=[]):
    'Returns grayscale version of codified sprite, with spectral areas rendered translucent.'
    r = im.getchannel(0) # palette
    g = im.getchannel(1) # linework
    b = im.getchannel(2) # detail

    # mask detail with palette areas and subtract inverted linework
    sprite = ImageMath.eval('convert((r > 0) * b - (0xFF - g), "L")', r=r, g=g, b=b)

    if len(spectral_ids):
        spectral_areas = ' + '.join('(r == {})'.format(id) for id in spectral_ids)
        # create scaled binary mask of palette areas minus spectral areas
        opaque = ImageMath.eval('convert(0xFF * (r > 0) * (1 - (' + spectral_areas + ')), "L")', r=r)
        # mask detail with spectral areas and scale to adjust intensity
        translucent = ImageMath.eval('convert(0xFF * (b * (' + spectral_areas + ') - 0x64) / (0xFF - 0x64), "L")', r=r, b=b)
        # add together opaque mask, translucent mask, and inverted linework
        a = ImageMath.eval('convert(o + t + (0xFF - g), "L")', o=opaque, t=translucent, g=g)
    else:
        # create scaled binary mask of palette areas and add inverted linework
        a = ImageMath.eval('convert(0xFF * (r > 0) + (0xFF - g), "L")', r=r, g=g)

    sprite.putalpha(a)
    return sprite

if __name__ == '__main__':
    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/moves')

    for filename, im in file.iter_img('image_processing/input/Sprite'):
        if '_BB' in filename or '_SM' in filename:
            spectral_ids = []
            if 'Beowulf_' in filename:
                spectral_ids = [0xEC]
            elif 'Cerebella_' in filename:
                spectral_ids = [0xB7]
            elif 'Eliza_' in filename:
                spectral_ids = [0xED]
            elif 'Parasoul_' in filename:
                spectral_ids = [0xCF]
            elif 'RoboFortune_' in filename:
                spectral_ids = [0xE4, 0xD2, 0xD7, 0xDF]
            elif 'Squigly_' in filename:
                spectral_ids = [0xCE]
            sprite = petrify_sprite(im, spectral_ids)
            sprite.save('image_processing/output/moves/' + filename)
