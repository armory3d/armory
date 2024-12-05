from enum import Enum, unique
import glob
import itertools
import json
import locale
import os
import platform
import random
import re
import shlex
import shutil
import subprocess
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
import webbrowser

import numpy as np

import bpy

import arm.lib.armpack
from arm.lib.lz4 import LZ4
import arm.log as log
import arm.make_state as state
import arm.props_renderpath

if arm.is_reload(__name__):
    arm.lib.armpack = arm.reload_module(arm.lib.armpack)
    arm.lib.lz4 = arm.reload_module(arm.lib.lz4)
    from arm.lib.lz4 import LZ4
    log = arm.reload_module(log)
    state = arm.reload_module(state)
    arm.props_renderpath = arm.reload_module(arm.props_renderpath)
else:
    arm.enable_reload(__name__)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class WorkingDir:
    """Context manager for safely changing the current working directory."""
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.prev_cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self.cwd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.prev_cwd)

def write_arm(filepath, output):
    if filepath.endswith('.lz4'):
        with open(filepath, 'wb') as f:
            packed = arm.lib.armpack.packb(output)
            # Prepend packed data size for decoding. Haxe can't unpack
            # an unsigned int64 so we use a signed int64 here
            f.write(np.int64(LZ4.encode_bound(len(packed))).tobytes())

            f.write(LZ4.encode(packed))
    else:
        if bpy.data.worlds['Arm'].arm_minimize:
            with open(filepath, 'wb') as f:
                f.write(arm.lib.armpack.packb(output))
        else:
            filepath_json = filepath.split('.arm')[0] + '.json'
            with open(filepath_json, 'w') as f:
                f.write(json.dumps(output, sort_keys=True, indent=4, cls=NumpyEncoder))

def unpack_image(image, path, file_format='JPEG'):
    print('Armory Info: Unpacking to ' + path)
    image.filepath_raw = path
    image.file_format = file_format
    image.save()

def convert_image(image, path, file_format='JPEG'):
    # Convert image to compatible format
    print('Armory Info: Converting to ' + path)
    ren = bpy.context.scene.render
    orig_quality = ren.image_settings.quality
    orig_file_format = ren.image_settings.file_format
    orig_color_mode = ren.image_settings.color_mode
    ren.image_settings.quality = get_texture_quality_percentage()
    ren.image_settings.file_format = file_format
    if file_format == 'PNG':
        ren.image_settings.color_mode = 'RGBA'
    orig_image_colorspace = image.colorspace_settings.name
    image.colorspace_settings.name = 'Non-Color'
    image.save_render(path, scene=bpy.context.scene)
    image.colorspace_settings.name = orig_image_colorspace
    ren.image_settings.quality = orig_quality
    ren.image_settings.file_format = orig_file_format
    ren.image_settings.color_mode = orig_color_mode


def get_random_color_rgb() -> list[float]:
    """Return a random RGB color with values in range [0, 1]."""
    return [random.random(), random.random(), random.random()]


def is_livepatch_enabled():
    """Returns whether live patch is enabled and can be used."""
    wrd = bpy.data.worlds['Arm']
    # If the game is published, the target is krom-[OS] and not krom,
    # so there is no live patch when publishing
    return wrd.arm_live_patch and state.target == 'krom'


def blend_name():
    return bpy.path.basename(bpy.context.blend_data.filepath).rsplit('.', 1)[0]

def build_dir():
    return 'build_' + safestr(blend_name())


def get_fp() -> str:
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_project_root != '':
        return bpy.path.abspath(wrd.arm_project_root)
    else:
        s = None
        if use_local_sdk and bpy.data.filepath == '':
            s = os.getcwd()
        else:
            s = bpy.data.filepath.split(os.path.sep)
            s.pop()
            s = os.path.sep.join(s)
        if get_os_is_windows() and len(s) == 2 and s[1] == ':':
            # If the project is located at a drive root (C:/ for example),
            # then s = "C:". If joined later with another path, no path
            # separator is added by default because C:some_path is valid
            # Windows path syntax (some_path is then relative to the CWD on the
            # C drive). We prevent this by manually adding the path separator
            # in these cases. Please refer to the Python doc of os.path.join()
            # for more details.
            s += os.path.sep
        return s


def get_fp_build():
    return os.path.join(get_fp(), build_dir())


def to_absolute_path(path: str, from_library: Optional[bpy.types.Library] = None) -> str:
    """Convert the given absolute or relative path into an absolute path.

    - If `from_library` is not set (default), a given relative path will be
      interpreted as relative to the project directory.
    - If `from_library` is set, a given relative path will be interpreted as
      relative to the filepath of the specified library.
    """
    return os.path.normpath(bpy.path.abspath(path, start=get_fp(), library=from_library))


def get_os() -> str:
    s = platform.system()
    if s == 'Windows':
        return 'win'
    elif s == 'Darwin':
        return 'mac'
    else:
        return 'linux'


def get_os_is_windows() -> bool:
    return get_os() == 'win'


