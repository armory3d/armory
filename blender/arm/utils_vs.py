import locale
import os
import subprocess

import arm.utils

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


def get_visual_studio_from_version(version: str) -> tuple[str, str, str, str]:
    vs = [('10', '2010', 'Visual Studio 2010 (version 10)', 'vs2010'),
          ('11', '2012', 'Visual Studio 2012 (version 11)', 'vs2012'),
          ('12', '2013', 'Visual Studio 2013 (version 12)', 'vs2013'),
          ('14', '2015', 'Visual Studio 2015 (version 14)', 'vs2015'),
          ('15', '2017', 'Visual Studio 2017 (version 15)', 'vs2017'),
          ('16', '2019', 'Visual Studio 2019 (version 16)', 'vs2019'),
          ('17', '2022', 'Visual Studio 2022 (version 17)', 'vs2022')]
    for item in vs:
        if item[0] == version.strip():
            return item[0], item[1], item[2], item[3]


def get_list_installed_vs(get_version: bool, get_name: bool, get_path: bool) -> []:
    err = ''
    items = []
    path_file = os.path.join(arm.utils.get_sdk_path(), 'Kha', 'Kinc', 'Tools', 'kincmake', 'Data', 'windows', 'vswhere.exe')
    if not os.path.isfile(path_file):
        err = f'File "{path_file}" not found.'
        return items, err

    if (not get_version) and (not get_name) and (not get_path):
        return items, err

    items_ver = []
    items_name = []
    items_path = []
    count = 0

    if get_version:
        items_ver, err = get_list_installed_vs_version()
        count_items = len(items_ver)
    if len(err) > 0:
        return items, err
    if get_name:
        items_name, err = get_list_installed_vs_name()
        count_items = len(items_name)
    if len(err) > 0:
        return items, err
    if get_path:
        items_path, err = get_list_installed_vs_path()
        count_items = len(items_path)
    if len(err) > 0:
        return items, err

    for i in range(count_items):
        v = items_ver[i][0] if len(items_ver) > i else ''
        v_full = items_ver[i][1] if len(items_ver) > i else ''
        n = items_name[i] if len(items_name) > i else ''
        p = items_path[i] if len(items_path) > i else ''
        items.append((v, n, p, v_full))
    return items, err


def get_list_installed_vs_version() -> []:
    err = ''
    items = []
    path_file = os.path.join(arm.utils.get_sdk_path(), 'Kha', 'Kinc', 'Tools', 'kincmake', 'Data', 'windows', 'vswhere.exe')
    if os.path.isfile(path_file):
        # Set arguments
        cmd = path_file + ' -nologo -property installationVersion'
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline().decode("utf-8")
            if len(output.strip()) == 0 and process.poll() is not None:
                break
            if output:
                version_all = output.strip().replace(' ', '')
                version_parse = version_all.split('.')
                version_major = version_parse[0]
                items.append((version_major, version_all))
    else:
        err = f'File "{path_file}" not found.'
    return items, err


def get_list_installed_vs_name() -> []:
    err = ''
    items = []
    path_file = os.path.join(arm.utils.get_sdk_path(), 'Kha', 'Kinc', 'Tools', 'kincmake', 'Data', 'windows', 'vswhere.exe')
    if os.path.isfile(path_file):
        # Set arguments
        cmd = path_file + ' -nologo -property displayName'
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline().decode(locale.getpreferredencoding())
            if len(output.strip()) == 0 and process.poll() is not None:
                break
            if output:
                name = arm.utils.safestr(output).replace('_', ' ').strip()
                items.append(name)
    else:
        err = f'File "{path_file}" not found.'
    return items, err


def get_list_installed_vs_path() -> []:
    err = ''
    items = []
    path_file = os.path.join(arm.utils.get_sdk_path(), 'Kha', 'Kinc', 'Tools', 'kincmake', 'Data', 'windows', 'vswhere.exe')
    if os.path.isfile(path_file):
        # Set arguments
        cmd = path_file + ' -nologo -property installationPath'
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline().decode("utf-8")
            if len(output.strip()) == 0 and process.poll() is not None:
                break
            if output:
                path = output.strip()
                items.append(path)
    else:
        err = 'File "' + path_file + '" not found.'
    return items, err
