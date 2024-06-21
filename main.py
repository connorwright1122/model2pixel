bl_info = {
    "name": "model2pixel",
    "author": "Connor Wright",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > Render category",
    "description": "My custom operator buttons",
    "category": "Development",
}

import bpy
import os
#from install_blender_python_module import *
import sys
import subprocess
import platform

def isWindows():
    return os.name == 'nt'

def isMacOS():
    return os.name == 'posix' and platform.system() == "Darwin"

def isLinux():
    return os.name == 'posix' and platform.system() == "Linux"

def python_exec():
    
    if isWindows():
        return os.path.join(sys.prefix, 'bin', 'python.exe')
    elif isMacOS():
    
        try:
            # 2.92 and older
            path = bpy.app.binary_path_python
        except AttributeError:
            # 2.93 and later
            import sys
            path = sys.executable
        return os.path.abspath(path)
    elif isLinux():
        import sys
        return os.path.join(sys.prefix, 'bin', 'python3.11')
    else:
        print("sorry, still not implemented for ", os.name, " - ", platform.system)


def installModule(packageName):

    try:
        subprocess.call([python_exe, "import ", packageName])
    except:
        python_exe = python_exec()
       # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
       # install required packages
        subprocess.call([python_exe, "-m", "pip", "install", packageName])
        
installModule("pillow")
from PIL import Image

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )




class RENDER_PT_model2pixel(bpy.types.Panel):  # class naming convention ‘CATEGORY_PT_name’

    # where to add the panel in the UI
    bl_space_type = "VIEW_3D"  # 3D Viewport area (find list of values here https://docs.blender.org/api/current/bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items)
    bl_region_type = "UI"  # Sidebar region (find list of values here https://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items)

    bl_category = "Render"  # found in the Sidebar
    bl_label = "model2pixel"  # found at the top of the Panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        
        row = layout.row()
        row.prop(mytool, "my_bool", text="Bool Property")
        
        row = layout.row()
        row.label(text="Resolution")
        row = layout.row()
        row.prop(scene, "resolution_x")
        row.prop(scene, "resolution_y")

        row = layout.row()
        row.label(text="Render")
        row = layout.row()
        row.operator("render.base", text="Render Base")
        row = layout.row()
        row.operator("render.normal", text="Render Normal")
        #row = layout.row()
        #row.operator("object.shade_smooth", text="Shade Smooth")
        row = layout.row()
        #row.prop(scene, "scene.render.filepath", text="")
        row.prop(scene.render, "filepath", text="Output Directory")
        #row.operator("render.select_dir", text="Output Directory")
        #row.prop(scene, "render.select_dir")
        
        
        if (my_bool == True):
            print ("Property Enabled")
        else:
            print ("Property Disabled")

        





    
    
def swap_render_engine(new_engine):
    bpy.context.scene.render.engine = new_engine
    
    
    
def settings_base_render():
    swap_render_engine("BLENDER_EEVEE")
    scene = bpy.context.scene
    scene.render.resolution_x = scene.resolution_x
    scene.render.resolution_y = scene.resolution_y
    scene.render.filter_size = 0
    scene.render.film_transparent = True
    scene.render.image_settings.compression = 0
    
    
def settings_normal_render():
    swap_render_engine("BLENDER_WORKBENCH")
    scene = bpy.context.scene
    scene.render.resolution_x = scene.resolution_x
    scene.render.resolution_y = scene.resolution_y
    scene.render.filter_size = 0.01
    scene.render.film_transparent = True
    scene.render.image_settings.compression = 0
    scene.display.shading.studio_light = "check_normal+y.exr"
    scene.display.render_aa = "OFF"



