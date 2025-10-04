# Dit bestand bevat de metadata voor de Windows executable.
# PyInstaller gebruikt dit om de 'Details' tab in de bestandseigenschappen te vullen.
# Een linter kan klagen over ongedefinieerde namen (VSVersionInfo, etc.),
# maar dit is verwacht gedrag. PyInstaller injecteert deze tijdens het build-proces.

VSVersionInfo(
    ffi=FixedFileInfo(
        # filevers en prodvers: (Major, Minor, Patch, Build)
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
        # Set flags and OS
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "040904B0",
                    [  # Taal ID: U.S. English, Karakterset: Unicode
                        StringStruct("CompanyName", "TekstDB Project"),
                        StringStruct("FileDescription", "Grafische editor voor TekstDB"),
                        StringStruct("FileVersion", "1.0.0.0"),
                        StringStruct("InternalName", "TekstDbGui"),
                        StringStruct("LegalCopyright", "Copyright © Michel"),
                        StringStruct("OriginalFilename", "tekstdb_gui.exe"),
                        StringStruct("ProductName", "TekstDB Project"),
                        StringStruct("ProductVersion", "1.0.0.0"),
                    ],
                )
            ]
        ),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),  # 1033: U.S. English, 1200: Unicode
    ],
)
