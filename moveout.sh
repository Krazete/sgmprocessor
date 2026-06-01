#!/bin/bash

echo "Moving output files..."$'\n'

mv data_processing/output/sgm/* ../sgm
mv data_processing/output/sgmodds/* ../sgmodds
mv image_processing/output/sgm/* ../sgm
mv image_processing/output/sgmpalette/* ../sgmpalette

echo $'\n'"Cleaning up..."$'\n'

rmdir data_processing/output/sgm
rmdir data_processing/output/sgmodds
rmdir image_processing/output/sgm
rmdir image_processing/output/sgmpalette

echo $'\n'"Complete."
read -p "Press any key to exit." -r -n 1 -s
