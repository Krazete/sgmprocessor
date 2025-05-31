#!/bin/bash

read -p "Delete base and DummyDll? (y/n)"$'\n' delbad
if [[ $delbad == [Yy] ]]; then
    rm -r data_processing/input/base
    rm -r data_processing/input/DummyDll
    echo "Folders deleted."
else
    echo "Folders retained."
fi

adb start-server
read -p "Press any key to start."$'\n' -r -n 1 -s

phone=sdcard/Android/data/com.autumn.skullgirls/files/
dp=data_processing/input/
ip=image_processing/input/

mkdir -p $dp
mkdir -p $ip

pkglist=$(adb shell pm list packages -3 -f)
while IFS=$'\t\r\n' read -r line; do
    if [[ $line =~ package:(.+com\.autumn\.skullgirls.+/) ]]; then
        pkg=${BASH_REMATCH[1]}
        adb pull -a $pkg"base.apk" $dp"base.apk"
        adb pull $pkg"lib"
        mv lib/arm64/libil2cpp.so $dp"libil2cpp.so"
        rm -r lib
        # todo: integrate apktool
        # todo: integrate il2cppdumper
        break
    fi
done <<< "$pkglist"

adb pull -a $phone"localization" $dp"localization"
adb pull -a $phone"signatureabilities" $dp"signatureabilities"

adb pull -a $phone"palettizedimages" $ip"palettizedimages"

# unused extra stuff
adb pull -a $phone"cosmetics" $ip"cosmetics"
adb pull -a $phone"liveops" $ip"liveops"
adb pull -a $phone"talkingheads" $ip"talkingheads"

echo "Extraction complete."
read -p "Press any key to exit." -r -n 1 -s
