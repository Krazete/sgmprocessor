import re
import UnityPy
from image_processing import file

phone = UnityPy.load('image_processing/input/palettizedimages')

def all_assets(bundle):
    for sf in phone.assets[bundle].values():
        if isinstance(sf, UnityPy.files.SerializedFile):
            for k in sf.keys():
                yield k, sf[k]

def get_phonebook():
    index = {}
    for pid, obj in all_assets('palettizedimages'):
        index[pid] = obj
    return index

phonebook = get_phonebook()

for asset in all_assets('palettizedimages'):
    if phonebook[asset[0]].type == "Texture2D":
        var = phonebook[asset[0]]
        tx = var.read()
        im = UnityPy.export.Texture2DConverter.get_image_from_texture2d(tx)
        fn = tx.read_type_tree()['name']
        im.save('image_processing/output/sprite/' + fn + '.png')