def get_os_is_windows_64() -> bool:
    if platform.machine().endswith('64'):
        return True
    # Checks if Python (32 bit) is running on Windows (64 bit)
    if 'PROCESSOR_ARCHITEW6432' in os.environ:
        return True
    if os.environ['PROCESSOR_ARCHITECTURE'].endswith('64'):
        return True
    if 'PROGRAMFILES(X86)' in os.environ:
        if os.environ['PROGRAMW6432'] is not None:
            return True
    else:
        return False


def get_gapi():
    wrd = bpy.data.worlds['Arm']
    if state.is_export:
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        return getattr(item, target_to_gapi(item.arm_project_target))
    if wrd.arm_runtime == 'Browser':
        return 'webgl'
    return 'direct3d11' if get_os() == 'win' else 'opengl'


def is_gapi_gl_es() -> bool:
    """Return whether the currently targeted graphics API is using OpenGL ES."""
    wrd = bpy.data.worlds['Arm']

    if state.is_export:
        item_exporter = wrd.arm_exporterlist[wrd.arm_exporterlist_index]

        # See Khamake's ShaderCompiler.findType() and krafix::Target.es in krafix.cpp ("target.es")
        if state.target == 'android-hl':
            return item_exporter.arm_gapi_android == 'opengl'
        if state.target == 'ios-hl':
            return item_exporter.arm_gapi_ios == 'opengl'
        elif state.target == 'html5':
            return True
        return False

    else:
        return wrd.arm_runtime == 'Browser'


def get_rp() -> arm.props_renderpath.ArmRPListItem:
    wrd = bpy.data.worlds['Arm']
    if not state.is_export and wrd.arm_play_renderpath != '':
        return arm.props_renderpath.ArmRPListItem.get_by_name(wrd.arm_play_renderpath)
    else:
        return wrd.arm_rplist[wrd.arm_rplist_index]


# Passed by load_post handler when armsdk is found in project folder
use_local_sdk = False
def get_sdk_path():
    addon_prefs = get_arm_preferences()
    if use_local_sdk:
        return os.path.normpath(get_fp() + '/armsdk/')
    else:
        return os.path.normpath(addon_prefs.sdk_path)

def get_last_commit():
    p = get_sdk_path() + 'armory/.git/refs/heads/main'

    try:
        file = open(p, 'r')
        commit = file.readline()
    except:
        commit = ''
    return commit


def get_arm_preferences() -> bpy.types.AddonPreferences:
    preferences = bpy.context.preferences
    return preferences.addons["armory"].preferences


def get_ide_bin():
    addon_prefs = get_arm_preferences()
    return '' if not hasattr(addon_prefs, 'ide_bin') else addon_prefs.ide_bin

def get_ffmpeg_path():
    path = get_arm_preferences().ffmpeg_path
    if path == "": path = shutil.which("ffmpeg")
    return path

def get_renderdoc_path():
    p = get_arm_preferences().renderdoc_path
    if p == '' and get_os() == 'win':
        pdefault = 'C:\\Program Files\\RenderDoc\\qrenderdoc.exe'
        if os.path.exists(pdefault):
            p = pdefault
    return p

def get_code_editor():
    addon_prefs = get_arm_preferences()
    return 'kodestudio' if not hasattr(addon_prefs, 'code_editor') else addon_prefs.code_editor

def get_ui_scale():
    addon_prefs = get_arm_preferences()
    return 1.0 if not hasattr(addon_prefs, 'ui_scale') else addon_prefs.ui_scale

def get_khamake_threads() -> int:
    addon_prefs = get_arm_preferences()
    if hasattr(addon_prefs, 'khamake_threads_use_auto') and addon_prefs.khamake_threads_use_auto:
        return -1
    return 1 if not hasattr(addon_prefs, 'khamake_threads') else addon_prefs.khamake_threads

def get_compilation_server():
    addon_prefs = get_arm_preferences()
    return False if not hasattr(addon_prefs, 'compilation_server') else addon_prefs.compilation_server

def get_save_on_build():
    addon_prefs = get_arm_preferences()
    return False if not hasattr(addon_prefs, 'save_on_build') else addon_prefs.save_on_build

def get_debug_console_auto():
    addon_prefs = get_arm_preferences()
    return False if not hasattr(addon_prefs, 'debug_console_auto') else addon_prefs.debug_console_auto

def get_debug_console_visible_sc():
    addon_prefs = get_arm_preferences()
    return 192 if not hasattr(addon_prefs, 'debug_console_visible_sc') else addon_prefs.debug_console_visible_sc

def get_debug_console_scale_in_sc():
    addon_prefs = get_arm_preferences()
    return 219 if not hasattr(addon_prefs, 'debug_console_scale_in_sc') else addon_prefs.debug_console_scale_in_sc

def get_debug_console_scale_out_sc():
    addon_prefs = get_arm_preferences()
    return 221 if not hasattr(addon_prefs, 'debug_console_scale_out_sc') else addon_prefs.debug_console_scale_out_sc

def get_viewport_controls():
    addon_prefs = get_arm_preferences()
    return 'qwerty' if not hasattr(addon_prefs, 'viewport_controls') else addon_prefs.viewport_controls

