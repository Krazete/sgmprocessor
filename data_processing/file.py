import os
import json
from shutil import rmtree

def iter_json(directory, show_error=False):
    'Generate labeled objects from JSON files of the specified directory.'
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), encoding='utf-8') as file:
            try:
                stem = os.path.splitext(filename)[0]
                content = json.load(file)
                yield stem, content
            except Exception as message:
                if show_error:
                    print('Error opening {}: {}.'.format(filename, message))

def load(directory, is_monobehaviour=False):
    'Build object from the JSON file directory.'
    data = {}
    for stem, content in iter_json(directory):
        if is_monobehaviour:
            substem = stem.split('-')
            data.setdefault(substem[1], {})
            data[substem[1]].setdefault(substem[2], content)
        else:
            data.setdefault(stem, content)
    return data

def save(data, path, pretty=False):
    'Save object as a JSON file.'
    with open(path, 'w') as file:
        if pretty:
            json.dump(data, file, indent=4, separators=(',', ': '), sort_keys=True)
        else:
            json.dump(data, file, sort_keys=True)

def rmkdir(directory):
    'Delete directory if it exists, then create directory with the same name.'
    if os.path.exists(directory):
        rmtree(directory)
    os.mkdir(directory)
