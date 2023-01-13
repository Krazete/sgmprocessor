from PIL import ImageOps
from image_processing import file

def dichotimize_gif(im):
    'Return frames of GIF converted to black and white and inverted.'
    frames = []
    for i in range(im.n_frames):
        im.seek(i)
        bw = im.convert('1', dither=False)
        frame = ImageOps.invert(bw.convert('L'))
        frames.append(frame)
    return frames

if __name__ == '__main__':
    file.mkdir('image_processing/output')
    file.mkdir('image_processing/output/throbber')

    for filename, im in file.iter_img('image_processing/input/throbber'):
        if filename.split('.')[-1] == 'gif':
            frames = dichotimize_gif(im)
            file.save_gif(frames, 'image_processing/output/throbber/' + filename)