def get_legacy_shaders():
    addon_prefs = get_arm_preferences()
    return False if not hasattr(addon_prefs, 'legacy_shaders') else addon_prefs.legacy_shaders

def get_relative_paths():
    """Whether to convert absolute paths to relative"""
    addon_prefs = get_arm_preferences()
    return False if not hasattr(addon_prefs, 'relative_paths') else addon_prefs.relative_paths

def get_pref_or_default(prop_name: str, default: Any) -> Any:
    """Return the preference setting for prop_name, or the value given as default if the property does not exist."""
    addon_prefs = get_arm_preferences()
    return getattr(addon_prefs, prop_name, default)

def get_node_path():
    if get_os() == 'win':
        return get_sdk_path() + '/nodejs/node.exe'
    elif get_os() == 'mac':
        return get_sdk_path() + '/nodejs/node-osx'
    else:
        return get_sdk_path() + '/nodejs/node-linux64'

def get_kha_path():
    if os.path.exists('Kha'):
        return 'Kha'
    return get_sdk_path() + '/Kha'

def get_haxe_path():
    if get_os() == 'win':
        return get_kha_path() + '/Tools/windows_x64/haxe.exe'
    elif get_os() == 'mac':
        return get_kha_path() + '/Tools/macos/haxe'
    else:
        return get_kha_path() + '/Tools/linux_x64/haxe'

def get_khamake_path():
    return get_kha_path() + '/make'

def krom_paths():
    sdk_path = get_sdk_path()
    if arm.utils.get_os() == 'win':
        krom_location = sdk_path + '/Krom'
        krom_path = krom_location + '/Krom.exe'
    elif arm.utils.get_os() == 'mac':
        krom_location = sdk_path + '/Krom/Krom.app/Contents/MacOS'
        krom_path = krom_location + '/Krom'
    else:
        krom_location = sdk_path + '/Krom'
        krom_path = krom_location + '/Krom'
    return krom_location, krom_path

def fetch_bundled_script_names():
    wrd = bpy.data.worlds['Arm']
    wrd.arm_bundled_scripts_list.clear()

    with WorkingDir(get_sdk_path() + '/armory/Sources/armory/trait'):
        for file in glob.glob('*.hx'):
            wrd.arm_bundled_scripts_list.add().name = file.rsplit('.', 1)[0]


script_props = {}
script_props_defaults = {}
script_warnings: Dict[str, List[Tuple[str, str]]] = {}  # Script name -> List of (identifier, warning message)

# See https://regex101.com/r/bbrCzN/8
RX_MODIFIERS = r'(?P<modifiers>(?:public\s+|private\s+|static\s+|inline\s+|final\s+)*)?'  # Optional modifiers
RX_IDENTIFIER = r'(?P<identifier>[_$a-z]+[_a-z0-9]*)'  # Variable name, follow Haxe rules
RX_TYPE = r'(?:\s*:\s*(?P<type>[_a-z]+[\._a-z0-9]*))?'  # Optional type annotation
RX_VALUE = r'(?:\s*=\s*(?P<value>(?:\".*\")|(?:[^;]+)|))?'  # Optional default value

PROP_REGEX_RAW = fr'@prop\s+{RX_MODIFIERS}(?P<attr_type>var|final)\s+{RX_IDENTIFIER}{RX_TYPE}{RX_VALUE};'
PROP_REGEX = re.compile(PROP_REGEX_RAW, re.IGNORECASE)
def fetch_script_props(filename: str):
    """Parses @prop declarations from the given Haxe script."""
    with open(filename, 'r', encoding='utf-8') as sourcefile:
        source = sourcefile.read()

    if source == '':
        return

    name = filename.rsplit('.', 1)[0]

    # Convert the name into a package path relative to the "Sources" dir
    if 'Sources' in name:
        name = name[name.index('Sources') + 8:]
    if '/' in name:
        name = name.replace('/', '.')
    if '\\' in filename:
        name = name.replace('\\', '.')

    script_props[name] = []
    script_props_defaults[name] = []
    script_warnings[name] = []

    for match in re.finditer(PROP_REGEX, source):

        p_modifiers: Optional[str] = match.group('modifiers')
        p_identifier: str = match.group('identifier')
        p_type: Optional[str] = match.group('type')
        p_default_val: Optional[str] = match.group('value')

        if p_modifiers is not None:
            if 'static' in p_modifiers:
                script_warnings[name].append((p_identifier, '`static` modifier might cause unwanted behaviour!'))
            if 'inline' in p_modifiers:
                script_warnings[name].append((p_identifier, '`inline` modifier is not supported!'))
                continue
            if 'final' in p_modifiers or match.group('attr_type') == 'final':
                script_warnings[name].append((p_identifier, '`final` properties are not supported!'))
                continue

        # Property type is annotated
        if p_type is not None:
            if p_type.startswith("iron.object."):
                p_type = p_type[12:]
            elif p_type.startswith("iron.math."):
                p_type = p_type[10:]

            type_default_val = get_type_default_value(p_type)
            if type_default_val is None:
                script_warnings[name].append((p_identifier, f'unsupported type `{p_type}`!'))
                continue

            # Default value exists
            if p_default_val is not None:
                # Remove string quotes
                p_default_val = p_default_val.replace('\'', '').replace('"', '')
            else:
                p_default_val = type_default_val

        # Default value is given instead, try to infer the properties type from it
        elif p_default_val is not None:
            p_type = get_prop_type_from_value(p_default_val)

            # Type is not recognized
            if p_type is None:
                script_warnings[name].append((p_identifier, 'could not infer property type from given value!'))
                continue
            if p_type == "String":
                p_default_val = p_default_val.replace('\'', '').replace('"', '')

        else:
            script_warnings[name].append((p_identifier, 'missing type or default value!'))
            continue

        # Register prop
        prop = (p_identifier, p_type)
        script_props[name].append(prop)
        script_props_defaults[name].append(p_default_val)


