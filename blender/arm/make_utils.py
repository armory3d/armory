import arm.utils
import subprocess
import bpy
import os

def kode_studio():
    sdk_path = arm.utils.get_sdk_path()
    project_path = arm.utils.get_fp()

    if arm.utils.get_os() == 'win':
        # Fight long-path issues on Windows
        if not os.path.exists(sdk_path + '/win32/resources/app/extensions/kha/Kha'):
            source = sdk_path + '/win32/resources/app/extensions/kha/Kha'
            target = sdk_path + '/win32/Kha'
            subprocess.check_call('mklink /J "%s" "%s"' % (source, target), shell=True)
        if not os.path.exists(sdk_path + '/win32/resources/app/extensions/krom/Krom'):
            source = sdk_path + '/win32/resources/app/extensions/krom/Krom'
            target = sdk_path + '/win32/Krom'
            subprocess.check_call('mklink /J "%s" "%s"' % (source, target), shell=True)
        kode_path = sdk_path + '/win32/Kode Studio.exe'
        subprocess.Popen([kode_path, arm.utils.get_fp()])
    elif arm.utils.get_os() == 'mac':
        kode_path = '"' + sdk_path + '/Kode Studio.app/Contents/MacOS/Electron"'
        subprocess.Popen([kode_path + ' "' + arm.utils.get_fp() + '"'], shell=True)
    else:
        kode_path = sdk_path + '/linux64/kodestudio'
        subprocess.Popen([kode_path, arm.utils.get_fp()])

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def get_kha_target(target_name): # TODO: remove
    if target_name == 'macos':
        return 'osx'
    return target_name

def target_to_gapi(arm_project_target):
    # TODO: align target names
    if arm_project_target == 'krom':
        return 'arm_gapi_' + arm.utils.get_os()
    elif arm_project_target == 'macos':
        return 'arm_gapi_mac'
    elif arm_project_target == 'windows':
        return 'arm_gapi_win'
    elif arm_project_target == 'windowsapp':
        return 'arm_gapi_winapp'
    elif arm_project_target == 'android-native':
        return 'arm_gapi_android'
    elif arm_project_target == 'node':
        return 'arm_gapi_html5'
    else:
        return 'arm_gapi_' + arm_project_target