def create_output_directory(subfolder_name):
    scene = bpy.context.scene
    parent_path = scene.render.filepath
    subfolder_path = os.path.join(parent_path, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    scene.render.filepath = os.path.join(subfolder_path, "")


def pack_spritesheet(output_dir, subfolder_name, spritesheet_name):
    subfolder_path = os.path.join(output_dir, subfolder_name)
    images = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
    images.sort()  
    
    if not images:
        print("No images found to pack into a spritesheet.")
        return
    
    start_index = 0
    
    if isMacOS():
        start_index = 1
        print("MacOS")
    else:
        print("Not mac")
        
    print(start_index)
    first_image_path = os.path.join(subfolder_path, images[start_index])
    with Image.open(first_image_path) as img:
        width,height = img.size
    
    
    columns = int((len(images) - start_index) * 0.5) + 1
    rows = int((len(images) - start_index) + columns - 1) // columns
    spritesheet = Image.new('RGBA', (columns * width, rows * height))
    
    '''
    for index,image in enumerate(images, start=start_index):
        with Image.open(subfolder_path, image) as img:
            x = (index % columns) * width
            y = (index // columns) * height
            spritesheet.paste(img, (x,y))
    '''
    for i in range(start_index, len(images)):
        image_filename = images[i]
      
        if image_filename.lower().endswith('.png'):
            image_path = os.path.join(subfolder_path, image_filename)
            with Image.open(image_path) as img:
                x = ((i - start_index) % columns) * width  
                y = ((i - start_index) // columns) * height
                spritesheet.paste(img, (x, y))

    
    spritesheet_path = os.path.join(output_dir, f"{spritesheet_name}.png")
    spritesheet.save(spritesheet_path)
    print(f"Spritesheet saved to: {spritesheet_path}")


class RENDER_OT_render_base(bpy.types.Operator):
    bl_idname = "render.base"
    bl_label = "Render Base"

    def execute(self, context):
        scene = bpy.context.scene
        settings_base_render()
        temp_directory = scene.render.filepath
        create_output_directory("Base")
        bpy.ops.render.render(animation=True)
        scene.render.filepath = temp_directory
        
        output_dir = bpy.path.abspath(scene.render.filepath)
        pack_spritesheet(output_dir, "Base", "Base_Spritesheet")
        
        
        self.report({'INFO'}, f"This is {self.bl_idname}")
        return {'FINISHED'}
    

class RENDER_OT_render_normal(bpy.types.Operator):
    bl_idname = "render.normal"
    bl_label = "Render Normal"

    def execute(self, context):
        settings_normal_render()
        temp_directory = bpy.context.scene.render.filepath
        create_output_directory("Normal")
        bpy.ops.render.render(animation=True)
        bpy.context.scene.render.filepath = temp_directory
        
        self.report({'INFO'}, f"This is {self.bl_idname}")
        return {'FINISHED'}



class SelectDirExample(bpy.types.Operator):
    """Create render for all characters"""
    bl_idname = "render.select_dir"
    bl_label = "Select Output Folder"
    bl_options = {'REGISTER'}

    # Define this to tell 'fileselect_add' that we want a directoy
    directory: bpy.props.StringProperty(
        name="Outdir Path",
        description="Where I will save my stuff"
        )

    # Filters folders
    filter_folder: bpy.props.BoolProperty(
        default=True,
        options={"HIDDEN"}
        )

    def execute(self, context):
        #context.scene.output_directory = self.directory
        scene = bpy.context.scene
        scene.render.filepath = self.directory
        print("Selected dir: '" + self.directory + "'")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Open browser, take reference to 'self' read the path to selected
        # file, put path in predetermined self fields.
        # See: https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        context.window_manager.fileselect_add(self)
        # Tells Blender to hang on for the slow user input
        return {'RUNNING_MODAL'}


class Render_Settings(PropertyGroup):
    '''
    bl_idname = "render.settings"
    bl_label = "Render Settings"
    bl_options = {'REGISTER'}
    '''
    
    my_bool : BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default = False
        )

    '''
    my_int : IntProperty(
        name = "Set a value",
        description="A integer property",
        default = 23,
        min = 10,
        max = 100
        )

    my_float : FloatProperty(
        name = "Set a value",
        description = "A float property",
        default = 23.7,
        min = 0.01,
        max = 30.0
        )
    '''





classes = (RENDER_OT_render_base, RENDER_OT_render_normal, RENDER_PT_model2pixel, SelectDirExample, Render_Settings)



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.resolution_x = bpy.props.IntProperty(
        name="X",
        description="Resolution X",
        default=64,
        min=1
    )
    bpy.types.Scene.resolution_y = bpy.props.IntProperty(
        name="Y",
        description="Resolution Y",
        default=64,
        min=1
    )
    bpy.types.Scene.my_tool = PointerProperty(type=Render_Settings)




def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.resolution_x
    del bpy.types.Scene.resolution_y
    del bpy.types.Scene.my_tool

        
        
if __name__ == "__main__":
    register()