def get_prop_type_from_value(value: str):
    """
    Returns the property type based on its representation in the code.

    If the type is not supported, `None` is returned.
    """
    # Maybe ast.literal_eval() is better here?
    try:
        int(value)
        return "Int"
    except ValueError:
        try:
            float(value)
            return "Float"
        except ValueError:
            # "" is required, " alone will not work
            if len(value) > 1 and value.startswith(("\"", "'")) and value.endswith(("\"", "'")):
                return "String"
            if value in ("true", "false"):
                return "Bool"
            if value.startswith("new "):
                value = value.split()[1].split("(")[0]
                if value.startswith("Vec"):
                    return value
                if value.startswith("iron.math.Vec"):
                    return value[10:]

    return None

def get_type_default_value(prop_type: str):
    """
    Returns the default value of the given Haxe type.

    If the type is not supported, `None` is returned:
    """
    if prop_type == "Int":
        return 0
    if prop_type == "Float":
        return 0.0
    if prop_type == "String" or prop_type in (
            "Object", "CameraObject", "LightObject", "MeshObject", "SpeakerObject"):
        return ""
    if prop_type == "Bool":
        return False
    if prop_type == "Vec2":
        return [0.0, 0.0]
    if prop_type == "Vec3":
        return [0.0, 0.0, 0.0]
    if prop_type == "Vec4":
        return [0.0, 0.0, 0.0, 0.0]

    return None

def fetch_script_names():
    if bpy.data.filepath == "":
        return
    wrd = bpy.data.worlds['Arm']
    # Sources
    wrd.arm_scripts_list.clear()
    sources_path = os.path.join(get_fp(), 'Sources', safestr(wrd.arm_project_package))
    if os.path.isdir(sources_path):
        with WorkingDir(sources_path):
            # Glob supports recursive search since python 3.5 so it should cover both blender 2.79 and 2.8 integrated python
            for file in glob.glob('**/*.hx', recursive=True):
                mod = file.rsplit('.', 1)[0]
                mod = mod.replace('\\', '/')
                mod_parts = mod.rsplit('/')
                if re.match('^[A-Z][A-Za-z0-9_]*$', mod_parts[-1]):
                    wrd.arm_scripts_list.add().name = mod.replace('/', '.')
                    fetch_script_props(file)

    # Canvas
    wrd.arm_canvas_list.clear()
    canvas_path = get_fp() + '/Bundled/canvas'
    if os.path.isdir(canvas_path):
        with WorkingDir(canvas_path):
            for file in glob.glob('*.json'):
                if file == "_themes.json":
                    continue
                wrd.arm_canvas_list.add().name = file.rsplit('.', 1)[0]

def fetch_wasm_names():
    if bpy.data.filepath == "":
        return
    wrd = bpy.data.worlds['Arm']
    # WASM modules
    wrd.arm_wasm_list.clear()
    sources_path = get_fp() + '/Bundled'
    if os.path.isdir(sources_path):
        with WorkingDir(sources_path):
            for file in glob.glob('*.wasm'):
                name = file.rsplit('.', 1)[0]
                wrd.arm_wasm_list.add().name = name


def fetch_trait_props():
    for o in bpy.data.objects:
        if o.override_library is None:
            # We can't update the list of trait properties for linked
            # objects because Blender doesn't allow to remove items from
            # overridden lists
            fetch_prop(o)

    for s in bpy.data.scenes:
        fetch_prop(s)


def fetch_prop(o: Union[bpy.types.Object, bpy.types.Scene]):
    for item in o.arm_traitlist:
        if item.type_prop == 'Bundled Script':
            name = 'armory.trait.' + item.name
        else:
            name = item.name
        if name not in script_props:
            continue
        props = script_props[name]
        defaults = script_props_defaults[name]
        warnings = script_warnings[name]

        # Remove old props
        for i in range(len(item.arm_traitpropslist) - 1, -1, -1):
            ip = item.arm_traitpropslist[i]
            if ip.name not in [p[0] for p in props]:
                item.arm_traitpropslist.remove(i)

        # Add new props
        for index, p in enumerate(props):
            found_prop = False
            for i_prop in item.arm_traitpropslist:
                if i_prop.name == p[0]:
                    if i_prop.type == p[1]:
                        found_prop = i_prop
                    else:
                        item.arm_traitpropslist.remove(item.arm_traitpropslist.find(i_prop.name))
                    break

            # Not in list
            if not found_prop:
                prop = item.arm_traitpropslist.add()
                prop.name = p[0]
                prop.type = p[1]
                prop.set_value(defaults[index])

            if found_prop:
                prop = item.arm_traitpropslist[found_prop.name]

                # Default value added and current value is blank (no override)
                if (found_prop.get_value() is None
                        or found_prop.get_value() == "") and defaults[index]:
                    prop.set_value(defaults[index])
                # Type has changed, update displayed name
                if len(found_prop.name) == 1 or (len(found_prop.name) > 1 and found_prop.name[1] != p[1]):
                    prop.name = p[0]
                    prop.type = p[1]

            item.arm_traitpropswarnings.clear()
            for warning in warnings:
                entry = item.arm_traitpropswarnings.add()
                entry.propName = warning[0]
                entry.warning = warning[1]


