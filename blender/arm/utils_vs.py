"""
Various utilities for interacting with Visual Studio on Windows.
"""
import json
import os
import re
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

_REGEX_SLN_MIN_VERSION = re.compile(r'MinimumVisualStudioVersion\s*=\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')


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


def fetch_installed_vs(silent=False) -> bool:
    global _installed_versions

    data_instances = _vswhere_get_instances(silent)
    if data_instances is None:
        return False

    items = []

    for inst in data_instances:
        name = _vswhere_get_display_name(inst)
        versions = _vswhere_get_version(inst)
        path = _vswhere_get_path(inst)

        if name is None or versions is None or path is None:
            if not silent:
                log.warn(
                    f'Found a Visual Studio installation with incomplete information, skipping\n'
                    f'    ({name=}, {versions=}, {path=})'
                )
            continue

        items.append({
            'version_major': versions[0],
            'version_full': versions[1],
            'version_full_ints': versions[2],
            'name': name,
            'path': path
        })

    # Store in descending order
    items.sort(key=lambda x: x['version_major'], reverse=True)

    _installed_versions = items
    return True


def open_project_in_vs(version_major: str, version_min_full: Optional[str] = None) -> bool:
    installation = get_installed_version(version_major, re_fetch=True)
    if installation is None:
        if version_min_full is not None:
            # Try whether other installed versions are supported, versions
            # are already sorted in descending order
            for installed_version in _installed_versions:
                if (installed_version['version_full_ints'] >= version_full_to_ints(version_min_full)
                        and int(installed_version['version_major']) < int(version_major)):
                    installation = installed_version
                    break

        # Still nothing found, warn for version_major
        if installation is None:
            vs_info = get_supported_version(version_major)
            log.warn(f'Could not open project in Visual Studio, {vs_info["name"]} was not found.')
            return False

    sln_path = get_sln_path()
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

    projectfile_path = get_vcxproj_path()

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


def _vswhere_get_display_name(instance_data: dict[str, Any]) -> Optional[str]:
    name_raw = instance_data.get('displayName', None)
    if name_raw is None:
        return None
    return arm.utils.safestr(name_raw).replace('_', ' ').strip()


def _vswhere_get_version(instance_data: dict[str, Any]) -> Optional[tuple[str, str, tuple[int, ...]]]:
    version_raw = instance_data.get('installationVersion', None)
    if version_raw is None:
        return None

    version_full = version_raw.strip()
    version_full_ints = version_full_to_ints(version_full)
    version_major = version_full.split('.')[0]
    return version_major, version_full, version_full_ints


def _vswhere_get_path(instance_data: dict[str, Any]) -> Optional[str]:
    return instance_data.get('installationPath', None)


def _vswhere_get_instances(silent=False) -> Optional[list[dict[str, Any]]]:
    # vswhere.exe only exists at that location since VS2017 v15.2, for
    # earlier versions we'd need to package vswhere with Armory
    exe_path = os.path.join(os.environ["ProgramFiles(x86)"], 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
    command = [exe_path, '-format', 'json', '-utf8']

    try:
        result = subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        # Do not silence this warning, if this exception is caught there
        # likely is an issue in the command above
        log.warn_called_process_error(e)
        return None
    except FileNotFoundError as e:
        if not silent:
            log.warn(f'Could not open file "{exe_path}", make sure the file exists (errno {e.errno}).')
        return None

    result = json.loads(result.decode('utf-8'))
    return result


def version_full_to_ints(version_full: str) -> tuple[int, ...]:
    return tuple(int(i) for i in version_full.split('.'))


def get_project_path() -> str:
    return os.path.join(arm.utils.get_fp_build(), 'windows-hl-build')


def get_project_name():
    wrd = bpy.data.worlds['Arm']
    return arm.utils.safesrc(wrd.arm_project_name + '-' + wrd.arm_project_version)


def get_sln_path() -> str:
    project_path = get_project_path()
    project_name = get_project_name()
    return os.path.join(project_path, project_name + '.sln')


def get_vcxproj_path() -> str:
    project_name = get_project_name()
    project_path = get_project_path()
    return os.path.join(project_path, project_name + '.vcxproj')


def fetch_project_version() -> tuple[Optional[str], Optional[str], Optional[str]]:
    version_major = None
    version_min_full = None

    try:
        # References:
        # https://learn.microsoft.com/en-us/visualstudio/extensibility/internals/solution-dot-sln-file?view=vs-2022#file-header
        # https://github.com/Kode/kmake/blob/a104a89b55218054ceed761d5bc75d6e5cd60573/kmake/src/Exporters/VisualStudioExporter.ts#L188-L225
        with open(get_sln_path(), 'r') as file:
            for linenum, line in enumerate(file):
                line = line.strip()

                if linenum == 1:
                    if line == '# Visual Studio Version 17':
                        version_major = 17
                    elif line == '# Visual Studio Version 16':
                        version_major = 16
                    elif line == '# Visual Studio 15':
                        version_major = 15
                    elif line == '# Visual Studio 14':
                        version_major = 14
                    elif line == '# Visual Studio 2013':
                        version_major = 12
                    elif line == '# Visual Studio 2012':
                        version_major = 11
                    elif line == '# Visual Studio 2010':
                        version_major = 10
                    else:
                        log.warn(f'Could not parse Visual Studio version. Invalid major version, parsed {line}')
                        return None, None, 'err_invalid_version_major'

                elif linenum == 3 and version_major >= 12:
                    match = _REGEX_SLN_MIN_VERSION.match(line)
                    if match:
                        version_min_full = match.group(1)
                        break

                    log.warn(f'Could not parse Visual Studio version. Invalid full version, parsed {line}')
                    return None, None, 'err_invalid_version_full'

    except FileNotFoundError:
        return None, None, 'err_file_not_found'

    return str(version_major), version_min_full, None
