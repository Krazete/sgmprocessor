import re
from image_processing import file

if __name__ == '__main__':
    pattern = re.compile('(.*)_\d+\.png')
    gifs = {}

    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/idle')

    for filename, im in file.iter_img('image_processing/input/Sprite'): # todo: eliminate dependence on AssetStudio (switch to UnityPy)
        stems = re.findall(pattern, filename)
        if len(stems):
            stem = stems[0]
            gifs.setdefault(stem, [])
            if 'shelldag' in stem:
                im = im.rotate(270, expand=True)
            gifs[stem].append(im.convert('RGB', dither=False))

    for stem in gifs:
        file.save_gif(gifs[stem], 'image_processing/output/idle/' + stem + '.gif', 200)
