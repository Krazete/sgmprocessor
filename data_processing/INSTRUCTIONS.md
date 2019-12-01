# How to Mine the APK

## (For Mac Users) Install Windows
1. Get a [Windows 10 ISO](https://www.microsoft.com/en-us/software-download/windows10ISO).
2. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads).
3. Create a new Windows 10 Virtual Machine (WVM) in VirtualBox.
4. Create a Shared Folder in the Settings window for WVM.
5. Start WVM and select `Insert Guest Additions CD Image...` under the `Devices` menu in the Mac menu bar.

## (Within Windows) Install APK Mining Tools
1. Download [APKTool](https://ibotpeaches.github.io/Apktool/install/).
2. Download [AssetStudio](https://github.com/Perfare/AssetStudio) and its [Requirements](https://github.com/Perfare/AssetStudio#requirements).
3. Open Notepad and enter `apktool d sgm.apk -f -o sgm_decoded`. Save the file as `decode_sgm.bat`.
4. Download [UnityAssetBundleExtractor](https://github.com/DerPopo/UABE) (UABE).
5. Download [Visual C++ 2010](https://www.microsoft.com/en-us/download/details.aspx?id=14632) (required for UABE).
6. Download [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) (required for UABE).

## Decompile the APK
1. Download the latest [APK](https://apkpure.com/skullgirls/com.autumn.skullgirls).
2. Rename the APK to `sgm.apk` and move it into the folder where `decode_sgm.bat` is located.
3. Run `decode_sgm.bat`.

## Extract the Game's Entire Corpus and Other Files
1. Run AssetStudio and load the folder `sgm_decoded`.
2. For corpus files, select `TextAsset` in the `Filter Type` menu.
3. For image files, select `Sprite` and `Texture2D` in the `Filter Type` menu.
4. Make sure `Group by type` is checked in the dropdown list under the `Options` menu.
5. Click `Filtered assets` in the `Export` menu. Save to a new folder named `sgm_exports`.

## Extract Scripts
1. Run Il2CppDumper and open `sgm_decoded/lib/x86/libil2cpp.so` and then `sgm_decoded/assets/bin/Data/Managed/Metadata/global-metadata.dat` when prompted. Unless this document is severely outdated, enter `2018.3` when prompted for the Unity version number. Select the mode Auto (Plus) and note the new `DummyDll` folder, created in the same directory as the Il2CppDumper program.
2. Run UABE and open `sgm_decoded/assets/bin/data/sharedassets0.assets.split0`.
3. Click `Get script information` in the `Tools` menu. Several windows will appear sequentially.
4. Navigate to the `DummyDll` folder and select the file that appears (if no file appears, click Cancel). Repeat. Afterwards, there will be a window detailing errors; click OK.
5. Sort by Type. Select all MonoBehaviour files and click `Export Dump` in the right panel. Choose the `Unity JsonUtility file` format and save to a new folder named `MonoBehaviour` within `sgm_exports`.
6. Open `sgm_decoded/assets/bin/data/globalgamemanagers` and repeat steps 3-5. This folder contains essential Ability data.

## (For Mac Users) Transfer Data from Windows VM to Mac
1. Move `sgm_exports` to the shared folder.
2. Shut down Windows.

#### Notes
- AssetStudio is used for extracting most files because it's easier to use and it organizes its exported assets by type.
- UABE is used for extracting scripts because AssetStudio misses important data when exporting scripts.
- The art for portraits, cards, and moves are not located within the APK; they reside in the game files downloaded to the phone. To access those, use an app like iMazing to copy the `com.autumn.skullgirls` folder from your phone and then open it with AssetStudio or UABE.
- As of version 2.7.0, MonoBehaviour:VariantData files cannot be properly extracted.
- As of version 3.1.0, MonoBehaviour:VariantData files can be extracted again, but Ability files are inaccessible. Beowulf's character data is also inaccessible for some reason.
- To fill in missing data, check [INSTRUCGTIONS.md]().
