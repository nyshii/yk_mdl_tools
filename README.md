

# yk_mdl_tools
A Blender addon that reads models from character_model_model_data.bin and imports them. 
Currently, it does not read tex_change_table or gets dedit colors.

## HOW TO INSTALL
Just download yk_mdl_tools.py from this repository and install it in Blender. (Preferences > Add-ons > Install)

## PREREQUISITES
- [ParManager](https://github.com/Kaplas80/ParManager) (to extract the .PAR files)
- [yk_gmd_io](https://github.com/theturboturnip/yk_gmd_io/releases/) (for importing the .GMDs)
## USAGE
Once installed, a new menu named "YK MDL Tools" will appear on the Blender sidebar (default hotkey is N). 

The DB folder must be the folder where all the .bins are located (e.g. `C:\Program Files (x86)\Steam\steamapps\common\Lost Judgment\runtime\media\data\db.coyote.en.par.unpack`)

The chara folder is where the folders like tops, btms, etc. are located. (e.g. `C:\Program Files (x86)\Steam\steamapps\common\Lost Judgment\runtime\media\data\chara.par.unpack`)

The textures folder is where all the textures are stored (e.g. `C:\Program Files (x86)\Steam\steamapps\common\Yakuza Like a Dragon\runtime\media\data\chara.par.unpack\dds`) . I recommend converting the .dds textures in `chara.par/dds` to .png as Blender cannot read BC7 textures yet.

The model name in DB is the name of the model from character_model_model_data.bin (or character_parts_model_data.bin in Yakuza 6) you wish to import. (e.g. `c_em_ichiban`)

Turning off "Hide flagged meshes" will make it so that flagged meshes are not hidden when imported.

Press "Delete LOD meshes" to delete meshes that start with [l1], [l2], and [l3] (LOD models).

## CREDITS
[Ret-HZ for reARMP](https://github.com/Ret-HZ/reARMP)