def fetch_bundled_trait_props():
    # Bundled script props
    for o in bpy.data.objects:
        for t in o.arm_traitlist:
            if t.type_prop == 'Bundled Script':
                file_path = get_sdk_path() + '/armory/Sources/armory/trait/' + t.name + '.hx'
                if os.path.exists(file_path):
                    fetch_script_props(file_path)
                    fetch_prop(o)

def update_trait_collections():
    for col in bpy.data.collections:
        if col.name.startswith('Trait|'):
            bpy.data.collections.remove(col)
    for o in bpy.data.objects:
        for t in o.arm_traitlist:
            if 'Trait|' + t.name not in bpy.data.collections:
                col = bpy.data.collections.new('Trait|' + t.name)
            else:
                col = bpy.data.collections['Trait|' + t.name]
            col.objects.link(o)


def to_hex(val):
    return '#%02x%02x%02x%02x' % (int(val[3] * 255), int(val[0] * 255), int(val[1] * 255), int(val[2] * 255))


def color_to_int(val) -> int:
    # Clamp values, otherwise the return value might not fit in 32 bit
    # (and later cause problems, e.g. in the .arm file reader)
    val = [max(0.0, min(v, 1.0)) for v in val]
    return (int(val[3] * 255) << 24) + (int(val[0] * 255) << 16) + (int(val[1] * 255) << 8) + int(val[2] * 255)


def unique_name_in_lists(item_lists: Iterable[list], name_attr: str, wanted_name: str, ignore_item: Optional[Any] = None) -> str:
    """Creates a unique name that no item in the given lists already has.
    The format follows Blender's behaviour when handling duplicate
    object names.

    @param item_lists An iterable of item lists (any type).
    @param name_attr The attribute of the items that holds the name.
    @param wanted_name The name that should be preferably returned, if
        no name collision occurs.
    @param ignore_item (Optional) Ignore this item in the list when
        comparing names.
    """
    def _has_collision(name: str) -> bool:
        for item in itertools.chain(*item_lists):
            if item == ignore_item:
                continue
            if getattr(item, name_attr) == name:
                return True
        return False

    # Check this once at the beginning to make sure the user can use
    # a wanted name like "XY.001" if they want, even if "XY" alone does
    # not collide
    if not _has_collision(wanted_name):
        return wanted_name

    # Get base name without numeric suffix
    base_name = wanted_name
    dot_pos = base_name.rfind('.')
    if dot_pos != -1:
        if base_name[dot_pos + 1:].isdecimal():
            base_name = base_name[:dot_pos]

    num_collisions = 0
    out_name = base_name
    while _has_collision(out_name):
        num_collisions += 1
        out_name = f'{base_name}.{num_collisions:03d}'

    return out_name


def merge_into_collection(col_src, col_dst, clear_dst=True):
    """Merges the items of the `col_src` collection property into the
    `col_dst` collection property.

    If `clear_dst` is true, the destination collection is cleared before
    merging. Otherwise, new items are added on top of the existing items
    in `col_dst`. There is no check for duplicates.
    """
    if clear_dst:
        col_dst.clear()

    for item_src in col_src:
        item_dst = col_dst.add()

        # collect names of writable properties
        prop_names = [p.identifier for p in item_src.bl_rna.properties
                      if not p.is_readonly]

        # copy those properties
        for prop_name in prop_names:
            setattr(item_dst, prop_name, getattr(item_src, prop_name))


def safesrc(s):
    s = safestr(s).replace('.', '_').replace('-', '_').replace(' ', '')
    if s[0].isdigit():
        s = '_' + s
    return s

def safestr(s: str) -> str:
    """Outputs a string where special characters have been replaced with
    '_', which can be safely used in file and path names."""
    for c in r'''[]/\;,><&*:§$%=+@!#^()|?^'"''':
        s = s.replace(c, '_')
    return ''.join([i if ord(i) < 128 else '_' for i in s])

def get_haxe_json_string(d: dict) -> str:
    s = str(d)
    s = s.replace('True', 'true')
    s = s.replace('False', 'false')
    s = s.replace("'", '"')
    return s

def asset_name(bdata):
    if bdata == None:
        return None
    s = bdata.name
    # Append library name if linked
    if bdata.library is not None:
        s += '_' + bdata.library.name
    return s

