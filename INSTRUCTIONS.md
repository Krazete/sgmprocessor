# Obtaining Input Data

## N. (For MacOS) Install Windows

Sections II-IV require programs that only run on Windows, so you must install a Windows machine if you are working on a Mac.

| Download | Link |
|---|---|
| VirtualBox | https://www.virtualbox.org/wiki/Downloads |
| Windows 10 ISO | https://www.microsoft.com/en-us/software-download/windows10ISO |

1. In VirtualBox, create a new Windows 10 Virtual Machine (WVM).
2. In the WVM Settings window, create a Shared Folder.
3. With the WVM open, click `Devices` in the Mac menu bar and select `Insert Guest Additions CD Image...`. This enables the Shared Folder, allowing you to transfer files between the WVM and your Mac.

## I. Decompile the APK

This step is necessary for the AssetStudio and UABE programs in sections II-IV.

| Download | Link |
|---|---|
| APKTool | https://ibotpeaches.github.io/Apktool/install |
| Latest APK | https://apkpure.com/skullgirls/com.autumn.skullgirls |

1. Open Notepad, enter `apktool d sgm.apk -f -o sgm_decoded`, and save it as `decode_sgm.bat`.
2. Rename the APK to `sgm.apk` and place it in the same folder as `decode_sgm.bat`.
3. Run `decode_sgm.bat`. This creates the `sgm_decoded` folder.

## II. Extract the Corpus, Image Assets, and Fonts

AssetStudio is used for extracting most files because it's easier to use and it organizes its exported assets by type.

| Download | Link |
|---|---|
| AssetStudio Requirements | https://github.com/Perfare/AssetStudio#requirements |
| AssetStudio | https://github.com/Perfare/AssetStudio |
| iMazing* | https://imazing.com |

<sup>*\*for iOS only*</sup>

### APK Data

1. With AssetStudio, open `sgm_decoded`.
2. In the `Filter Type` menu, select `TextAsset`, `Sprite`, `Texture2D`, and `Font`.
3. In the `Options` menu, ensure `Group by type` is checked.
4. In the `Export` menu, click `Filtered assets`. This creates the folders `TextAsset`, `Sprite`, `Texture2D`, and `Font`.

### Phone Data

5. Get a phone which has the Skullgirls Mobile app downloaded and updated.
6. Copy the `com.autumn.skullgirls` folder from your phone. For Android, this is located in `Android/data`. For iPhone, you need a program like iMazing to extract this folder from the app.
6. Repeat steps 1-4, but with the `com.autumn.skullgirls` folder and export `Sprite` only. Save into a different folder to prevent mixing the APK's `Sprite` files with your phone's `Sprite` files.

## III. Extract MonoBehaviour Files

UABE is used for extracting scripts because it exports nicely formatted JSON files while AssetStudio tends to miss important script data.

| Download | Link |
|---|---|
| Visual C++ 2010 | https://www.microsoft.com/en-us/download/details.aspx?id=14632 |
| UnityAssetBundleExtractor | https://github.com/DerPopo/UABE |
| Il2CppDumper | https://github.com/Perfare/Il2CppDumper |

### Recreate DLL

1. With Il2CppDumper, open `sgm_decoded/lib/x86/libil2cpp.so` and then `sgm_decoded/assets/bin/Data/Managed/Metadata/global-metadata.dat` when prompted.
2. For the Unity version number, enter `2018.3`.
3. Choose `Auto (Plus)` mode, which will create the folder `DummyDll` within in the same directory as the Il2CppDumper program.

### General Data

4. With UABE, open `sgm_decoded/assets/bin/data/sharedassets0.assets.split0`.
5. In the `Tools` menu, click `Get script information`. Several windows will appear sequentially. Navigate to the `DummyDll` folder and select the file that appears (if no file appears, click Cancel). Repeat. Afterwards, there will be a window detailing errors; click OK when complete.
6. Sort by Type. Select all MonoBehaviour files and click `Export Dump` in the right panel. Choose the `Unity serialized JSON` format and save to a new folder named `MonoBehaviourShared`.

### Ability Data

