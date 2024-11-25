import UnityPy
from PIL import Image, ImageMath
from image_processing import file

spectral_log = {
    'Annie': [47, 48, 49],
    'Beowulf': [61],
    'BigBand': [53],
    'BlackDahlia': [47, 62, 64],
    'BrainDrain': [45],
    'Cerebella': [34],
    'Eliza': [66],
    'Fukua': [27, 28],
    "Marie": [50, 51, 54],
    'Minette': [72],
    'Parasoul': [37],
    'RoboFortune': [49, 50, 52, 53],
    'Squigly': [43],
    'Umbrella': [35, 36, 47],
    "Valentine": [38] # not necessary; only used in Final Fang card art
}

def get_mask(im, character=None):
    'Return mask of sprite, with spectral areas rendered translucent.'
    r = im.getchannel(0) # palette
    g = im.getchannel(1) # linework
    b = im.getchannel(2) # detail

    spectral_ids = spectral_log.get(character, [])
    if len(spectral_ids):
        # create scaled binary mask of palette areas minus spectral areas
        opaque = ImageMath.lambda_eval(
            lambda _: _['convert'](0xFF * (_['r'] > 0) * (1 - sum(_['r'] == id for id in spectral_ids)), 'L'),
            r=r
        )
        # mask detail with spectral areas and scale to adjust intensity
        translucent = ImageMath.lambda_eval(
            lambda _: _['convert'](0xFF * (_['b'] * sum(_['r'] == id for id in spectral_ids) - 0x64) / (0xFF - 0x64), 'L'),
            r=r, b=b
        )
        # add together opaque mask, translucent mask, and inverted linework
        a = ImageMath.lambda_eval(
            lambda _: _['convert'](_['o'] + _['t'] + (0xFF - _['g']), 'L'),
            o=opaque, t=translucent, g=g
        )
    else:
        # create scaled binary mask of palette areas and add inverted linework
        a = ImageMath.lambda_eval(
            lambda _: _['convert'](0xFF * (_['r'] > 0) + (0xFF - _['g']), 'L'),
            r=r, g=g
        )

    return a

def petrify_sprite(im, character=None):
    'Return grayscale version of sprite.'
    r = im.getchannel(0) # palette
    g = im.getchannel(1) # linework
    b = im.getchannel(2) # detail

    # mask detail with palette areas and subtract inverted linework
    sprite = ImageMath.lambda_eval(
        lambda _: _['convert']((_['r'] > 0) * _['b'] - (0xFF - _['g']), 'L'),
        r=r, g=g, b=b
    )
    # apply mask
    a = get_mask(im, character)
    sprite.putalpha(a)

    return sprite

if __name__ == '__main__':
    palettizedimages = UnityPy.load('image_processing/input/palettizedimages')

    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/move')

    for key in palettizedimages.container:
        obj = palettizedimages.container[key].read()
        if '_BB' in obj.name or '_SM' in obj.name or '_AM' in obj.name:
            character = obj.name.split('_')[0]
            sprite = petrify_sprite(obj.image, character)
            scale = 140 / sprite.width # because of image resolution difference between old and new sprites
            scaled_sprite = sprite.resize((int(dim * scale) for dim in sprite.size), Image.Resampling.LANCZOS)
            palettized_sprite = scaled_sprite.convert('RGBA').convert('P') # intermediate RGBA conversion preserves transparency
            palettized_sprite.save('image_processing/output/move/{}.png'.format(obj.name.lower()))
