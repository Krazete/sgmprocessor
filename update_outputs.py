import os
import shutil
import re

srcs = [
    'data_processing/output/sgm',
    'data_processing/output/sgmodds',
    'image_processing/output/sgm',
    'image_processing/output/sgmpalette'
]

for src in srcs:
    for root, _, files in os.walk(src):
        for file in files:
            dstroot = re.sub(r'^\w+_processing/output', '..', root)
            os.replace(
                os.path.join(root, file),
                os.path.join(dstroot, file),
            )
    shutil.rmtree(src, ignore_errors=True)
