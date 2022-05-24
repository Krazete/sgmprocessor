import re
import UnityPy
from image_processing import file

if __name__ == '__main__':
    phone = UnityPy.load('image_processing/input/palettizedimages')

    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/sprite')

    for sf in phone.assets['palettizedimages'].values():
        if isinstance(sf, UnityPy.files.SerializedFile):
            for k in sf.keys():
                if sf[k].type == 'Texture2D':
                    md = sf[k].read()
                    im = UnityPy.export.Texture2DConverter.get_image_from_texture2d(md)
                    fn = md.read_type_tree()['name']
                    im.save('image_processing/output/sprite/{}.png'.format(fn))
