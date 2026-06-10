#!/bin/bash

echo "Activating virtual environment..."$'\n'
source venv/Scripts/activate

echo "Processing data..."$'\n'
python -m data_processing.gen_typetrees
python -m data_processing.main
python -m data_processing.loot

echo "Processing images..."$'\n'
python -m image_processing.gen_sprites
python -m image_processing.gen_portraits2
python -m image_processing.gen_portraits4stanley

echo "Moving output files..."$'\n'
python -m update_outputs

echo "Updating HTML versions..."$'\n'
python -m update_versions

echo "Updating SGMPalette directory..."$'\n'
cd ../sgmpalette
python -m update_directory
cd ../sgmprocessor

echo "Updating wiki FighterData module..."$'\n'
python -m update_wiki

echo "Complete. You must manually update patchnote labels for SGM Gallery."
read -p "Press any key to exit." -r -n 1 -s
