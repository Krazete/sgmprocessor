from image_processing import file
from subprocess import run
from PIL import ImageOps

def dichotimize_gif(im):
    'Returns frames of GIF converted to black and white and inverted.'
    frames = []
    for i in range(1000000):
        try:
            im.seek(i)
            bw = im.convert('1', dither=False)
            frame = ImageOps.invert(bw.convert('L'))
            frames.append(frame)
        except:
            break
    return frames

def save_gif(frames, path, show_error=False):
    'Saves frames as GIF and attempts to compress results with Gifsicle.'
    frames[0].save(path, save_all=True, append_images=frames[1:], transparency=0, disposal=2)
    try:
        run(['gifsicle', path, '-o', path])
    except Exception as message:
        if show_error:
            print('Could not optimize {}: {}.'.format(path, message))

if __name__ == '__main__':
    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/throbber')

    for filename, im in file.iter_img('image_processing/input/throbber'):
        if filename.split('.')[-1] == 'gif':
            frames = dichotimize_gif(im)
            save_gif(frames, 'image_processing/output/throbber/' + filename, True)
