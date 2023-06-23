bl_info = {
    'name': 'Yakuza Model Tools',
    'author': 'notyoshi',
    'category': 'All',
    'location': 'View 3D > Tool Shelf > YKZ MDL Tools',
    'description': 'A buncha crappy tools to make Yakuza renders and/or modding easier.',
    'version': (0, 0, 1),
    'blender': (3, 2, 0),
}

import bpy, json, os, re, numpy, ast
from bpy.types import Panel
from bpy.types import Operator


## hide flagged meshes ##

def hide_flagged_meshes(context, modelname, modelflags, mode):

    # get parts
    def parts(context):
        with open(context.scene.db_folder +
                  "character_sub_parts_type.bin.json") as parts_json_file:
            sub_parts = json.load(parts_json_file)
        parts = []
        part_flags = []
        inc = 0

        for x in sub_parts:
            def sub_parts_func(key):
                key = sub_parts[str(inc)][list(sub_parts[str(inc)].keys())[0]][str(key)]
                return key

            if inc != sub_parts['ROW_COUNT']:
                try:
                    sub_parts_func("prefix")
                except:
                    parts.append('null')
                    part_flags.append([0,0,0,0])
                    inc += 1
                else:
                    parts.append(sub_parts_func("prefix"))
                    sub_parts_flags = [int(sub_parts_func("use_hair")), #0
                                       int(sub_parts_func("use_face")), #1
                                       int(sub_parts_func("use_tops")), #2
                                       int(sub_parts_func("use_btms")) #3
                                       ]
                    part_flags.append(sub_parts_flags)
                    inc += 1

        while len(parts) != 64:
            parts.append('null')
            part_flags.append([0,0,0,0])

        parts.reverse()
        part_flags.reverse()
        return parts, part_flags
        ###

    # filter parts
    def filter_parts(flags, context):
        binary = [int(d) for d in format(numpy.int64(flags), '064b')]

        inc = 0
        filteredparts = []

        partspartsparts = parts(context)[0]
        partsflags = parts(context)[1]


        # filter the parts
        for x in partspartsparts:
            if binary[inc] == 1:
                filteredparts.append(parts(context)[0][inc])
            if partsflags[inc][mode] == 0:
                filteredparts.append(parts(context)[0][inc])
            inc += 1
        return filteredparts

    filter_list = filter_parts(modelflags, context)

    # actually hiding it
    def hide(mesh_object):

        if any(x in mesh_object.name for x in parts(context)[0]):
            helpme = 0
            for i in filter_list:
                helpme -= 1
                regex_test = "(?:\[.*?\])+((ns_|sw_)?(sw_|ns_)?" + re.escape(i) + ").*|^((ns_|sw_)?(sw_|ns_)?" + re.escape(i) + ").*"
                if not re.search(regex_test, mesh_object.name):
                    helpme += 1

            if helpme != -1:
                bpy.data.objects[mesh_object.name].hide_viewport = True
                bpy.data.objects[mesh_object.name].hide_render = True

    if context.scene.hideflagged:
        for ob in bpy.data.objects[modelname.lower() + "_armature"].children:
            hide(ob)

## Load models from db ##

def load_models_from_db(context):
    modeldata = "character_parts_model_data.bin.json" if context.scene.yakuza6 else "character_model_model_data.bin.json"

    with open(context.scene.db_folder + modeldata) as json_file:
        model_data = json.load(json_file)

    entry = 0
    i = 0
    state = False

    while not state:
        try:
            entry = model_data['subTable'][str(i)][context.scene.modelname]['2']
        except:
            if i != len(model_data['subTable']):
                i += 1
            else:
                state = True
                raise Exception(context.scene.modelname + " does not exist.")
        else:
            state = True

    face_flag = numpy.int64(model_data[str(entry)]['']['face_flags'])
    hair_flag = numpy.int64(model_data[str(entry)]['']['hair_flags'])
    tops_flag = numpy.int64(model_data[str(entry)]['']['tops_flags'])
    btms_flag = numpy.int64(model_data[str(entry)]['']['btms_flags'])

    face = str(model_data[str(entry)]['']['face_model']) if 'face_model' in model_data[str(entry)][''] else ''
    hair = str(model_data[str(entry)]['']['hair_model']) if 'hair_model' in model_data[str(entry)][''] else ''
    tops = str(model_data[str(entry)]['']['tops_model']) if 'tops_model' in model_data[str(entry)][''] else ''
    btms = str(model_data[str(entry)]['']['btms_model']) if 'btms_model' in model_data[str(entry)][''] else ''

    if face != '':
        bpy.ops.import_scene.gmd_skinned(files=[{"name": face + ".gmd"}],
                                         directory=context.scene.chara_folder + '\\face\\' + face + "\\")

        hide_flagged_meshes(context, face, face_flag, 1)
    if hair != '':
        bpy.ops.import_scene.gmd_skinned(files=[{"name": hair + ".gmd"}],
                                         directory=context.scene.chara_folder + '\\hair\\' + hair + "\\")
        hide_flagged_meshes(context, hair, hair_flag, 0)

    if tops != '':
        bpy.ops.import_scene.gmd_skinned(files=[{"name": tops + ".gmd"}],
                                         directory=context.scene.chara_folder + '\\tops\\' + tops + "\\")
        hide_flagged_meshes(context, tops, tops_flag, 2)
    if btms != '':
        bpy.ops.import_scene.gmd_skinned(files=[{"name": btms + ".gmd"}],
                                         directory=context.scene.chara_folder + '\\btms\\' + btms + "\\")
        hide_flagged_meshes(context, btms, btms_flag, 3)

