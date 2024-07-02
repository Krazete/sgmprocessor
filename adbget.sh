#!/bin/bash

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
