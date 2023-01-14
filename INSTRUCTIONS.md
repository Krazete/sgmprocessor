# Preparing Input Data

## I. Retrieve Shallow Data Files

> These files are stored on your phone as is, so retrieving them is easy. Small patches, like translation fixes, likely involve updates to these files.

*If you have an iOS instead of an Android, download [iMazing](https://imazing.com) to access your phone's file system.*

1. Make sure Skullgirls Mobile is installed on your phone and updated from within the app.
2. Connect your phone to your computer and set connection type to File Transfer.
   - MacOS: Download [Android File Transfer](https://android.com/filetransfer) first. When connecting, you may need to open your phone settings, enable Developer Options, and set USB Configuration to MTP (Media Transfer Protocol).
3. Navigate to `Android/data/com.autumn.skullgirls/files`.
   1. Copy `localization` to `data_processing/input`.
   2. Copy `signatureabilities` to `data_processing/input`.
   3. Copy `palettizedimages` to `image_processing/input`.

## II. Retrieve the APK

*If you have an iOS instead of an Android, download the APK from someplace like [APKPure](https://apkpure.com/skullgirls-fighting-rpg/com.autumn.skullgirls) instead. Rename the downloaded APK to `base.apk` and skip this section.*

1. Install the Android Debug Bridge.
   - MacOS: In the Terminal, run `brew install android-platform-tools`.
   - Windows: Download [SDK Platform-Tools](https://developer.android.com/studio/releases/platform-tools.html#downloads) and move the folder `platform-tools` somewhere safe. To give the Command Prompt global access to the adb command, you must also add `platform-tools` to your system PATH:
     1. Open System Settings > System > About.
     2. From the right sidebar, click Advanced System Settings to open System Properties.
     3. In the Advanced tab, click Environment Variables.
     4. Under User Variables, select Path. Click the Edit button.
     5. Click New and enter `C:\WHEREVER_YOU_PLACED_IT\platform-tools`.
2. Connect your phone to your computer, set connection type to File Transfer, and enable debugging.
   1. In your phone settings, open Additional Settings.
   2. Turn on Developer Options, then turn on USB Debugging.
   3. Make sure USB Configuration is set to MTP (Media Transfer Protocol).
3. Open the Command Prompt or Terminal and extract the APK with ADB.
   1. Run `adb devices` to make sure your device is accessible. If the list is empty, recheck the previous step.
   2. Run `adb shell pm list packages -3 -f` to list directories of all APKs.
   3. Find the line with `com.autumn.skullgirls`. Copy the directory path (between `package:` and `/base.apk=com.autumn.skullgirls`).
   4. Navigate to wherever you want the extracted files to go.
   5. Run `adb pull THE_PATH_YOU_JUST_COPIED`. This extracts the folder to your current directory. The extracted folder will contain `base.apk` and `lib`.
4. Copy `base.apk` to `data_processing/input`.

## III. Decompile the APK

1. Install [APKTool](https://ibotpeaches.github.io/Apktool/install).
2. In the Command Prompt or Terminal, navigate to the directory where `base.apk` is located.
3. Enter `apktool d base.apk -f -o base`. This decompiles `base.apk` into the folder named `base`.

## IV. Generate DummyDll

1. Install and open Il2CppDumper.
   - MacOS: Use an [online version of Il2CppDumper](https://il2cppdumper.com).
   - Windows: Download [Il2CppDumper](https://github.com/Perfare/Il2CppDumper). Open `Il2CppDumper.exe`.
2. It will ask for `libil2cpp.so` and then `global-metadata.dat`.
   - `libil2cpp.so` is in `lib/arm64`.
   - `global-metadata.dat` is in `base/assets/bin/Data/Managed/Metadata`.
3. A folder named `DummyDll` will be generated. Move `DummyDll` into `data_processing/input`.

---

# Prerequisites for Running Scripts

## Python

- [Python 3](https://python.org/downloads) is required to run all scripts in this project.

## Installing Libraries

> A virtual environment is recommended so that the required libraries can be installed to this project folder instead of your entire system.

1. Open the Command Prompt or Terminal and navigate to this project folder.
2. Create a virtual environment with `python -m venv venv`.
3. Activate the virtual environment.
   - MacOS: Enter `source venv/bin/activate`.
   - Windows: Enter `venv/Scripts/Activate.ps1`. You may need to enter `Set-ExecutionPolicy Unrestricted -Scope Process` first if there is a security error.
4. Install this project's requirements with `pip install -r requirements.txt`.
   - You can enter `pip freeze` to see the installed libraries.
5. Exit the virtual environment with `deactivate`. The libraries should remain accessible. If they don't, activate the environment again to run any scripts.

## Running Scripts

- If using Visual Studio Code, press `Shift+Enter` to run selected lines.
- If using the Command Prompt or Terminal, navigate to this project folder and enter `python -m FOLDER.SCRIPT` to run the script `FOLDER/SCRIPT.py`.
  - E.g. `python -m data_processing.main`.

---

# Data Processing

## Generate TypeTrees

> TypeTrees are necessary for UnityPy to read the entirety of MonoBehaviour assets. Without it, many important details about fighter variants would be inaccessible.

1. Install [.NET 6.0](https://dotnet.microsoft.com/en-us/download/dotnet/6.0). If you don't know which installer to use, the x64 option is the safest bet.
2. Run `dataprocessing/gen_typetrees.py`. This will create `typetrees.json` in `data_processing/input`.

## Generate Data for SGM Gallery

- Run `data_processing/main.py`.

## Other Scripts

| Script | Function |
| --- | --- |
| `data_processing/common.py` | Extract localizations of common terms. |
| `data_processing/gen_masteryicons.py` | Extract mastery icons. |

---

# Image Processing

## Generate Sprites for SGM Palette

- Run `image_processing/gen_sprites.py`.

## Generate Portraits for SGM Gallery

1. Run `image_processing/gen_masks.py`.
2. Edit the images in `image_processing/output/mask/shadow`.
   - Create a nice silhouette of each portrait.
   - Use `image_processing/input/circle.png` and `image_processing/input/circle2.png` to help with edges.
3. Edit the images in `image_processing/output/mask/color`.
   - Cut out areas that do not contain any information about the portraits' color.
4. Move `mask` into `image_processing/input`.
5. Make sure `image_processing/portrait_ids.py` is up to date with all current variant ids.
6. Run `image_processing/gen_portraits.py`.

## Other Scripts

| Script | Function |
| --- | --- |
| `image_processing/gen_moves.py` | Generate move icons. |
| `image_processing/gen_throbbers.py` | Generate loading GIFs. |

---

# Other Useful Programs

| Program | Note |
| --- | --- |
| [AssetStudio](https://github.com/Perfare/AssetStudio) | AssetStudio the most user-friendly Unity extraction program. |
| [DevX Unity Unpacker](http://devxdevelopment.com/UnityUnpacker) | This program helps in understanding the APK's file structure. It works on MacOS, Windows, and Android. |
| [UnityAssetBundleExtractor](https://github.com/DerPopo/UABE) | This is the program I used before switching to UnityPy. |
| [Pngyu](https://nukesaq88.github.io/Pngyu) | For compressing PNGs. Don't use this on the sprites meant for SGM Palette. |
| [Gifsicle](http://lcdf.org/gifsicle) | For optimizing GIFs. This is an optional prerequisite for `gen_throbbers.py`. |