def asset_path(s):
    """Remove leading '//'"""
    return s[2:] if s[:2] == '//' else s

def extract_filename(s):
    return os.path.basename(asset_path(s))

def get_render_resolution(scene):
    render = scene.render
    scale = render.resolution_percentage / 100
    return int(render.resolution_x * scale), int(render.resolution_y * scale)

def get_texture_quality_percentage() -> int:
    return int(bpy.data.worlds['Arm'].arm_texture_quality * 100)

def get_project_scene_name():
    return get_active_scene().name

def get_active_scene() -> bpy.types.Scene:
    wrd = bpy.data.worlds['Arm']
    if not state.is_export:
        if wrd.arm_play_scene is None:
            return bpy.context.scene
        return wrd.arm_play_scene
    else:
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        return item.arm_project_scene

def logic_editor_space(context_screen=None):
    if context_screen == None:
        context_screen = bpy.context.screen
    if context_screen != None:
        areas = context_screen.areas
        for area in areas:
            for space in area.spaces:
                if space.type == 'NODE_EDITOR':
                    if space.node_tree != None and space.node_tree.bl_idname == 'ArmLogicTreeType':
                        return space
    return None

def voxel_support():
    # macos does not support opengl 4.5, needs metal
    return state.target != 'html5' and get_os() != 'mac'

def get_cascade_size(rpdat):
    cascade_size = int(rpdat.rp_shadowmap_cascade)
    # Clamp to 4096 per cascade
    if int(rpdat.rp_shadowmap_cascades) > 1 and cascade_size > 4096:
        cascade_size = 4096
    return cascade_size


def check_blender_version(op: bpy.types.Operator):
    """Check whether the Blender version is supported by Armory,
    if not, report in UI.
    """
    if bpy.app.version[0] != 3 or bpy.app.version[1] != 6:
        op.report({'INFO'}, 'For Armory to work correctly, you need Blender 3.6 LTS.')


def check_saved(self):
    if bpy.data.filepath == "":
        msg = "Save blend file first"
        self.report({"ERROR"}, msg) if self is not None else log.warn(msg)
        return False
    return True

def check_path(s):
    for c in r'[];><&*%=+@!#^()|?^':
        if c in s:
            return False
    for c in s:
        if ord(c) > 127:
            return False
    return True

def check_sdkpath(self):
    s = get_sdk_path()
    if not check_path(s):
        msg = f"SDK path '{s}' contains special characters. Please move SDK to different path for now."
        self.report({"ERROR"}, msg) if self is not None else log.warn(msg)
        return False
    else:
        return True

def check_projectpath(self):
    s = get_fp()
    if not check_path(s):
        msg = f"Project path '{s}' contains special characters, build process may fail."
        self.report({"ERROR"}, msg) if self is not None else log.warn(msg)
        return False
    else:
        return True

def disp_enabled(target):
    rpdat = get_rp()
    if rpdat.arm_rp_displacement == 'Tessellation':
        return target == 'krom' or target == 'native'
    return rpdat.arm_rp_displacement != 'Off'

def is_object_animation_enabled(bobject):
    # Checks if animation is present and enabled
    if bobject.arm_animation_enabled == False or bobject.type == 'BONE' or bobject.type == 'ARMATURE':
        return False
    if bobject.animation_data and bobject.animation_data.action:
        return True
    return False

def is_bone_animation_enabled(bobject):
    # Checks if animation is present and enabled for parented armature
    if bobject.parent and bobject.parent.type == 'ARMATURE':
        if bobject.parent.arm_animation_enabled == False:
            return False
        # Check for present actions
        adata = bobject.parent.animation_data
        has_actions = adata != None and adata.action != None
        if not has_actions and adata != None:
            if hasattr(adata, 'nla_tracks') and adata.nla_tracks != None:
                for track in adata.nla_tracks:
                    if track.strips == None:
                        continue
                    for strip in track.strips:
                        if strip.action == None:
                            continue
                        has_actions = True
                        break
                    if has_actions:
                        break
        if adata != None and has_actions:
            return True
    return False


def export_bone_data(bobject: bpy.types.Object) -> bool:
    """Returns whether the bone data of the given object should be exported."""
    return bobject.find_armature() and is_bone_animation_enabled(bobject) and get_rp().arm_skin == 'On'

def export_morph_targets(bobject: bpy.types.Object) -> bool:
    if get_rp().arm_morph_target != 'On':
        return False

    if not hasattr(bobject.data, 'shape_keys'):
        return False

    shape_keys = bobject.data.shape_keys
    if not shape_keys:
        return False
    if len(shape_keys.key_blocks) < 2:
        return False
    for shape_key in shape_keys.key_blocks[1:]:
            if(not shape_key.mute):
                return True
    return False

def export_vcols(bobject: bpy.types.Object) -> bool:
    for material in bobject.data.materials:
        if material is not None and material.export_vcols:
            return True
    return False

