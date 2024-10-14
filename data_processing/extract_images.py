import UnityPy
from data_processing import file
from argparse import ArgumentParser

file.mkdir('data_processing')
file.mkdir('data_processing/output')

apk = UnityPy.load('data_processing/input/base.apk')

def extract_images(query, directory='image', mode='P', first_only=False):
    path = 'data_processing/output/' + directory
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

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-q', '--query', help='filename query')
    args = parser.parse_args()
    if args.query:
        extract_images(args.query)
    else:
        extract_images('florence')
        extract_images('MasteryIcon')
        extract_images('character_symbol')
        extract_images('bunny', mode=False)

        from data_processing.main import get_catalysts
        catalysts = get_catalysts()
        icons = set()
        for i in catalysts:
            icons.add(catalysts[i]['icon'])
        for icon in icons:
            extract_images(icon, 'catalyst', first_only=True)
