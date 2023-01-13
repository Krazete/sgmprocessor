import UnityPy
from data_processing import file

file.mkdir('data_processing')
file.mkdir('data_processing/output')
file.mkdir('data_processing/output/image')

apk = UnityPy.load('data_processing/input/base.apk')

def extract_images(filter):
    for asset in apk.assets:
        for val in asset.values():
            if val.type.name == 'Sprite' or val.type.name == 'Texture2D':
                value = val.read()
                if filter in value.name and hasattr(value, 'image'):
                    value.image.convert('P').save('data_processing/output/image/{}.png'.format(value.name))

if __name__ == '__main__':
    extract_images('MasteryIcon')
