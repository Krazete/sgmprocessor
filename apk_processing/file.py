import os
import json
from shutil import copyfile, rmtree

def iter_json_dir(directory, show_error=False):
    'Generate all valid JSON files in given directory.'
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), encoding='utf-8') as file:
            try:
                stem = os.path.splitext(filename)[0]
                content = json.load(file)
                yield stem, content
            except Exception as message:
                if show_error:
                    print('Error opening {}: {}.'.format(filename, message))

def load(directory, is_mono_dir=False):
    'Build python object from JSON file directory.'
    obj = {}
    for stem, content in iter_json_dir(directory):
        if is_mono_dir:
            substem = stem.split('-')
            obj.setdefault(substem[1], {})
            obj[substem[1]].setdefault(substem[2], content)
        else:
            obj.setdefault(stem, content)
    return obj

def save(obj, path, pretty=True):
    'Save python object to JSON file.'
    with open(path, 'w') as file:
        if pretty:
            json.dump(obj, file, indent=4, separators=(',', ': '), sort_keys=True)
        else:
            json.dump(obj, file, sort_keys=True)

def copy(src, dst, show_error=False):
    'Copy a file.'
    try:
        copyfile(src, dst)
    except FileNotFoundError:
        if show_error:
            print('FileNotFoundError:', src, ' to ', dst)

def resetdir(path):
    if os.path.exists(path):
        rmtree(path)
    os.mkdir(path)
