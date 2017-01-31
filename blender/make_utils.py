import armutils
import subprocess
import bpy

def kode_studio():
    sdk_path = armutils.get_sdk_path()
    project_path = armutils.get_fp()

    if armutils.get_os() == 'win':
        kode_path = sdk_path + '/win32/Kode Studio.exe'
        subprocess.Popen([kode_path, armutils.get_fp()])
    elif armutils.get_os() == 'mac':
        kode_path = '"' + sdk_path + '/Kode Studio.app/Contents/MacOS/Electron"'
        subprocess.Popen([kode_path + ' ' + armutils.get_fp()], shell=True)
    else:
        kode_path = sdk_path + '/linux64/kodestudio'
        subprocess.Popen([kode_path, armutils.get_fp()])

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def get_kha_target(target_name): # TODO: remove
    if target_name == 'macos':
        return 'osx'
    return target_name

def runtime_to_gapi():
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_play_runtime == 'Krom' or wrd.arm_play_runtime == 'Native':
        return 'arm_gapi_' + armutils.get_os()
    else:
        return 'arm_gapi_html5'

def target_to_gapi():
    # TODO: align target names
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_project_target == 'krom':
        return 'arm_gapi_' + armutils.get_os()
    elif wrd.arm_project_target == 'macos':
        return 'arm_gapi_mac'
    elif wrd.arm_project_target == 'windows':
        return 'arm_gapi_win'
    elif wrd.arm_project_target == 'android-native':
        return 'arm_gapi_android'
    else:
        return 'arm_gapi_' + wrd.arm_project_target