class YKMDL_OP_loadmodelfromdb(Operator):
    bl_idname = "ykmdl.load_model_from_db"
    bl_label = "Load Model(s) from DB"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        load_models_from_db(context)
        if context.scene.png_folder != "":
            bpy.ops.yk.image_relink(directory=context.scene.png_folder)

        return {'FINISHED'}

## remove LOD meshes ##
def remove_lod_meshes(context):
    for ob in bpy.context.scene.objects:
        x = re.search("(\[l1).*|(\[l2).*|(\[l3).*", ob.name)
        if x is not None:
            bpy.data.objects.remove(ob, do_unlink=True)

class YKMDL_OP_removelodmeshes(bpy.types.Operator):
    bl_idname = "ykmdl.remove_lod_meshes"
    bl_label = "Delete LOD meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_lod_meshes(context)
        return {'FINISHED'}

## menu crap ##

# filepath declaration #
class YKMDL_OP_menu(Panel):
    bl_idname = "ykmdl.menu"
    bl_label = "Menu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YK MDL Tools"

    @classmethod
    def poll(cls, context):
        return True

    # called every frame
    def draw(self, context):
        col = self.layout.column()
        row = self.layout.row()

        def prop_split(layout, data, field, name, **prop_kwargs):
            split = layout.split(factor=0.5)
            split.label(text=name)
            split.prop(data, field, text="", **prop_kwargs)

        prop_split(col, context.scene, "db_folder", "DB folder")
        prop_split(col, context.scene, "chara_folder", "Chara folder")
        prop_split(col, context.scene, "png_folder", "Textures folder")
        prop_split(col, context.scene, "modelname", "Model name in DB")
        prop_split(col, context.scene, "hideflagged", "Hide flagged meshes")
        prop_split(col, context.scene, "yakuza6", "Yakuza 6")
        col.operator(YKMDL_OP_loadmodelfromdb.bl_idname)
        col.operator(YKMDL_OP_removelodmeshes.bl_idname)

## boring shit ##

def register():
    bpy.types.Scene.db_folder = bpy.props.StringProperty(name="db folder",
                                                                          subtype="FILE_PATH")

    bpy.types.Scene.chara_folder = bpy.props.StringProperty(name="chara folder", subtype="FILE_PATH")

    bpy.types.Scene.modelname = bpy.props.StringProperty(name="model name")

    bpy.types.Scene.png_folder = bpy.props.StringProperty(name="png_folder", subtype="FILE_PATH")

    bpy.types.Scene.yakuza6 = bpy.props.BoolProperty(name="Yakuza 6")
    bpy.types.Scene.hideflagged = bpy.props.BoolProperty(name="Hide flagged meshes", default=True)
    
    bpy.utils.register_class(YKMDL_OP_removelodmeshes)
    bpy.utils.register_class(YKMDL_OP_loadmodelfromdb)
    bpy.utils.register_class(YKMDL_OP_menu)


def unregister():
    del bpy.types.Scene.character_model_model_data
    del bpy.types.Scene.db_folder
    del bpy.types.Scene.entry
    del bpy.types.Scene.png_folder
    del bpy.types.Scene.hideflagged

    bpy.utils.unregister_class(YKMDL_OP_loadmodelfromdb)
    bpy.utils.unregister_class(YKMDL_OP_loadmodelfromdb)
    bpy.utils.unregister_class(YKMDL_OP_menu)


if __name__ == "__main__":
    register()