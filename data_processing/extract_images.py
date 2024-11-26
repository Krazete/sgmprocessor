import UnityPy
from PIL import Image
from data_processing import file
from argparse import ArgumentParser

file.mkdir('data_processing')
file.mkdir('data_processing/output')

apk = UnityPy.load('data_processing/input/base.apk')

def extract_images(query, directory='image', fltr=None, mode='P', first_only=False):
    path = 'data_processing/output/' + directory
    file.mkdir(path)
    file.mkdir(path + '/Sprite')
    file.mkdir(path + '/Texture2D')
    saved = {'Sprite': {}, 'Texture2D': {}}
    for asset in apk.assets:
        for val in asset.values():
            try:
                vtn = val.type.name
                if vtn == 'Sprite' or vtn == 'Texture2D':
                    value = val.read()
                    vn = value.name
                    if query.lower() in vn.lower() and hasattr(value, 'image'):
                        img = value.image
                        if fltr:
                            img = fltr(img)
                        if mode:
                            img = value.image.convert(mode)
                        if vn in saved[vtn]:
                            saved[vtn][vn] += 1
                            img.save('{}/{}/{} ({}).png'.format(path, vtn, vn, saved[vtn][vn]))
                        else:
                            saved[vtn][vn] = 0
                            img.save('{}/{}/{}.png'.format(path, vtn, vn))
                            if first_only:
                                return
            except:
                continue

def getalphawhite(img):
    alpha = img.getchannel(3)
    data = alpha.getdata()
    data2 = [p ** 2 / 256 for p in data]
    alpha.putdata(data2)
    # tan = Image.new('RGBA', img.size, (255, 218, 178, 0))
    white = Image.new('LA', img.size, 255)
    white.putalpha(alpha)
    return white

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-q', '--query', help='filename query')
    parser.add_argument('-o', '--original', action='store_true', help='skip palette mode conversion')
    args = parser.parse_args()
    if args.query:
        extract_images(args.query, mode=None if args.original else 'P')
    else:
        extract_images('MasteryIcon')
        extract_images('character_symbol', fltr=getalphawhite, mode=None)
        # extract_images('bunny', mode=None)
        # extract_images('florence')

        from data_processing.main import get_catalysts
        catalysts = get_catalysts()
        icons = set()
        for i in catalysts:
            icons.add(catalysts[i]['icon'])
        for icon in icons:
            extract_images(icon, 'catalyst', first_only=True)
