# Advanced (Extracting MonoBehaviour:VariantData)

For some reason, UABE cannot extract `MonoBehaviour:VariantData` files in APK versions after 2.6.1. Extra steps are needed to get these files.

Note for the following that Variant files are the ones that have `_B_`, `_S_`, `_G_`, or `_D_` in the filename.

## Get the Format from APK 2.6.1
1. Follow the process above using the latest APK.
2. Download [APK 2.6.1](https://apkpure.com/skullgirls/com.autumn.skullgirls/download/31-APK).
3. Using the same process, extract scripts from APK 2.6.1.
4. Copy all of the old Variant files into `MonoBehaviour` within `sgm_exports` (created from the latest APK).

## Get the Data from the Latest APK
1. Download the [DevX Unity Unpacker](http://devxdevelopment.com/UnityUnpacker).
2. Open the latest APK in DevX Unity Unpacker.
3. Search for all Variant files.
4. Manually update all Variant files, including the path ID embedded in the filename.
5. Use old Variant files to create new files for new Variants that didn't exist in 2.6.1.

The directory `__FAKE_Variant_MonoBehaviour` and the script `faker.py` within this folder were created to ease this process, recreating only the data which is necessary for the website. The `sgm_exports` folder must be within this folder to run `faker.py`.

This removes the APK 2.6.1 steps, but still requires the DevX steps to manually update the `faker.py` reference data.

The scripts within this folder must have this folder's parent directory set as the working directory in order to run. The `data` folder located in this folder's parent directory must also be created before running `main.py`.