def open_editor(hx_path=None):
    ide_bin = get_ide_bin()

    if hx_path is None:
        hx_path = arm.utils.get_fp()

    if get_code_editor() == 'default':
        # Get editor environment variables
        # https://unix.stackexchange.com/q/4859
        env_v_editor = os.environ.get('VISUAL')
        env_editor = os.environ.get('EDITOR')

        if env_v_editor is not None:
            ide_bin = env_v_editor
        elif env_editor is not None:
            ide_bin = env_editor

        # No environment variables set -> Let the system decide how to
        # open the file
        else:
            webbrowser.open('file://' + hx_path)
            return

    if os.path.exists(ide_bin):
        args = [ide_bin, arm.utils.get_fp()]

        # Sublime Text
        if get_code_editor() == 'sublime':
            project_name = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_name)
            subl_project_path = arm.utils.get_fp() + f'/{project_name}.sublime-project'

            if not os.path.exists(subl_project_path):
                generate_sublime_project(subl_project_path)

            args += ['--project', subl_project_path]

            args.append('--add')

        args.append(hx_path)

        if arm.utils.get_os() == 'mac':
            argstr = ""

            for arg in args:
                if not (arg.startswith('-') or arg.startswith('--')):
                    argstr += '"' + arg + '"'
                argstr += ' '

            subprocess.Popen(argstr[:-1], shell=True)
        else:
            subprocess.Popen(args)

    else:
        raise FileNotFoundError(f'Code editor executable not found: {ide_bin}. You can change the path in the Armory preferences.')

def open_folder(folder_path: str):
    if arm.utils.get_os() == 'win':
        subprocess.run(['explorer', folder_path])
    elif arm.utils.get_os() == 'mac':
        subprocess.run(['open', folder_path])
    elif arm.utils.get_os() == 'linux':
        subprocess.run(['xdg-open', folder_path])
    else:
        webbrowser.open('file://' + folder_path)

def generate_sublime_project(subl_project_path):
    """Generates a [project_name].sublime-project file."""
    print('Generating Sublime Text project file')

    project_data = {
        "folders": [
            {
                "path": ".",
                "file_exclude_patterns": ["*.blend*", "*.arm"]
            },
        ],
    }

    with open(subl_project_path, 'w', encoding='utf-8') as project_file:
        json.dump(project_data, project_file, ensure_ascii=False, indent=4)

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def get_kha_target(target_name): # TODO: remove
    if target_name == 'macos-hl':
        return 'osx-hl'
    elif target_name.startswith('krom'): # krom-windows
        return 'krom'
    elif target_name == 'custom':
        return ''
    return target_name


def target_to_gapi(arm_project_target: str) -> str:
    # TODO: align target names
    if arm_project_target == 'krom':
        return 'arm_gapi_' + arm.utils.get_os()
    elif arm_project_target == 'krom-windows':
        return 'arm_gapi_win'
    elif arm_project_target == 'windows-hl':
        return 'arm_gapi_win'
    elif arm_project_target == 'krom-linux':
        return 'arm_gapi_linux'
    elif arm_project_target == 'linux-hl':
        return 'arm_gapi_linux'
    elif arm_project_target == 'krom-macos':
        return 'arm_gapi_mac'
    elif arm_project_target == 'macos-hl':
        return 'arm_gapi_mac'
    elif arm_project_target == 'android-hl':
        return 'arm_gapi_android'
    elif arm_project_target == 'ios-hl':
        return 'arm_gapi_ios'
    elif arm_project_target == 'node':
        return 'arm_gapi_html5'
    else: # html5, custom
        return 'arm_gapi_' + arm_project_target


def check_default_props():
    wrd = bpy.data.worlds['Arm']
    if len(wrd.arm_rplist) == 0:
        wrd.arm_rplist.add()
        wrd.arm_rplist_index = 0

    if wrd.arm_project_name == '':
        # Take blend file name
        wrd.arm_project_name = arm.utils.blend_name()

# Enum Permissions Name
class PermissionName(Enum):
    ACCESS_COARSE_LOCATION = 'ACCESS_COARSE_LOCATION'
    ACCESS_NETWORK_STATE = 'ACCESS_NETWORK_STATE'
    ACCESS_FINE_LOCATION = 'ACCESS_FINE_LOCATION'
    ACCESS_WIFI_STATE = 'ACCESS_WIFI_STATE'
    BLUETOOTH = 'BLUETOOTH'
    BLUETOOTH_ADMIN = 'BLUETOOTH_ADMIN'
    CAMERA = 'CAMERA'
    EXPAND_STATUS_BAR = 'EXPAND_STATUS_BAR'
    FOREGROUND_SERVICE = 'FOREGROUND_SERVICE'
    GET_ACCOUNTS = 'GET_ACCOUNTS'
    INTERNET = 'INTERNET'
    READ_EXTERNAL_STORAGE = 'READ_EXTERNAL_STORAGE'
    VIBRATE = 'VIBRATE'
    WRITE_EXTERNAL_STORAGE = 'WRITE_EXTERNAL_STORAGE'

# Add permission for target android
def add_permission_target_android(permission_name_enum):
    wrd = bpy.data.worlds['Arm']
    check = False
    for item in wrd.arm_exporter_android_permission_list:
        if (item.arm_android_permissions.upper() == str(permission_name_enum.value).upper()):
            check = True
            break
    if not check:
        wrd.arm_exporter_android_permission_list.add()
        wrd.arm_exporter_android_permission_list[len(wrd.arm_exporter_android_permission_list) - 1].arm_android_permissions = str(permission_name_enum.value).upper()

