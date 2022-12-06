import UnityPy
from image_processing import file

if __name__ == '__main__':
    palettizedimages = UnityPy.load('image_processing/input/palettizedimages')

    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/sprite')

    for key in palettizedimages.container:
        obj = palettizedimages.container[key].read()
        obj.image.convert('RGB').save('image_processing/output/sprite/{}.png'.format(obj.name))
