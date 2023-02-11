import UnityPy
from PIL import Image, ImageMath
from image_processing import file

spectral_log = {
    'Annie': [47, 48, 49],
    'Beowulf': [61],
    'BigBand': [53],
    'BlackDahlia': [47, 62, 64],
    'Cerebella': [34],
    'Eliza': [66],
    'Fukua': [27, 28],
    'Parasoul': [37],
    'RoboFortune': [49, 50, 52, 53],
    'Squigly': [43],
    'Umbrella': [35, 36, 47]
}

def petrify_sprite(im, spectral_ids=[]):
    'Return grayscale version of codified sprite, with spectral areas rendered translucent.'
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
    palettizedimages = UnityPy.load('image_processing/input/palettizedimages')

    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/move')

    for key in palettizedimages.container:
        obj = palettizedimages.container[key].read()
        if '_BB' in obj.name or '_SM' in obj.name:
            name_prefix = obj.name.split('_')[0]
            spectral_ids = spectral_log.get(name_prefix, [])
            sprite = petrify_sprite(obj.image, spectral_ids)
            scale = 140 / sprite.width # because of image resolution difference between old and new sprites
            scaled_sprite = sprite.resize((int(dim * scale) for dim in sprite.size), Image.Resampling.LANCZOS)
            palettized_sprite = scaled_sprite.convert('RGBA').convert('P') # intermediate RGBA conversion preserves transparency
            palettized_sprite.save('image_processing/output/move/{}.png'.format(obj.name.lower()))
