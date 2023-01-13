# **UNDER CONSTRUCTION**

(This document was already outdated, but SGM 5.2.0 broke UABE and made the data section completely useless.)

Also, Atom is being sunset (goodbye Hydrogen, you were the best). So I'll take this opportunity to start using virtual environments finally.

> `python -m venv venv`  
> MAC: `source venv/bin/activate`  
> WIN: `venv/Scripts/Activate.ps1`  
> if security error: `Set-ExecutionPolicy Unrestricted -Scope Process`  
> `pip install -r requirements.txt`  
> `deactivate`
> 
> VSCODE: select all then press Shift+Enter (don't run, it'll use the wrong working folder)  

I'll refine those instructions later.

> `pip freeze > requirements.txt`

# Prepare Input Data

## N. (For MacOS) Install Windows

Il2CppDumper only runs on Windows. You must install a Windows machine via dual boot or VirtualBox. If using VirtualBox,  o you must install a Windows machine if you are working on a Mac.

| Download | Link |
| --- | --- |
| VirtualBox | https://www.virtualbox.org/wiki/Downloads |
| Windows 10 ISO | https://www.microsoft.com/en-us/software-download/windows10ISO |

1. In VirtualBox, create a new Windows 10 Virtual Machine (WVM).
2. In the WVM Settings window, create a Shared Folder.
3. With the WVM open, click `Devices` in the Mac menu bar and select `Insert Guest Additions CD Image...`. This enables the Shared Folder, allowing you to transfer files between the WVM and your Mac.

## I. Retrieve the APK

You must have an Android phone with Skullgirls Mobile installed first.

1. Download the Android Debug Bridge.
   - Windows: Download [SDK Platform-Tools](https://developer.android.com/studio/releases/platform-tools.html#downloads) and move the folder `platform-tools` somewhere safe. To give the Command Prompt global access to the adb command, you must also add `platform-tools` to your system PATH:
     1. Open System Settings > System > About.
     2. From the right sidebar, click Advanced System Settings to open System Properties.
     3. In the Advanced tab, click Environment Variables.
     4. Under User Variables, select Path. Click the Edit button.
     5. Click New and enter `C:\WHEREVER_YOU_PLACED_IT\platform-tools`.
   - MacOS: In the Terminal, run `brew install android-platform-tools`.
2. Connect your phone to your computer and enable debugging.
   1. In your phone settings, open Additional Settings.
   2. Turn on Developer Options, then turn on USB Debugging.
   3. You may also need to change Select USB Configuration to MTP (Media Transfer Protocol).
3. Open the Command Prompt or Terminal and extract the APK with ADB.
   1. Run `adb devices` to make sure your device is accessible. If the list is empty, redo the previous step.
   2. Run `adb shell pm list packages -3 -f` to list directories of all APKs.
   3. Find the line with `com.autumn.skullgirls`. Copy the directory path (between `package:` and `/base.apk=com.autumn.skullgirls`).
   4. Navigate to wherever you want the extracted files to go.
   5. Run `adb pull THE_PATH_YOU_JUST_COPIED`. This extracts the folder to your current directory.

Alternatively, you can try downloading the APK from someplace like [APKPure](https://apkpure.com/skullgirls-fighting-rpg/com.autumn.skullgirls). This isn't guaranteed to be the latest version though, and it may lack some necessary internal files required for Il2CppDumper and UnityPy.

## II. Decompile the APK

1. Install [APKTool](https://ibotpeaches.github.io/Apktool/install).
2. Open Notepad, paste the following, and save it as `decode_apks.bat`.
    ```bat
    for %%f in (*.apk) do (
        apktool d "%%~nf.apk" -f -o "%%~nf"
    )
    ```
3. Place `decode_apks.bat` in the same folder as the APK file(s).
3. Open `decode_apks.bat`. This generates folders each named after the APK from which they were decompiled.

## III. Generate DummyDll

To read MonoBehaviour assets, UnityPy (and AssetStudio and UABE) need these files.

1. Download [Il2CppDumper](https://github.com/Perfare/Il2CppDumper).
2. Open Il2CppDumper. It will ask for `libil2cpp.so` and `global-metadata.dat`.
   - `libil2cpp.so` is in `lib/arm64`.
   - `global-metadata.dat` is in `base/assets/bin/Data/Managed/Metadata`.
3. A folder named `DummyDll` will be generated. Move `DummyDll` into `data_processing/input`.

This is currently the only step which requires a Windows machine. If you need it, 

## OV. Phone Data

5. Get a phone which has the Skullgirls Mobile app downloaded and updated.
6. Copy the `com.autumn.skullgirls` folder from your phone. For Android, this is located in `Android/data`. For iPhone, you need a program like [iMazing](https://imazing.com) to extract this folder from the app.
6. Get `localization`, `signatureabilities`, and `palettizedimages`.

---

# Processing Input Data

If an `ImportError` occurs for any `.py` file, modify each script so the line `from *_processing import file` becomes just `import file`.

## I. Generate Gallery Data

| Download | Link |
| --- | --- |
| Python 3 | https://www.python.org/downloads |

3. Run `data_processing/main.py`.
4. For localizations of common terms, run `data_processing/common.py`.

## II. Generate Portraits

| Download | Link |
| --- | --- |
| Pillow | https://pillow.readthedocs.io/en/stable/installation.html |

2. Run `image_processing/gen_masks.py`.
3. Edit the images in `image_processing/output/mask/shadow`. Create a nice silhouette of each portrait, using `image_processing/input/circle.png` and `image_processing/input/circle2.png` to help with edges.
3. Edit the images in `image_processing/output/mask/color`. Cut out areas that do not contain any information about the portraits' color.
4. Move `mask` into `image_processing/input`.
5. Ensure `image_processing/portrait_ids.py` is up-to-date.
6. Run `image_processing/gen_portraits.py`.

## III. Generate Move Icons

1. Move `Sprite` (extracted from your phone data) into `image_processing/input`.
2. Run `image_processing/gen_moves.py`.

## V. Generate Loading GIFs

2. Run `image_processing/gen_throbbers.py`.

## V. Other Useful Programs

| Download | Link | Notes |
| --- | --- | --- |
| Visual C++ 2010 | https://www.microsoft.com/en-us/download/details.aspx?id=14632 |
| AssetStudio | https://github.com/Perfare/AssetStudio | AssetStudio is used for extracting most files because it's easier to use and it organizes its exported assets by type. |
| DevX Unity Unpacker | http://devxdevelopment.com/UnityUnpacker | With DevX, open `sgm.apk`. This program helps in understanding the file structure of the APK and does not require a Windows machine. |
| UnityAssetBundleExtractor | https://github.com/DerPopo/UABE | |
| Pngyu | https://nukesaq88.github.io/Pngyu | Do not compress the `Sprite` extracted from your phone data. |
| Gifsicle | http://www.lcdf.org/gifsicle | If you want optimized GIFs, install Gifsicle by following instructions found on its GitHub repository. |
| Latest APK | https://apkpure.com/skullgirls/com.autumn.skullgirls |
