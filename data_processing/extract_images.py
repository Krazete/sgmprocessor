import UnityPy
from data_processing import file

file.mkdir('data_processing')
file.mkdir('data_processing/output')

apk = UnityPy.load('data_processing/input/base.apk')

def extract_images(query, directory='image', mode='P', flatten=True, first_only=False):
    flatpath = 'data_processing/output/' + directory
    file.mkdir(flatpath)
    saved = {}
    for asset in apk.assets:
        for val in asset.values():
            if val.type.name == 'Sprite' or val.type.name == 'Texture2D':
                value = val.read()
                if query.lower() in value.name.lower() and hasattr(value, 'image'):
                    img = value.image
                    if mode:
                        img = value.image.convert(mode)
                    path = flatpath
                    if not flatten:
                        path += '/' + asset.name
                        file.mkdir(path)
                    if value.name in saved:
                        saved[value.name] += 1
                        img.save('{}/{} ({}).png'.format(path, value.name, saved[value.name]))
                    else:
                        saved[value.name] = 0
                        img.save('{}/{}.png'.format(path, value.name))
                        if first_only:
                            return

if __name__ == '__main__':
    extract_images('MasteryIcon')
    extract_images('bunny', mode=False)

    from data_processing.main import get_catalysts
    catalysts = get_catalysts()
    icons = set()
    for i in catalysts:
        icons.add(catalysts[i]['icon'])
    for icon in icons:
        extract_images(icon, 'catalyst', first_only=True)