7. With UABE, open `sgm_decoded/assets/bin/data/globalgamemanagers`.
8. Repeat step 5.
9. Select all MonoBehaviour and GameObject files and export to `MonoBehaviourGlobal`.

## IV. Recreate Beowulf's Data

For some reason, Beowulf's BaseCharacter file is unreadable and cannot be extracted using the steps in section III. It must be manually recreated.

### Filename

1. With UABE, open `sgm_decoded/assets/bin/data/sharedassets0.assets.split0`.
2. In the `View` menu, click `Search by name` and enter `MonoBehaviour Beowulf`. Note the resulting entry's Path ID.
3. Within this repository's `data_processing/input` folder, there is a file whose name starts with `Beowulf-` and contains a 5-digit number. Update the filename by replacing that number with the aforementioned Path ID.
4. Open the `Beowulf-` file. You will be updating all `m_PathID` entries.

### Character Ability

5. Search for `GameObject CharAbility_Beowulf`.
6. Click `View Data` in the right panel.
7. Expand the menus to reach `GameObject Base/vector m_Component/Array Array/1/ComponentPair data/PPtr<Component> component/SInt64 m_PathID`.
8. In the `Beowulf-` file, change characterAbility's `m_PathID` to the `SInt64 m_PathID` value.

### Moves

9. Sort by Name.
10. Search for `MonoBehaviour Beowulf_SM*`.
11. In the `Beowulf-` file, update specialMoves' Path IDs. This should be easy since they are sequential.
12. Search for `MonoBehaviour Beowulf_BB*`.
13. In the `Beowulf-` file, update blockbusters' Path IDs. These numbers are also sequential.

## V. Verify Data

There is no need to verify the extracted data; I just wanted to include a link to DevX in this document. This program helps in understanding the file structure of the APK and does not require a Windows machine.

| Download | Link |
|---|---|
| DevX Unity Unpacker | http://devxdevelopment.com/UnityUnpacker |

1. With DevX, open `sgm.apk`. Use the default settings.
2. Browse and view whichever files you want.

## VI. Gain Access to the Art Capture Folder

The `Art Capture` folder contains officially rendered portraits, cards, and move icons. Like section V, this section is pretty much useless.

1. You must gain permission in order to access the `Art Capture` folder.
2. This permission may not be requested.
3. It's an invitation-only thing.
4. Sorry.

# Processing Input Data

If an `ImportError` occurs for any `.py` file, modify each script so the line `from *_processing import file` becomes just `import file`.

## I. Generate Gallery Data

| Download | Link |
|---|---|
| Python 3 | https://www.python.org/downloads |

1. Move `TextAsset`, `MonoBehaviourShared`, and `MonoBehaviourGlobal` into `data_processing/input`.
2. Run `data_processing/main.py`.
3. For localizations of common terms, run `data_processing/common.py`.

## II. Generate Portraits

| Download | Link |
|---|---|
| Pillow | https://pillow.readthedocs.io/en/stable/installation.html |

1. Move `Art Capture` into `image_processing/input`.
2. Run `image_processing/gen_masks.py`.
3. Edit the masks.
4. Make a copy of the masks and trim them down further.
5. Run `image_processing/gen_portraits.py`.

## III. Generate Move Icons

1. Move `Sprite` (extracted from your phone data) into `image_processing/input`.
2. Run `image_processing/gen_moves.py`.

## IV. Generate Loading GIFs

| Download | Link |
|---|---|
| Gifsicle | http://www.lcdf.org/gifsicle |

1. If you want optimized GIFs, install Gifsicle by following instructions found on its GitHub repository.
1. Run `image_processing/gen_throbbers.py`.

## V. Compress Images

| Download | Link |
|---|---|
| Pngyu | https://nukesaq88.github.io/Pngyu |

1. Open Pngyu and drag `portrait` and `move` from `data_processing/output` into the Pngyu window.
2. Click `Compress Start`.
3. Optionally, click `Clear` and repeat the process with `Sprite` (extracted from the APK data) and `Texture2D`. Do not compress the `Sprite` extracted from your phone data.