def get_project_android_build_apk():
    wrd = bpy.data.worlds['Arm']
    return wrd.arm_project_android_build_apk

def get_android_sdk_root_path():
    if os.getenv('ANDROID_SDK_ROOT') == None:
        addon_prefs = get_arm_preferences()
        return '' if not hasattr(addon_prefs, 'android_sdk_root_path') else addon_prefs.android_sdk_root_path
    else:
        return os.getenv('ANDROID_SDK_ROOT')

def get_android_apk_copy_path():
    addon_prefs = get_arm_preferences()
    return '' if not hasattr(addon_prefs, 'android_apk_copy_path') else addon_prefs.android_apk_copy_path

def get_android_apk_copy_open_directory():
    addon_prefs = get_arm_preferences()
    return False if not hasattr(addon_prefs, 'android_apk_copy_open_directory') else addon_prefs.android_apk_copy_open_directory

def get_android_emulators_list():
    err = ''
    items = []
    path_file = get_android_emulator_file()
    if len(path_file) > 0:
        cmd = path_file + " -list-avds"
        if get_os_is_windows():
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        else:
            process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline().decode("utf-8")
            if len(output.strip()) == 0 and process.poll() is not None:
                break
            if output:
                items.append(output.strip())
    else:
        err = 'File "'+ path_file +'" not found.'
    return items, err

def get_android_emulator_path():
    return os.path.join(get_android_sdk_root_path(), "emulator")

def get_android_emulator_file():
    path_file = ''
    if get_os_is_windows():
        path_file = os.path.join(get_android_emulator_path(), "emulator.exe")
    else:
        path_file = os.path.join(get_android_emulator_path(), "emulator")
    # File Exists
    return '' if not os.path.isfile(path_file) else path_file

def get_android_emulator_name():
    wrd = bpy.data.worlds['Arm']
    return '' if not len(wrd.arm_project_android_list_avd.strip()) > 0 else wrd.arm_project_android_list_avd.strip()

def get_android_open_build_apk_directory():
    addon_prefs = get_arm_preferences()
    return False if not hasattr(addon_prefs, 'android_open_build_apk_directory') else addon_prefs.android_open_build_apk_directory

def get_html5_copy_path():
    addon_prefs = get_arm_preferences()
    return '' if not hasattr(addon_prefs, 'html5_copy_path') else addon_prefs.html5_copy_path

def get_link_web_server():
    addon_prefs = get_arm_preferences()
    return '' if not hasattr(addon_prefs, 'link_web_server') else addon_prefs.link_web_server


def get_file_arm_version_tuple() -> tuple[int]:
    wrd = bpy.data.worlds['Arm']
    return tuple(map(int, wrd.arm_version.split('.')))

def type_name_to_type(name: str) -> bpy.types.bpy_struct:
    """Return the Blender type given by its name, if registered."""
    return bpy.types.bpy_struct.bl_rna_get_subclass_py(name)

def change_version_project(version: str) -> str:
    ver = version.strip().replace(' ', '').split('.')
    v_i = int(ver[len(ver) - 1]) + 1
    ver[len(ver) - 1] = str(v_i)
    version = ''
    for i in ver:
        if len(version) > 0:
            version += '.'
        version += i
    return version


def cpu_count(*, physical_only=False) -> Optional[int]:
    """Returns the number of logical (default) or physical CPUs.
    The result can be `None` if `os.cpu_count()` was not able to get the
    correct count of logical CPUs.
    """
    if not physical_only:
        return os.cpu_count()

    err_reason = ''
    command = []

    _os = get_os()
    try:
        if _os == 'win':
            sysroot = os.environ.get("SYSTEMROOT", default="C:\\WINDOWS")
            command = [f'{sysroot}\\System32\\wbem\\wmic.exe', 'cpu', 'get', 'NumberOfCores']
            result = subprocess.check_output(command)
            result = result.decode('utf-8').splitlines()
            result = int(result[2])
            if result > 0:
                return result

        elif _os == 'linux':
            command = ["grep -P '^core id' /proc/cpuinfo | sort -u | wc -l"]
            result = subprocess.check_output(command[0], shell=True)
            result = result.decode('utf-8').splitlines()
            result = int(result[0])
            if result > 0:
                return result

        # macOS
        else:
            command = ['sysctl', '-n', 'hw.physicalcpu']
            return int(subprocess.check_output(command))

    except subprocess.CalledProcessError as e:
        err_reason = f'Reason: command {command} exited with code {e.returncode}.'
    except FileNotFoundError as e:
        err_reason = f'Reason: couldn\'t open file from command {command} ({e.errno=}).'

    # Last resort even though it can be wrong
    log.warn("Could not retrieve count of physical CPUs, using logical CPU count instead.\n\t" + err_reason)
    return os.cpu_count()


def register(local_sdk=False):
    global use_local_sdk
    use_local_sdk = local_sdk

def unregister():
    pass
