import armutils
import subprocess

def kode_studio():
    sdk_path = armutils.get_sdk_path()
    project_path = armutils.get_fp()

    if armutils.get_os() == 'win':
        kode_path = sdk_path + '/win32/Kode Studio.exe'
    elif armutils.get_os() == 'mac':
        kode_path = '"' + sdk_path + '/Kode Studio.app/Contents/MacOS/Electron"'
    else:
        kode_path = sdk_path + '/linux64/kodestudio'

    subprocess.Popen([kode_path, armutils.get_fp()], shell=True)

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def get_kha_target(target_name): # TODO: remove
    if target_name == 'macos':
        return 'osx'
    return target_name
