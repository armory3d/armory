import bpy, math, os, platform, subprocess, sys, re, shutil

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class TLM_Install_OpenCV(bpy.types.Operator):
    """Install OpenCV"""
    bl_idname = "tlm.install_opencv_lightmaps"
    bl_label = "Install OpenCV"
    bl_description = "Install OpenCV"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene
        cycles = bpy.data.scenes[scene.name].cycles

        print("Module OpenCV")

        if (2, 91, 0) > bpy.app.version:
            pythonbinpath = bpy.app.binary_path_python
        else:
            pythonbinpath = sys.executable

        if platform.system() == "Windows":
            pythonlibpath = os.path.join(os.path.dirname(os.path.dirname(pythonbinpath)), "lib")
        else:
            pythonlibpath = os.path.join(os.path.dirname(os.path.dirname(pythonbinpath)), "lib", os.path.basename(pythonbinpath)[:-1])

        ensurepippath = os.path.join(pythonlibpath, "ensurepip")

        cmda = [pythonbinpath, ensurepippath, "--upgrade", "--user"]
        pip = subprocess.run(cmda)
        cmdc = [pythonbinpath, "-m", "pip", "install", "--upgrade", "pip"]
        pipc = subprocess.run(cmdc)

        if pip.returncode == 0:
            print("Sucessfully installed pip!\n")
        else:

            try:
                import pip
                module_pip = True
            except ImportError:
                #pip 
                module_pip = False

            if not module_pip:
                print("Failed to install pip!\n")
                if platform.system() == "Windows":
                    ShowMessageBox("Failed to install pip - Please start Blender as administrator", "Restart", 'PREFERENCES')
                else:
                    ShowMessageBox("Failed to install pip - Try starting Blender with SUDO", "Restart", 'PREFERENCES')
                return{'FINISHED'}

        cmdb = [pythonbinpath, "-m", "pip", "install", "opencv-python"]
        
        #opencv = subprocess.run(cmdb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        opencv = subprocess.run(cmdb)

        if opencv.returncode == 0:
            print("Successfully installed OpenCV!\n")
        else:
            print("Failed to install OpenCV!\n")

            if platform.system() == "Windows":
                ShowMessageBox("Failed to install opencv - Please start Blender as administrator", "Restart", 'PREFERENCES')
            else:
                ShowMessageBox("Failed to install opencv - Try starting Blender with SUDO", "Restart", 'PREFERENCES')

            return{'FINISHED'}

        module_opencv = True
        print("Sucessfully installed OpenCV!\n")
        ShowMessageBox("Please restart blender to enable OpenCV filtering", "Restart", 'PREFERENCES')

        return{'FINISHED'}