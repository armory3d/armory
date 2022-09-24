"""
Various utilities for interacting with Visual Studio on Windows.
"""
import json
import os
import subprocess
from typing import Any, Optional, Callable

import bpy

import arm.log as log
import arm.make
import arm.make_state as state
import arm.utils

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    arm.make = arm.reload_module(arm.make)
    state = arm.reload_module(state)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


# VS versions supported by khamake. Keep in mind that this list is also
# used for the wrd.arm_project_win_list_vs EnumProperty!
supported_versions = [
    ('10', '2010', 'Visual Studio 2010 (version 10)'),
    ('11', '2012', 'Visual Studio 2012 (version 11)'),
    ('12', '2013', 'Visual Studio 2013 (version 12)'),
    ('14', '2015', 'Visual Studio 2015 (version 14)'),
    ('15', '2017', 'Visual Studio 2017 (version 15)'),
    ('16', '2019', 'Visual Studio 2019 (version 16)'),
    ('17', '2022', 'Visual Studio 2022 (version 17)')
]

# version_major to --visualstudio parameter
version_to_khamake_id = {
    '10': 'vs2010',
    '11': 'vs2012',
    '12': 'vs2013',
    '14': 'vs2015',
    '15': 'vs2017',
    '16': 'vs2019',
    '17': 'vs2022',
}

# VS versions found with fetch_installed_vs()
_installed_versions = []


def is_version_installed(version_major: str) -> bool:
    return any(v['version_major'] == version_major for v in _installed_versions)


def get_installed_version(version_major: str, re_fetch=False) -> Optional[dict[str, str]]:
    for installed_version in _installed_versions:
        if installed_version['version_major'] == version_major:
            return installed_version

    # No installation was found. If re_fetch is True, fetch and try again
    # (the user may not have fetched installations before for example)
    if re_fetch:
        if not fetch_installed_vs():
            return None
        return get_installed_version(version_major, False)

    return None


def get_supported_version(version_major: str) -> Optional[dict[str, str]]:
    for version in supported_versions:
        if version[0] == version_major:
            return {
                'version_major': version[0],
                'year': version[1],
                'name': version[2]
            }
    return None


def fetch_installed_vs() -> bool:
    global _installed_versions

    data_instances = vswhere_get_instances()
    if data_instances is None:
        return False

    items = []

    for inst in data_instances:
        name = vswhere_get_display_name(inst)
        versions = vswhere_get_version(inst)
        path = vswhere_get_path(inst)

        if name is None or versions is None or path is None:
            log.warn(
                f'Found a Visual Studio installation with incomplete information, skipping\n'
                f'    ({name=}, {versions=}, {path=})'
            )
            continue

        items.append({
            'version_major': versions[0],
            'version_full': versions[1],
            'name': name,
            'path': path
        })

    _installed_versions = items
    return True


def open_project_in_vs(version_major: str, project_path: str, project_name: str) -> bool:
    installation = get_installed_version(version_major, re_fetch=True)
    if installation is None:
        vs_info = get_supported_version(version_major)
        log.warn(f'Could not open project in Visual Studio, {vs_info["name"]} was not found.')
        return False

    sln_path = os.path.join(project_path, project_name + '.sln"')
    devenv_path = os.path.join(installation['path'], 'Common7', 'IDE', 'devenv.exe')
    cmd = ['start', devenv_path, sln_path]

    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        log.warn_called_process_error(e)
        return False

    return True


def enable_vsvars_env(version_major: str, done: Callable[[], None]) -> bool:
    installation = get_installed_version(version_major, re_fetch=True)
    if installation is None:
        vs_info = get_supported_version(version_major)
        log.error(f'Could not compile project in Visual Studio, {vs_info["name"]} was not found.')
        return False

    wrd = bpy.data.worlds['Arm']
    arch_bits = '64' if wrd.arm_project_win_build_arch == 'x64' else '32'
    vcvars_path = os.path.join(installation['path'], 'VC', 'Auxiliary', 'Build', 'vcvars' + arch_bits + '.bat')

    if not os.path.isfile(vcvars_path):
        log.error(
            'Could not compile project in Visual Studio\n'
            f'    File "{vcvars_path}" not found. Please verify that {installation["name"]} was installed correctly.'
        )
        return False

    state.proc_publish_build = arm.make.run_proc(vcvars_path, done)
    return True


def compile_in_vs(version_major: str, done: Callable[[], None]) -> bool:
    installation = get_installed_version(version_major, re_fetch=True)
    if installation is None:
        vs_info = get_supported_version(version_major)
        log.error(f'Could not compile project in Visual Studio, {vs_info["name"]} was not found.')
        return False

    wrd = bpy.data.worlds['Arm']

    msbuild_path = os.path.join(installation['path'], 'MSBuild', 'Current', 'Bin', 'MSBuild.exe')
    if not os.path.isfile(msbuild_path):
        log.error(
            'Could not compile project in Visual Studio\n'
            f'    File "{msbuild_path}" not found. Please verify that {installation["name"]} was installed correctly.'
        )
        return False

    project_name = arm.utils.safesrc(wrd.arm_project_name + '-' + wrd.arm_project_version)
    project_path = os.path.join(arm.utils.get_fp_build(), arm.utils.get_kha_target(state.target)) + '-build'
    projectfile_path = os.path.join(project_path, project_name + '.vcxproj')

    cmd = [msbuild_path, projectfile_path]

    # Arguments
    platform = 'x64' if wrd.arm_project_win_build_arch == 'x64' else 'win32'
    log_param = wrd.arm_project_win_build_log
    if log_param == 'WarningsAndErrorsOnly':
        log_param = 'WarningsOnly;ErrorsOnly'

    cmd.extend([
        '-m:' + str(wrd.arm_project_win_build_cpu),
        '-clp:' + log_param,
        '/p:Configuration=' + wrd.arm_project_win_build_mode,
        '/p:Platform=' + platform
    ])

    print('\nCompiling the project ' + projectfile_path)
    state.proc_publish_build = arm.make.run_proc(cmd, done)
    state.redraw_ui = True
    return True


def vswhere_get_display_name(instance_data: dict[str, Any]) -> Optional[str]:
    name_raw = instance_data.get('displayName', None)
    if name_raw is None:
        return None
    return arm.utils.safestr(name_raw).replace('_', ' ').strip()


def vswhere_get_version(instance_data: dict[str, Any]) -> Optional[tuple[str, str]]:
    version_raw = instance_data.get('installationVersion', None)
    if version_raw is None:
        return None

    version_full = version_raw.strip()
    version_major = version_full.split('.')[0]
    return version_major, version_full


def vswhere_get_path(instance_data: dict[str, Any]) -> Optional[str]:
    return instance_data.get('installationPath', None)


def vswhere_get_instances() -> Optional[list[dict[str, Any]]]:
    # vswhere.exe only exists at that location since VS2017 v15.2, for
    # earlier versions we'd need to package vswhere with Armory
    exe_path = os.path.join(os.environ["ProgramFiles(x86)"], 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
    command = [exe_path, '-format', 'json', '-utf8']

    try:
        result = subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        log.warn_called_process_error(e)
        return None
    except FileNotFoundError as e:
        log.warn(f'Could not open file "{exe_path}", make sure the file exists (errno {e.errno}).')
        return None

    result = json.loads(result.decode('utf-8'))
    return result
