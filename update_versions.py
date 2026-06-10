import re

with open('data_processing/output/version.txt', 'r') as fp:
    version = fp.read()

pages = [
    'sgm/artifacts',
    'sgm/assists',
    'sgm/catalysts',
    'sgm/index',
    'sgm/moves',
    'sgm/ratings',
    'sgmpalette/index'
]

for page in pages:
    with open('../{}.html'.format(page), 'r+', encoding='utf-8') as fp:
        old = fp.read()
        new = re.sub(
            r'>(\d+\.\d+\.\d+)<',
            '>{}<'.format(version),
            old
        )
        fp.seek(0)
        fp.write(new)
