import UnityPy
from data_processing import file

file.mkdir('data_processing')
file.mkdir('data_processing/output')

apk = UnityPy.load('data_processing/input/base.apk')

def extract_images(query, directory='image', flatten=True, skip_assets=[]):
    flatpath = 'data_processing/output/' + directory
    file.mkdir(flatpath)
    for asset in apk.assets:
        if asset.name in skip_assets:
            continue
        for val in asset.values():
            if val.type.name == 'Sprite' or val.type.name == 'Texture2D':
                value = val.read()
                if query.lower() in value.name.lower() and hasattr(value, 'image'):
                    path = flatpath
                    if not flatten:
                        path += '/' + asset.name
                        file.mkdir(path)
                    value.image.convert('P').save('{}/{}.png'.format(path, value.name))

if __name__ == '__main__':
    extract_images('MasteryIcon')

    from data_processing.main import get_catalysts
    catalysts = get_catalysts()
    icons = set()
    for i in catalysts:
        icons.add(catalysts[i]['icon'])
    for icon in icons:
        extract_images(icon, 'catalyst', skip_assets=['sharedassets0.assets'])
