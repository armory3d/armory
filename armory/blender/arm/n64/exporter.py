import os
import subprocess
import math
import shutil
import json
import glob
import bpy

import arm
import arm.utils
import arm.log as log

from arm.n64 import codegen
from arm.n64 import utils as n64_utils

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    log = arm.reload_module(log)
    codegen = arm.reload_module(codegen)
    n64_utils = arm.reload_module(n64_utils)
else:
    arm.enable_reload(__name__)


class KouiThemeParser:
    """Parser for Koui .ksn theme files with inheritance resolution."""

    def __init__(self):
        self.globals = {}           # @globals variables
        self.selectors = {}         # Parsed selector styles: {selector_name: {properties}}
        self.resolved = {}          # Fully resolved styles (inheritance flattened)

    def parse_file(self, path: str):
        """Parse a .ksn theme file and merge into current state."""
        if not os.path.exists(path):
            return

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        current_section = None      # '@rules', '@globals', or selector name
        current_selector = None
        current_parent = None
        indent_stack = []           # Track indentation for nested properties
        property_path = []          # Current property path (e.g., ['color', 'text'])

        for line in content.split('\n'):
            # Skip comments and empty lines
            stripped = line.split('//')[0].rstrip()
            if not stripped:
                continue

            # Detect indentation level
            indent = len(line) - len(line.lstrip('\t'))

            # Section headers
            if stripped == '@rules:':
                current_section = 'rules'
                current_selector = None
                continue
            elif stripped == '@globals:':
                current_section = 'globals'
                current_selector = None
                continue
            elif stripped.endswith(':') and not stripped.startswith('\t'):
                # Selector line: "selector_name:" or "selector > parent:"
                current_section = 'selector'
                selector_part = stripped[:-1].strip()

                if ' > ' in selector_part:
                    current_selector, current_parent = selector_part.split(' > ')
                    current_selector = current_selector.strip()
                    current_parent = current_parent.strip()
                else:
                    current_selector = selector_part
                    current_parent = None

                if current_selector not in self.selectors:
                    self.selectors[current_selector] = {'_parent': current_parent}
                elif current_parent:
                    self.selectors[current_selector]['_parent'] = current_parent

                indent_stack = []
                property_path = []
                continue

            # Skip @rules section (schema definition)
            if current_section == 'rules':
                continue

            # Parse @globals
            if current_section == 'globals':
                if ': ' in stripped:
                    key, value = stripped.split(': ', 1)
                    self.globals[key.strip()] = value.strip()
                continue

            # Parse selector properties
            if current_section == 'selector' and current_selector:
                # Adjust property path based on indentation
                while indent_stack and indent <= indent_stack[-1]:
                    indent_stack.pop()
                    if property_path:
                        property_path.pop()

                if ': ' in stripped:
                    # Property assignment: "key: value"
                    key, value = stripped.split(': ', 1)
                    key = key.strip()
                    value = value.strip()

                    # Resolve variable references ($@globals.VAR or $_selector.path)
                    if value.startswith('$@globals.'):
                        var_name = value[10:]
                        value = self.globals.get(var_name, value)
                    elif value.startswith('$_'):
                        # Reference to another selector's property - skip for now
                        pass

                    # Build full property path
                    full_path = property_path + [key]
                    self._set_nested_property(self.selectors[current_selector], full_path, value)

                elif stripped.endswith(':'):
                    # Start of nested property group
                    key = stripped[:-1].strip()
                    if key.startswith('?'):
                        key = key[1:]  # Remove optional marker
                    indent_stack.append(indent)
                    property_path.append(key)

    def _set_nested_property(self, obj: dict, path: list, value):
        """Set a nested property in a dict using a path list."""
        for key in path[:-1]:
            if key not in obj:
                obj[key] = {}
            obj = obj[key]
        obj[path[-1]] = value

    def _get_nested_property(self, obj: dict, path: list, default=None):
        """Get a nested property from a dict using a path list."""
        for key in path:
            if not isinstance(obj, dict) or key not in obj:
                return default
            obj = obj[key]
        return obj

    def resolve_all(self):
        """Resolve all selectors with inheritance, flattening parent styles."""
        self.resolved = {}
        for selector in self.selectors:
            self.resolved[selector] = self._resolve_selector(selector)

    def _resolve_selector(self, selector: str, visited: set = None) -> dict:
        """Recursively resolve a selector's full style including parent inheritance."""
        if visited is None:
            visited = set()

        if selector in visited:
            return {}  # Circular reference protection
        visited.add(selector)

        if selector not in self.selectors:
            return {}

        raw = self.selectors[selector]
        parent_name = raw.get('_parent')

        # Start with parent's resolved style
        if parent_name:
            result = self._resolve_selector(parent_name, visited).copy()
            result = self._deep_merge(result, {})  # Deep copy
        else:
            result = {}

        # Merge current selector's properties (override parent)
        for key, value in raw.items():
            if key == '_parent':
                continue
            if isinstance(value, dict):
                if key not in result:
                    result[key] = {}
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dicts, with override taking precedence."""
        result = base.copy() if isinstance(base, dict) else {}
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get_style(self, selector: str) -> dict:
        """Get the fully resolved style for a selector."""
        return self.resolved.get(selector, {})

    def get_font_size(self, selector: str, default: int = 15) -> int:
        """Get font.size for a selector."""
        style = self.get_style(selector)
        try:
            return int(self._get_nested_property(style, ['font', 'size'], default))
        except (ValueError, TypeError):
            return default

    def get_text_color(self, selector: str, default: str = '#dddddd') -> str:
        """Get color.text for a selector as hex string."""
        style = self.get_style(selector)
        color = self._get_nested_property(style, ['color', 'text'], default)
        return color if color else default

    @staticmethod
    def parse_hex_color(hex_color: str) -> tuple:
        """Parse Koui hex color (#RRGGBB or #RRGGBBAA) to (r, g, b, a) tuple (0-255)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = 255
        elif len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
        else:
            return (221, 221, 221, 255)  # Default gray
        return (r, g, b, a)


class N64Exporter:
    """N64 Exporter - Exports Armory scenes to N64 C code."""

    # Font size conversion factor: Kha pixel height -> mkfont point size
    # Kha uses stbtt_ScaleForPixelHeight (height = ascent - descent)
    # mkfont/FreeType uses FT_SIZE_REQUEST_TYPE_NOMINAL (em-based sizing)
    # For most fonts, (ascent - descent) ≈ 1.1-1.3 × em-height
    # This factor converts Kha's pixel sizes to mkfont's point sizes
    # Value of 0.82 means: mkfont_size = kha_size * 0.82
    FONT_SIZE_SCALE = 0.82

    def __init__(self):
        self.scene_data = {}
        self.exported_meshes = {}
        self.exported_fonts = {}    # Track exported fonts: {(font_name, size): font_id}
        self.font_sizes = set()     # Unique font sizes needed from theme
        self.trait_info = {}        # Trait metadata from macro JSON
        self.has_physics = False    # Track if any rigid bodies are exported
        self.has_ui = False         # Track if any UI elements are used
        self.has_audio = False      # Track if any audio assets are used
        self.ui_canvas_data = {}    # Parsed Koui canvas JSON: {canvas_name: {labels: [...], ...}}
        self.theme_parser = None    # Koui theme parser instance
        self.color_style_map = {}   # Map of (r,g,b,a) -> style_id for font styles
        self.font_id_map = {}       # Map of size -> font_id for label assignment
        self.autoload_info = {}     # Autoload metadata from codegen


    @classmethod
    def export_project(cls):
        exporter = cls()
        exporter.export()


    @classmethod
    def publish_project(cls):
        exporter = cls()
        exporter.publish()


    @classmethod
    def play_project(cls):
        exporter = cls()
        exporter.play()


    def convert_materials_to_f3d(self):
        """Convert materials to F3D format (requires Fast64 addon)."""
        try:
            # Check if F3D addon is available
            if not hasattr(bpy.ops.scene, 'f3d_convert_to_bsdf'):
                log.warn('Fast64 addon not found - skipping F3D material conversion')
                return False

            bpy.ops.scene.f3d_convert_to_bsdf(
                direction='F3D',
                converter_type='All',
                backup=False,
                put_alpha_into_color=False,
                use_recommended=True,
                lights_for_colors=False,
                default_to_fog=False,
                set_rendermode_without_fog=False
            )
            return True
        except Exception as e:
            log.warn(f'F3D material conversion failed: {e}')
            return False


    def make_directories(self):
        build_dir = arm.utils.build_dir()
        os.makedirs(f'{build_dir}/n64', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/assets', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/data', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/events', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/iron', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/iron/object', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/iron/system', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/oimo', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/scenes', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/system', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/ui', exist_ok=True)


    def export_meshes(self):
        build_dir = arm.utils.build_dir()
        assets_dir = f'{build_dir}/n64/assets'

        self.exported_meshes = {}

        for scene in bpy.data.scenes:
            if scene.library:
                continue

            n64_utils.deselect_from_all_viewlayers()
            main_scene = bpy.context.scene
            main_view_layer = bpy.context.view_layer

            for obj in scene.objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.update()

                if obj.type != 'MESH':
                    continue

                mesh = obj.data
                if mesh in self.exported_meshes:
                    continue

                mesh_name = arm.utils.safesrc(mesh.name)
                model_output_path = os.path.join(assets_dir, f'{mesh_name}.gltf')

                orig_loc = obj.location.copy()
                orig_rot = obj.rotation_euler.copy()
                orig_scale = obj.scale.copy()

                obj.location = (0.0, 0.0, 0.0)
                obj.rotation_euler = (0.0, 0.0, 0.0)
                obj.scale = (1.0, 1.0, 1.0)

                bpy.context.window.scene = scene
                bpy.context.window.view_layer = scene.view_layers[0]

                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) # HACK: force delay to properly export meshes from other scenes
                bpy.context.view_layer.update()

                obj.select_set(True)

                bpy.ops.export_scene.gltf(
                    filepath=model_output_path,
                    export_format='GLTF_SEPARATE',
                    export_extras=True,
                    use_selection=True,
                    export_yup=True
                )

                obj.location = orig_loc
                obj.rotation_euler = orig_rot
                obj.scale = orig_scale

                bpy.context.view_layer.update()
                self.exported_meshes[mesh] = mesh_name

            bpy.context.window.scene = main_scene
            bpy.context.window.view_layer = main_view_layer


    def _extract_traits(self, obj) -> list:
        """Extract trait list from a Blender object/scene with property values."""
        traits = []
        if hasattr(obj, 'arm_traitlist'):
            for trait in obj.arm_traitlist:
                if not trait.enabled_prop:
                    continue

                # Get class name based on trait type
                if trait.type_prop == 'Logic Nodes':
                    if trait.node_tree_prop is not None:
                        # Logic nodes: class name is the node tree name
                        class_name = trait.node_tree_prop.name
                    else:
                        continue  # No node tree assigned
                elif trait.type_prop == 'Haxe Script' or trait.type_prop == 'Bundled Script':
                    if trait.class_name_prop:
                        class_name = trait.class_name_prop
                    else:
                        continue  # No class assigned
                elif trait.type_prop == 'UI Canvas':
                    # UI Canvas is handled separately in build_scene_data() - not a runtime trait
                    continue
                else:
                    continue  # Unsupported trait type for N64

                prop_data = n64_utils.extract_blender_trait_props(trait)
                traits.append({
                    "class_name": class_name,
                    "type": trait.type_prop,
                    "props": prop_data['values'],
                    "type_overrides": prop_data['types']
                })
        return traits


    def build_scene_data(self, scene):
        scene_name = arm.utils.safesrc(scene.name).lower()
        scene_traits = self._extract_traits(scene)

        # Extract canvas name directly from Blender trait list (UI Canvas is not a runtime trait)
        canvas_name = None
        if hasattr(scene, 'arm_traitlist'):
            for trait in scene.arm_traitlist:
                if trait.enabled_prop and trait.type_prop == 'UI Canvas':
                    canvas_name = getattr(trait, 'canvas_name_prop', '')
                    if canvas_name:
                        break

        # Get gravity from scene (Blender's scene.gravity is the actual gravity vector)
        gravity = [0.0, -9.81, 0.0]  # Default gravity
        if hasattr(scene, 'gravity'):
            gravity = [scene.gravity[0], scene.gravity[1], scene.gravity[2]]

        # Get physics debug draw mode from Armory settings
        debug_draw_mode = n64_utils.get_physics_debug_mode()

        # Safe access to Fast64 ambient color with fallback
        try:
            ambient_color = list(scene.fast64.renderSettings.ambientColor)
        except (AttributeError, KeyError):
            ambient_color = [0.2, 0.2, 0.2]  # Default ambient

        self.scene_data[scene_name] = {
            "canvas": canvas_name,  # UI canvas for this scene (or None)
            "world": {
                "clear_color": n64_utils.get_clear_color(scene),
                "ambient_color": ambient_color,
                "gravity": gravity,
                "physics_debug_mode": debug_draw_mode
            },
            "cameras": [],
            "lights": [],
            "objects": [],
            "traits": scene_traits
        }

        for obj in scene.objects:
            if obj.type == 'CAMERA':
                # Raw Blender coordinates - codegen.py will transform later
                cam_dir = obj.rotation_euler.to_matrix().col[2]
                cam_target = [
                    obj.location[0] - cam_dir[0],
                    obj.location[1] - cam_dir[1],
                    obj.location[2] - cam_dir[2]
                ]
                sensor = max(obj.data.sensor_width, obj.data.sensor_height)
                cam_fov = math.degrees(2 * math.atan((sensor * 0.5) / obj.data.lens))

                self.scene_data[scene_name]["cameras"].append({
                    "name": arm.utils.safesrc(obj.name),
                    "pos": list(obj.matrix_world.to_translation()),  # World position (flattened)
                    "target": cam_target,
                    "fov": cam_fov,
                    "near": obj.data.clip_start,
                    "far": obj.data.clip_end,
                    "traits": self._extract_traits(obj)
                })
            elif obj.type == 'LIGHT':  # TODO: support multiple light types [Point and Sun]
                # Raw Blender direction - codegen.py will transform and normalize
                light_dir = obj.rotation_euler.to_matrix().col[2]

                self.scene_data[scene_name]["lights"].append({
                    "name": arm.utils.safesrc(obj.name),
                    "pos": list(obj.matrix_world.to_translation()),
                    "color": list(obj.data.color),
                    "dir": list(light_dir),
                    "traits": self._extract_traits(obj)
                })
            elif obj.type == 'MESH':
                mesh = obj.data
                if mesh not in self.exported_meshes:
                    log.warn(f'Object "{obj.name}": mesh not exported, skipping')
                    continue
                mesh_name = self.exported_meshes[mesh]

                # Raw Blender coordinates - codegen.py will transform later
                # Export rotation as quaternion (XYZW order for T3D)
                quat = obj.matrix_world.to_quaternion()

                # Compute bounding sphere from mesh's bounding box (local space)
                # bound_box is 8 corners of the AABB in local coordinates
                bb = obj.bound_box
                min_corner = [min(v[i] for v in bb) for i in range(3)]
                max_corner = [max(v[i] for v in bb) for i in range(3)]
                bounds_center = [
                    (min_corner[0] + max_corner[0]) * 0.5,
                    (min_corner[1] + max_corner[1]) * 0.5,
                    (min_corner[2] + max_corner[2]) * 0.5
                ]
                # Radius is distance from center to corner
                half_extents = [
                    (max_corner[0] - min_corner[0]) * 0.5,
                    (max_corner[1] - min_corner[1]) * 0.5,
                    (max_corner[2] - min_corner[2]) * 0.5
                ]
                bounds_radius = math.sqrt(
                    half_extents[0]**2 + half_extents[1]**2 + half_extents[2]**2
                )

                # Extract rigid body data (N64 supports box, sphere, and capsule)
                rigid_body_data = None
                wrd = bpy.data.worlds['Arm']
                if obj.rigid_body is not None and wrd.arm_physics != 'Disabled':
                    rb = obj.rigid_body
                    shape = rb.collision_shape

                    # N64 supports BOX, SPHERE, CAPSULE, and MESH (static only)
                    rb_mesh_data = None
                    if shape == 'SPHERE':
                        rb_shape = "sphere"
                        # Calculate sphere radius from bounding box (max half-extent * max scale)
                        max_scale = max(obj.scale)
                        rb_radius = max(half_extents) * max_scale
                        rb_half_extents = None
                        rb_half_height = None
                    elif shape == 'CAPSULE':
                        rb_shape = "capsule"
                        # Capsule: radius from X/Z, half-height from Y (in Blender coords)
                        # Blender capsule is aligned along Z, we convert to Y-up for N64
                        rb_radius = max(half_extents[0], half_extents[1]) * max(obj.scale[0], obj.scale[1])
                        # Half-height is the cylinder part (total height - 2*radius) / 2
                        total_height = half_extents[2] * 2.0 * obj.scale[2]
                        rb_half_height = max(0.0, (total_height - 2.0 * rb_radius) / 2.0)
                        rb_half_extents = None
                    elif shape == 'MESH' and rb.type == 'PASSIVE':
                        # Mesh collision only works for static (passive) bodies
                        rb_shape = "mesh"
                        rb_radius = None
                        rb_half_height = None
                        rb_half_extents = None
                        # Extract mesh collision data
                        rb_mesh_data = n64_utils.extract_collision_mesh(obj)
                        if rb_mesh_data is None:
                            log.warn(f'Object "{obj.name}": failed to extract mesh collision data, using BOX')
                            rb_shape = "box"
                            rb_half_extents = [
                                half_extents[0] * obj.scale[0],
                                half_extents[2] * obj.scale[2],
                                half_extents[1] * obj.scale[1]
                            ]
                    else:
                        # Everything else becomes a box
                        rb_shape = "box"
                        rb_radius = None
                        rb_half_height = None
                        # Half extents scaled by object scale
                        # Convert from Blender (Z-up) to N64 (Y-up): swap Y and Z
                        rb_half_extents = [
                            half_extents[0] * obj.scale[0],
                            half_extents[2] * obj.scale[2],  # Blender Z -> N64 Y
                            half_extents[1] * obj.scale[1]   # Blender Y -> N64 Z
                        ]
                        if shape not in ('BOX', 'SPHERE', 'CAPSULE'):
                            if shape == 'MESH' and rb.type != 'PASSIVE':
                                log.warn(f'Object "{obj.name}": MESH collision shape only supported for static (passive) bodies, using BOX')
                            else:
                                log.warn(f'Object "{obj.name}": collision shape "{shape}" not supported on N64, using BOX')

                    # Mass (0 = static)
                    is_static = rb.type == 'PASSIVE'
                    rb_mass = 0.0 if is_static else rb.mass

                    # Collision groups/masks (convert from Blender's 20-bit to simple int)
                    col_group = 0
                    for i, b in enumerate(rb.collision_collections):
                        if b:
                            col_group |= (1 << i)

                    col_mask = 0
                    if hasattr(obj, 'arm_rb_collision_filter_mask'):
                        for i, b in enumerate(obj.arm_rb_collision_filter_mask):
                            if b:
                                col_mask |= (1 << i)
                    else:
                        col_mask = 1  # Default mask

                    rigid_body_data = {
                        "shape": rb_shape,
                        "mass": rb_mass,
                        "friction": rb.friction,
                        "restitution": rb.restitution,
                        "linear_damping": rb.linear_damping,
                        "angular_damping": rb.angular_damping,
                        "collision_group": col_group,
                        "collision_mask": col_mask,
                        "is_trigger": getattr(obj, 'arm_rb_trigger', False),
                        "rb_type": rb.type,  # 'PASSIVE' or 'ACTIVE'
                        "is_animated": rb.kinematic,  # Animated checkbox
                        "is_dynamic": rb.enabled,  # Dynamic checkbox
                        "use_deactivation": rb.use_deactivation
                    }

                    if rb_shape == "sphere":
                        rigid_body_data["radius"] = rb_radius
                    elif rb_shape == "capsule":
                        rigid_body_data["radius"] = rb_radius
                        rigid_body_data["half_height"] = rb_half_height
                    elif rb_shape == "mesh":
                        rigid_body_data["mesh_data"] = rb_mesh_data
                    else:
                        rigid_body_data["half_extents"] = rb_half_extents

                    self.has_physics = True

                obj_data = {
                    "name": arm.utils.safesrc(obj.name),
                    "mesh": f'MODEL_{mesh_name.upper()}',
                    "pos": list(obj.matrix_world.to_translation()),
                    "rot": [quat.x, quat.y, quat.z, quat.w],
                    "scale": list(obj.scale),
                    "visible": not obj.hide_render,
                    "bounds_center": bounds_center,
                    "bounds_radius": bounds_radius,
                    "traits": self._extract_traits(obj),
                    "is_static": True  # Computed after trait_info is loaded
                }

                if rigid_body_data is not None:
                    obj_data["rigid_body"] = rigid_body_data

                self.scene_data[scene_name]["objects"].append(obj_data)


    def write_makefile(self):
        wrd = bpy.data.worlds['Arm']
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'Makefile.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'Makefile')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        scene_lines = []
        for scene in bpy.data.scenes:
            if scene.library:
                continue
            scene_name = arm.utils.safesrc(scene.name).lower()
            scene_lines.append(f'    src/scenes/{scene_name}.c')
        scene_files = '\\\n'.join(scene_lines)

        # Physics source files (only if physics is used)
        # Note: oimo is header-only, only physics.c and geometry.c need compilation
        # physics_debug.c is only included if debug drawing is enabled
        if self.has_physics:
            physics_debug_mode = n64_utils.get_physics_debug_mode()
            if physics_debug_mode > 0:
                physics_sources = '''src +=\\
    src/events/physics_events.c \\
    src/oimo/physics.c \\
    src/oimo/debug/physics_debug.c \\
    src/oimo/collision/geometry/geometry.c'''
            else:
                physics_sources = '''src +=\\
    src/oimo/physics.c \\
    src/events/physics_events.c \\
    src/oimo/collision/geometry/geometry.c'''
        else:
            physics_sources = '# No physics'

        # UI source files (only if UI elements are used)
        if self.has_ui:
            ui_sources = '''src +=\\
    src/ui/fonts.c \\
    src/ui/canvas.c'''
        else:
            ui_sources = '# No UI'

        # Autoload source files (only if autoloads exist)
        if self.autoload_info.get('has_autoloads', False):
            autoload_lines = ['src +=\\']
            for c_name in self.autoload_info.get('autoloads', []):
                autoload_lines.append(f'    src/autoloads/{c_name}.c \\')
            # Remove trailing backslash from last line
            autoload_lines[-1] = autoload_lines[-1].rstrip(' \\')
            autoload_sources = '\n'.join(autoload_lines)
        else:
            autoload_sources = '# No autoloads'

        # Generate font targets and rules for each size variant
        font_targets, font_rules = self._generate_font_makefile_entries()

        output = tmpl_content.format(
            tiny3d_path=os.path.join(arm.utils.get_sdk_path(), 'lib', 'tiny3d').replace('\\', '/'),
            game_title=arm.utils.safestr(wrd.arm_project_name),
            scene_files=scene_files,
            physics_sources=physics_sources,
            canvas_sources=ui_sources,
            autoload_sources=autoload_sources,
            font_targets=font_targets,
            font_rules=font_rules
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def _generate_font_makefile_entries(self):
        """Generate Makefile entries for font conversion at different sizes.

        Since mkfont names outputs based on input filename, we copy the TTF file
        to size-specific names (e.g., Montserrat_15.ttf -> Montserrat_15.font64).

        The font sizes are scaled from Kha's pixel height to mkfont's point size
        using FONT_SIZE_SCALE to account for differences in how each library
        interprets font sizes.

        Returns:
            tuple: (font_targets_str, font_rules_str)
        """
        if not self.exported_fonts:
            return 'font_conv =', '# No fonts'

        targets = []
        rules = []

        for font_key, font_info in self.exported_fonts.items():
            font_name = font_info['name']
            kha_size = font_info['size']  # Original Kha pixel size
            # Scale font size for mkfont (Kha pixel height -> mkfont point size)
            mkfont_size = max(8, int(kha_size * self.FONT_SIZE_SCALE))
            # Target: filesystem/FontName_Size.font64
            target = f'filesystem/{font_key}.font64'
            targets.append(target)

            # Rule: mkfont uses input filename for output, so we use the size-specific TTF copy
            # The size-specific TTF was created during write_fonts()
            rule = f'''{target}: assets/{font_key}.ttf
	@mkdir -p $(dir $@)
	@echo "    [FONT] $@ (kha size {kha_size} -> mkfont size {mkfont_size})"
	$(N64_MKFONT) $(MKFONT_FLAGS) --size {mkfont_size} -o filesystem "$<"'''
            rules.append(rule)

        font_targets = 'font_conv = ' + ' \\\n             '.join(targets)
        font_rules = '\n\n'.join(rules)

        return font_targets, font_rules


    def write_types(self):
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'types.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'types.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        wrd = bpy.data.worlds.get('Arm')
        debug_hud_define = '\n#define ARM_DEBUG_HUD' if wrd and wrd.arm_debug_console else ''
        output = tmpl_content.format(debug_hud_define=debug_hud_define)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def write_traits(self):
        """Generate traits.h and traits.c files."""
        # Collect all type overrides from all trait instances across all scenes
        type_overrides = self._collect_type_overrides()

        # Get template data from codegen
        template_data, features = codegen.prepare_traits_template_data(type_overrides)

        # Update feature flags based on trait analysis
        if features:
            if features.get('has_ui'):
                self.has_ui = True
            if features.get('has_physics'):
                self.has_physics = True

        # Write files
        if template_data is None:
            # No traits - create empty stubs
            self.write_traits_h_empty()
            self.write_traits_c_empty()
        else:
            self.write_traits_h(template_data)
            self.write_traits_c(template_data)

    def write_traits_h(self, template_data: dict):
        """Generate traits.h from template."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'traits.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            template = f.read()

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(template.format(**template_data))

    def write_traits_c(self, template_data: dict):
        """Generate traits.c from template."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'traits.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            template = f.read()

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(template.format(**template_data))

    def write_traits_h_empty(self):
        """Generate empty traits.h stub."""
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.h')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("// Auto-generated empty traits header\n#ifndef _TRAITS_H_\n#define _TRAITS_H_\n#endif\n")

    def write_traits_c_empty(self):
        """Generate empty traits.c stub."""
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.c')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("// Auto-generated empty traits implementation\n#include \"traits.h\"\n")

    def _collect_type_overrides(self) -> dict:
        """Collect all type overrides from trait instances across all scenes.

        Returns:
            dict mapping trait_class -> member_name -> c_type
        """
        overrides = {}

        def collect_from_traits(traits):
            for trait in traits:
                class_name = trait.get("class_name", "")
                trait_overrides = trait.get("type_overrides", {})
                if trait_overrides:
                    if class_name not in overrides:
                        overrides[class_name] = {}
                    overrides[class_name].update(trait_overrides)

        for scene_data in self.scene_data.values():
            # Scene-level traits
            collect_from_traits(scene_data.get("traits", []))
            # Camera traits
            for cam in scene_data.get("cameras", []):
                collect_from_traits(cam.get("traits", []))
            # Light traits
            for light in scene_data.get("lights", []):
                collect_from_traits(light.get("traits", []))
            # Object traits
            for obj in scene_data.get("objects", []):
                collect_from_traits(obj.get("traits", []))

        return overrides

    def write_autoloads(self):
        """Generate autoload C files from IR JSON.

        Autoloads are singleton classes marked with @:n64Autoload.
        They become globally accessible C modules.
        """
        # Get template data from codegen
        autoload_data, master_data = codegen.prepare_autoload_template_data()

        if not autoload_data:
            self.autoload_info = {'autoloads': [], 'has_autoloads': False}
            return

        autoloads_dir = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads')
        os.makedirs(autoloads_dir, exist_ok=True)

        autoload_names = []
        for c_name, tmpl_data in autoload_data:
            autoload_names.append(c_name)
            self.write_autoload_h(c_name, tmpl_data)
            self.write_autoload_c(c_name, tmpl_data)

        # Write master autoloads.h
        self.write_autoloads_h(master_data)

        self.autoload_info = {'autoloads': autoload_names, 'has_autoloads': True}

    def write_autoload_h(self, c_name: str, template_data: dict):
        """Generate individual autoload .h file."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'autoloads', 'autoload.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads', f'{c_name}.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            template = f.read()

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(template.format(**template_data))

    def write_autoload_c(self, c_name: str, template_data: dict):
        """Generate individual autoload .c file."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'autoloads', 'autoload.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads', f'{c_name}.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            template = f.read()

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(template.format(**template_data))

    def write_autoloads_h(self, template_data: dict):
        """Generate master autoloads.h that includes all autoloads."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'autoloads', 'autoloads.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads', 'autoloads.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            template = f.read()

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(template.format(**template_data))

    def write_engine(self):
        n64_utils.copy_src('engine.c', 'src')

        # Generate engine.h from template with physics flag
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'engine.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'engine.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        # Calculate physics debug mode from Blender settings
        physics_debug_mode = n64_utils.get_physics_debug_mode()

        output = tmpl_content.format(
            enable_physics=1 if self.has_physics else 0,
            enable_physics_debug=1 if physics_debug_mode > 0 else 0,
            enable_ui=1 if self.has_ui else 0,
            enable_audio=1 if self.has_audio else 0
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def detect_ui_canvas(self):
        """Detect and parse Koui canvas JSON files referenced by scenes.

        Only parses canvases that are actually attached to scenes via UI Canvas trait.
        Sets has_ui = True if any canvas with labels is found.
        Stores parsed data in self.ui_canvas_data for code generation.
        Also parses Koui theme files to extract font size and text color per label.
        """
        bundled_dir = os.path.join(arm.utils.get_fp(), 'Bundled', 'koui_canvas')
        if not os.path.exists(bundled_dir):
            return

        # Collect canvas names referenced by scenes
        referenced_canvases = set()
        for scene_name, data in self.scene_data.items():
            canvas_name = data.get('canvas')
            if canvas_name:
                referenced_canvases.add(canvas_name)

        if not referenced_canvases:
            return  # No scenes use UI Canvas trait

        # Parse Koui theme files for style information
        self._parse_koui_themes()

        for canvas_name in referenced_canvases:
            json_path = os.path.join(bundled_dir, f'{canvas_name}.json')
            if not os.path.exists(json_path):
                log.warn(f'UI Canvas "{canvas_name}" not found at {json_path}')
                continue

            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    canvas_data = json.load(f)

                canvas_info = canvas_data.get('canvas', {})
                canvas_width = canvas_info.get('width')
                canvas_height = canvas_info.get('height')

                labels = []
                for scene in canvas_data.get('scenes', []):
                    for elem in scene.get('elements', []):
                        if elem.get('type') == 'Label':
                            props = elem.get('properties', {})
                            tid = elem.get('tID', '_label')

                            # Get font size and text color from theme
                            font_size = 15
                            text_color = (221, 221, 221, 255)  # Default #dddddd

                            if self.theme_parser:
                                font_size = self.theme_parser.get_font_size(tid, 15)
                                color_hex = self.theme_parser.get_text_color(tid, '#dddddd')
                                text_color = KouiThemeParser.parse_hex_color(color_hex)

                            # Track unique font sizes needed
                            self.font_sizes.add(font_size)

                            # Get or create style_id for this color
                            style_id = self._get_or_create_color_style(text_color)

                            label_data = {
                                'key': elem['key'],
                                'text': props.get('text', ''),
                                'pos_x': elem['posX'],
                                'pos_y': elem['posY'],
                                'width': elem['width'],
                                'height': elem['height'],
                                'anchor': elem['anchor'],
                                'visible': elem['visible'],
                                'align_h': props.get('alignmentHor', 0),
                                'align_v': props.get('alignmentVert', 0),
                                'tID': tid,
                                'font_size': font_size,
                                'text_color': text_color,
                                'style_id': style_id,
                            }
                            labels.append(label_data)

                if labels:
                    self.ui_canvas_data[canvas_name] = {
                        'width': canvas_width,
                        'height': canvas_height,
                        'labels': labels
                    }
                    self.has_ui = True
                    log.info(f'Found UI canvas: {canvas_name} with {len(labels)} label(s)')

            except Exception as e:
                log.warn(f'Failed to parse Koui canvas {json_path}: {e}')

    def _parse_koui_themes(self):
        """Parse Koui base theme and project override files."""
        self.theme_parser = KouiThemeParser()

        # Base theme from Koui Subprojects
        base_theme_path = os.path.join(arm.utils.get_fp(), 'Subprojects', 'Koui', 'Assets', 'theme.ksn')
        if os.path.exists(base_theme_path):
            self.theme_parser.parse_file(base_theme_path)
            log.info(f'Parsed base Koui theme: {base_theme_path}')

        # Project override from Assets/koui_canvas
        override_path = os.path.join(arm.utils.get_fp(), 'Assets', 'koui_canvas', 'ui_override.ksn')
        if os.path.exists(override_path):
            self.theme_parser.parse_file(override_path)
            log.info(f'Parsed Koui theme override: {override_path}')

        # Resolve all inheritance chains
        self.theme_parser.resolve_all()

    def _get_or_create_color_style(self, color: tuple) -> int:
        """Get or create a style_id for a given (r, g, b, a) color tuple."""
        if color in self.color_style_map:
            return self.color_style_map[color]

        # Style IDs start at 0 (which we'll use as default white if no colors defined)
        # but since we're assigning custom colors, start from 0
        style_id = len(self.color_style_map)
        self.color_style_map[color] = style_id
        return style_id

    def write_canvas(self):
        """Generate canvas.c and canvas.h from templates using parsed Koui canvas data."""
        if not self.ui_canvas_data:
            return

        self.write_canvas_h()
        self.write_canvas_c()

    def write_canvas_h(self):
        """Generate canvas.h from template with per-scene canvas support."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'canvas.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'canvas.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        # Get canvas dimensions from first canvas (all canvases should target same screen resolution)
        first_canvas = next(iter(self.ui_canvas_data.values()))
        canvas_width = first_canvas['width']
        canvas_height = first_canvas['height']

        # Build key-only label defines - indices are per-canvas (0, 1, 2...)
        # Traits use these key-only defines, which work for any canvas that has
        # a label with that key at that index. This allows traits to be reused
        # across scenes with different canvases (as long as label keys match).
        label_defines_lines = []
        total_label_count = 0
        seen_keys = {}  # Track key -> index for validation

        for canvas_name, canvas in self.ui_canvas_data.items():
            label_defines_lines.append(f'// Canvas: {canvas_name} ({canvas["width"]}x{canvas["height"]})')
            label_idx = 0
            for label in canvas['labels']:
                safe_key = arm.utils.safesrc(label['key']).upper()
                define_name = f'UI_LABEL_{safe_key}'

                if safe_key in seen_keys:
                    # Key already defined - check index matches for trait compatibility
                    if seen_keys[safe_key] != label_idx:
                        log.warn(f'Label key "{label["key"]}" has different indices across canvases '
                                 f'(index {seen_keys[safe_key]} vs {label_idx}). '
                                 f'Traits using this label may not work correctly across scenes.')
                else:
                    # First time seeing this key - emit define
                    label_defines_lines.append(f'#define {define_name} {label_idx}')
                    seen_keys[safe_key] = label_idx

                label_idx += 1
            total_label_count = max(total_label_count, label_idx)
            label_defines_lines.append('')  # Blank line between canvases

        output = tmpl_content.format(
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            label_defines='\n'.join(label_defines_lines),
            label_count=total_label_count
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def write_canvas_c(self):
        """Generate canvas.c from template with per-scene canvas init functions."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'canvas.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'canvas.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        # Build per-canvas label definitions (with style_id, font_id, and baseline_offset)
        canvas_label_defs = {}
        for canvas_name, canvas in self.ui_canvas_data.items():
            lines = []
            for label in canvas['labels']:
                text_escaped = label['text'].replace('\\', '\\\\').replace('"', '\\"')
                visible = 'true' if label['visible'] else 'false'
                style_id = label.get('style_id', 0)
                font_id = label.get('font_id', 0)
                baseline_offset = label.get('baseline_offset', 12)
                # Order: text, pos_x, pos_y, width, height, baseline_offset, anchor, style_id, font_id, visible
                lines.append(f'    {{ "{text_escaped}", {label["pos_x"]}, {label["pos_y"]}, {label["width"]}, {label["height"]}, {baseline_offset}, {label["anchor"]}, {style_id}, {font_id}, {visible} }},')
            canvas_label_defs[canvas_name] = {
                'defs': '\n'.join(lines),
                'count': len(canvas['labels'])
            }

        # Build per-canvas static arrays
        canvas_arrays = []
        for canvas_name, data in canvas_label_defs.items():
            safe_canvas = arm.utils.safesrc(canvas_name).lower()
            count = data['count']
            if count > 0:
                canvas_arrays.append(f'// Canvas: {canvas_name}')
                canvas_arrays.append(f'#define {safe_canvas.upper()}_LABEL_COUNT {count}')
                canvas_arrays.append(f'static const UILabelDef g_{safe_canvas}_label_defs[{safe_canvas.upper()}_LABEL_COUNT] = {{')
                canvas_arrays.append(data['defs'])
                canvas_arrays.append('};')
                canvas_arrays.append('')

        # Build switch cases for scene_id -> canvas loading
        scene_switch_cases = []
        for scene_name, data in self.scene_data.items():
            canvas_name = data.get('canvas')
            if canvas_name and canvas_name in self.ui_canvas_data:
                safe_scene = arm.utils.safesrc(scene_name).upper()
                safe_canvas = arm.utils.safesrc(canvas_name).lower()
                scene_switch_cases.append(f'        case SCENE_{safe_scene}:')
                scene_switch_cases.append(f'            load_labels(g_{safe_canvas}_label_defs, {safe_canvas.upper()}_LABEL_COUNT);')
                scene_switch_cases.append('            break;')

        # Generate font style registration code from color_style_map
        # Styles must be registered on ALL font size variants
        # Also ensures all font variants are loaded (via fonts_get())
        style_registration_lines = []
        if self.exported_fonts:
            for font_key, font_info in sorted(self.exported_fonts.items(), key=lambda x: x[1]['font_id']):
                font_id = font_info['font_id']
                # Skip font 0 - it's already loaded above
                if font_id == 0:
                    if self.color_style_map:
                        style_registration_lines.append(f'    // Font 0 styles (default font loaded above)')
                        for color, style_id in sorted(self.color_style_map.items(), key=lambda x: x[1]):
                            r, g, b, a = color
                            style_registration_lines.append(
                                f'    rdpq_font_style(font, {style_id}, &(rdpq_fontstyle_t){{ .color = RGBA32({r}, {g}, {b}, {a}) }});'
                            )
                    continue

                style_registration_lines.append(f'    // Font {font_id}: {font_key}')
                style_registration_lines.append(f'    {{')
                style_registration_lines.append(f'        rdpq_font_t *font_{font_id} = fonts_get({font_id});')
                if self.color_style_map:
                    style_registration_lines.append(f'        if (font_{font_id}) {{')
                    for color, style_id in sorted(self.color_style_map.items(), key=lambda x: x[1]):
                        r, g, b, a = color
                        style_registration_lines.append(
                            f'            rdpq_font_style(font_{font_id}, {style_id}, &(rdpq_fontstyle_t){{ .color = RGBA32({r}, {g}, {b}, {a}) }});'
                        )
                    style_registration_lines.append(f'        }}')
                style_registration_lines.append(f'    }}')

        if not style_registration_lines:
            style_registration_lines.append('    // No additional fonts or styles defined')

        # Total label count for g_labels array
        total_labels = sum(d['count'] for d in canvas_label_defs.values())

        output = tmpl_content.format(
            canvas_label_arrays='\n'.join(canvas_arrays),
            scene_init_switch_cases='\n'.join(scene_switch_cases),
            total_label_count=total_labels,
            font_style_registration='\n'.join(style_registration_lines) if style_registration_lines else '        // No custom styles defined'
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def write_fonts(self):
        """Copy font files and generate fonts.c/fonts.h if UI is used.

        Creates separate .font64 files for each unique font size needed from the theme.
        Since mkfont names outputs based on input filename, we create size-specific
        TTF copies (e.g., Montserrat_15.ttf, Montserrat_32.ttf).
        """
        if not self.has_ui:
            return

        n64_assets = os.path.join(arm.utils.build_dir(), 'n64', 'assets')
        os.makedirs(n64_assets, exist_ok=True)

        # Ensure we have at least the default size
        if not self.font_sizes:
            self.font_sizes.add(15)

        # Search order for fonts:
        # 1. Project's Assets folder (and subdirectories)
        # 2. Koui Subprojects Assets folder (default Montserrat fonts)
        font_search_paths = [
            os.path.join(arm.utils.get_fp(), 'Assets'),
            os.path.join(arm.utils.get_fp(), 'Subprojects', 'Koui', 'Assets'),
        ]

        base_font_name = None
        base_font_path = None

        for search_path in font_search_paths:
            if os.path.exists(search_path):
                fonts = glob.glob(os.path.join(search_path, '**', '*.ttf'), recursive=True)
                for font_path in fonts:
                    font_basename = os.path.splitext(os.path.basename(font_path))[0]
                    # Use first font found as the base font
                    if base_font_name is None:
                        base_font_name = font_basename
                        base_font_path = font_path
                        break  # Only need the first font
            if base_font_name:
                break

        if not base_font_name or not base_font_path:
            log.warn('No TTF fonts found for UI. Labels may not render correctly.')
            base_font_name = 'default'
            base_font_path = None

        # Create font entries for each unique size
        # Each size gets its own font64 file and font_id
        # We copy the TTF to size-specific names so mkfont creates correct output names
        font_id = 0
        for size in sorted(self.font_sizes):
            font_key = f'{base_font_name}_{size}'

            # Copy TTF with size-specific name for Makefile processing
            if base_font_path:
                dst = os.path.join(n64_assets, f'{font_key}.ttf')
                if not os.path.exists(dst):
                    shutil.copy(base_font_path, dst)
                    log.info(f'Copied font: {font_key}.ttf (size {size})')

            self.exported_fonts[font_key] = {
                'name': base_font_name,
                'size': size,
                'font_id': font_id
            }
            self.font_id_map[size] = font_id
            font_id += 1
            log.info(f'Font registered: {font_key} (size {size}, id {font_id - 1})')

        self.write_fonts_c()
        self.write_fonts_h()
        self._assign_font_ids_to_labels()

    def write_fonts_c(self):
        """Generate fonts.c from template.

        Creates entries for each font size variant (e.g., Montserrat_15.font64, Montserrat_32.font64).
        """
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'fonts.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'fonts.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        lines = []
        # Sort by font_id to ensure consistent ordering
        sorted_fonts = sorted(self.exported_fonts.items(), key=lambda x: x[1]['font_id'])
        for font_key, font_info in sorted_fonts:
            # font_key is already "FontName_Size"
            lines.append(f'    "rom:/{font_key}.font64"')
        font_paths = ',\n'.join(lines)

        output = tmpl_content.format(
            font_paths=font_paths,
            font_count=len(self.exported_fonts)
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def write_fonts_h(self):
        """Generate fonts.h from template.

        Creates enum entries for each font size variant (e.g., FONT_MONTSERRAT_15, FONT_MONTSERRAT_32).
        """
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'fonts.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'fonts.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        lines = []
        # Sort by font_id to ensure consistent ordering
        sorted_fonts = sorted(self.exported_fonts.items(), key=lambda x: x[1]['font_id'])
        for font_key, font_info in sorted_fonts:
            # Create a safe enum name (uppercase, replace special chars with _)
            enum_name = font_key.upper().replace('-', '_').replace(' ', '_')
            lines.append(f'    FONT_{enum_name} = {font_info["font_id"]},')
        font_enum_entries = '\n'.join(lines)

        output = tmpl_content.format(
            font_enum_entries=font_enum_entries,
            font_count=len(self.exported_fonts)
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def _assign_font_ids_to_labels(self):
        """Assign font_id and baseline_offset to each label based on its theme font size.

        The baseline_offset converts from Koui's top-based Y coordinate to
        libdragon's baseline-based Y coordinate. For most fonts:
        - Ascent ≈ 80% of pixel height (where text sits above baseline)
        - But since we scale font sizes for mkfont, we need to scale baseline too

        The actual rendered font height in mkfont is approximately:
        mkfont_size * 1.22 (due to em-to-pixel-height ratio)

        So baseline_offset ≈ (kha_size * FONT_SIZE_SCALE) * 1.22 * 0.8
                          ≈ kha_size * FONT_SIZE_SCALE * 0.98
                          ≈ kha_size * 0.8 (roughly the same as before, but now accurate)
        """
        for canvas_name, canvas in self.ui_canvas_data.items():
            for label in canvas.get('labels', []):
                # Get the label's font size (default 15 if not specified)
                kha_size = label.get('font_size', 15)
                # Look up the font_id for this size
                font_id = self.font_id_map.get(kha_size, 0)
                label['font_id'] = font_id
                # Calculate baseline offset based on scaled font metrics
                # mkfont_size = kha_size * FONT_SIZE_SCALE
                # rendered_height ≈ mkfont_size * 1.22 (em to pixel height)
                # ascent ≈ rendered_height * 0.80
                mkfont_size = max(8, int(kha_size * self.FONT_SIZE_SCALE))
                rendered_height = mkfont_size * 1.22  # Approximate em-to-pixel expansion
                baseline_offset = int(rendered_height * 0.80)
                label['baseline_offset'] = baseline_offset
                log.debug(f"Label '{label.get('key', 'unnamed')}': kha size {kha_size} -> mkfont {mkfont_size}, font_id {font_id}, baseline {baseline_offset}")

    def write_physics(self):
        """Copy physics engine files if physics is enabled."""
        if not self.has_physics:
            return

        # Copy oimo library first (header-only physics engine)
        # Must be done BEFORE rendering templates, since copy_dir clears the target
        n64_utils.copy_dir('oimo', 'src')

        # Render physics.c template (after copy_dir so it doesn't get deleted)
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'oimo', 'physics.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'oimo', 'physics.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        max_physics_bodies = n64_utils.get_config('max_physics_bodies', 32)
        output = tmpl_content.format(max_physics_bodies=max_physics_bodies)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

        # Render physics_events.h template
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'events', 'physics_events.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'events', 'physics_events.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        max_contact_subscribers = n64_utils.get_config('max_contact_subscribers', 4)
        max_contact_bodies = n64_utils.get_config('max_contact_bodies', 16)
        output = tmpl_content.format(
            max_contact_subscribers=max_contact_subscribers,
            max_contact_bodies=max_contact_bodies
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

        # Copy physics_events.c
        n64_utils.copy_src('physics_events.c', 'src/events')

        # Copy physics debug drawing files only if debug is enabled
        if n64_utils.get_physics_debug_mode() > 0:
            n64_utils.copy_src('physics_debug.h', 'src/oimo/debug')
            n64_utils.copy_src('physics_debug.c', 'src/oimo/debug')


    def write_main(self):
        wrd = bpy.data.worlds['Arm']
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'main.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'main.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        # Get physics fixed timestep from Armory settings (default 0.02 = 50Hz)
        fixed_timestep = getattr(wrd, 'arm_physics_fixed_step', 0.02)

        # Get physics debug mode
        physics_debug_mode = n64_utils.get_physics_debug_mode()

        # Autoload include and init
        has_autoloads = self.autoload_info.get('has_autoloads', False)
        autoloads_include = '#include "autoloads/autoloads.h"' if has_autoloads else ''
        autoloads_init = '    autoloads_init();\n' if has_autoloads else ''

        output = tmpl_content.format(
            initial_scene_id=f'SCENE_{arm.utils.safesrc(wrd.arm_exporterlist[wrd.arm_exporterlist_index].arm_project_scene.name).upper()}',
            fixed_timestep=fixed_timestep,
            physics_debug_mode=physics_debug_mode,
            autoloads_include=autoloads_include,
            autoloads_init=autoloads_init
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_models(self):
        self.write_models_c()
        self.write_models_h()


    def write_models_c(self):
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'models.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'models.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        lines = []
        for model_name in self.exported_meshes.values():
            lines.append(f'    "rom:/{model_name}.t3dm"')
        mesh_paths = ',\n'.join(lines)

        output = tmpl_content.format(
            mesh_paths=mesh_paths,
            model_count=len(self.exported_meshes)
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_models_h(self):
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'models.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'models.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        lines = []
        for i, model_name in enumerate(self.exported_meshes.values()):
            lines.append(f'    MODEL_{model_name.upper()} = {i},')
        model_enum_entries = '\n'.join(lines)

        output = tmpl_content.format(
            model_enum_entries=model_enum_entries,
            model_count=len(self.exported_meshes)
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_renderer(self):
        n64_utils.copy_src('renderer.c', 'src')
        n64_utils.copy_src('renderer.h', 'src')
        n64_utils.copy_src('utils.h', 'src')


    def write_scenes(self):
        self.write_scenes_c()
        self.write_scenes_h()

        # Apply coordinate conversion (Blender Z-up → N64 Y-up)
        codegen.convert_scene_data(self.scene_data)

        # Write converted scene data to C files
        for scene in bpy.data.scenes:
            if scene.library:
                continue
            self.write_scene_c(scene)


    def write_scene_c(self, scene):
        scene_name = arm.utils.safesrc(scene.name).lower()
        scene_data = self.scene_data[scene_name]

        clear_color = scene_data['world']['clear_color']
        ambient_color = scene_data['world']['ambient_color']

        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'scenes', 'scene.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'scenes', f'{scene_name}.c')
        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        scene_traits = scene_data.get('traits', [])

        output = tmpl_content.format(
            scene_name=scene_name,
            cr=n64_utils.to_uint8(clear_color[0]),
            cg=n64_utils.to_uint8(clear_color[1]),
            cb=n64_utils.to_uint8(clear_color[2]),
            ar=n64_utils.to_uint8(ambient_color[0]),
            ag=n64_utils.to_uint8(ambient_color[1]),
            ab=n64_utils.to_uint8(ambient_color[2]),
            camera_count=len(scene_data['cameras']),
            cameras_block=codegen.generate_camera_block(scene_data['cameras'], self.trait_info, scene_name),
            light_count=len(scene_data['lights']),
            lights_block=codegen.generate_light_block(scene_data['lights'], self.trait_info, scene_name),
            object_count=len(scene_data['objects']),
            objects_block=codegen.generate_object_block(scene_data['objects'], self.trait_info, scene_name),
            physics_block=codegen.generate_physics_block(scene_data['objects'], scene_data['world']),
            contact_subs_block=codegen.generate_contact_subscriptions_block(scene_data['objects'], self.trait_info),
            scene_trait_count=len(scene_traits),
            scene_traits_block=codegen.generate_scene_traits_block(scene_traits, self.trait_info, scene_name)
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_scenes_c(self):
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'scenes.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'scenes.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()


        init_lines = []
        init_switch_cases_lines = []
        name_entry_lines = []
        scene_count = 0

        for scene in bpy.data.scenes:
            if scene.library:
                continue
            scene_name = arm.utils.safesrc(scene.name).lower()
            original_name = scene.name  # Preserve original case for runtime lookup
            init_lines.append(f'    scene_{scene_name}_init(&g_scenes[SCENE_{scene_name.upper()}]);')
            init_switch_cases_lines.append(f'        case SCENE_{scene_name.upper()}:\n'
                                           f'            scene_{scene_name}_init(&g_scenes[SCENE_{scene_name.upper()}]);\n'
                                           f'            break;')
            # For runtime string -> SceneId lookup (use original name for case-sensitive match)
            name_entry_lines.append(f'    {{"{original_name}", SCENE_{scene_name.upper()}}},')
            scene_count += 1

        scene_inits = '\n'.join(init_lines)
        scene_init_switch_cases = '\n'.join(init_switch_cases_lines)
        scene_name_entries = '\n'.join(name_entry_lines)

        output = tmpl_content.format(
            scene_inits=scene_inits,
            scene_init_switch_cases=scene_init_switch_cases,
            scene_name_entries=scene_name_entries,
            scene_count=scene_count
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_scenes_h(self):
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'scenes.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'scenes.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        enum_lines = []
        declaration_lines = []
        scene_count = 0
        for scene in bpy.data.scenes:
            if scene.library:
                continue
            scene_name = arm.utils.safesrc(scene.name).lower()
            enum_lines.append(f'    SCENE_{scene_name.upper()} = {scene_count},')
            declaration_lines.append(f'void scene_{scene_name.lower()}_init(ArmScene *scene);')
            scene_count += 1
        scene_enum_entries = '\n'.join(enum_lines)
        scene_declarations = '\n'.join(declaration_lines)

        output = tmpl_content.format(
            scene_enum_entries=scene_enum_entries,
            scene_declarations=scene_declarations,
            scene_count=scene_count
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_iron(self):
        # Render trait_events.h template
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'events', 'trait_events.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'events', 'trait_events.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        max_button_subscribers = n64_utils.get_config('max_button_subscribers', 16)
        output = tmpl_content.format(max_button_subscribers=max_button_subscribers)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

        n64_utils.copy_src('events/trait_events.c', 'src')
        n64_utils.copy_src('iron/object/transform.h', 'src')
        n64_utils.copy_src('iron/object/transform.c', 'src')
        n64_utils.copy_src('iron/object/object.h', 'src')
        n64_utils.copy_src('iron/object/object.c', 'src')
        n64_utils.copy_src('iron/system/input.c', 'src')
        n64_utils.copy_src('iron/system/input.h', 'src')


    def write_signal(self):
        n64_utils.copy_src('signal.c', 'src/system')
        n64_utils.copy_src('signal.h', 'src/system')


    def reset_materials_to_bsdf(self):
        """Reset materials back to BSDF format (requires Fast64 addon)."""
        try:
            if not hasattr(bpy.ops.scene, 'f3d_convert_to_bsdf'):
                return False

            bpy.ops.scene.f3d_convert_to_bsdf(
                direction='BSDF',
                converter_type='All',
                backup=False,
                put_alpha_into_color=False,
                use_recommended=True,
                lights_for_colors=False,
                default_to_fog=False,
                set_rendermode_without_fog=False
            )
            bpy.ops.outliner.orphans_purge(
                do_local_ids=True,
                do_linked_ids=True,
                do_recursive=True
            )
            return True
        except Exception as e:
            log.warn(f'BSDF material reset failed: {e}')
            return False


    def run_make(self):
        msys2_executable = arm.utils.get_msys2_bash_executable()
        if len(msys2_executable) > 0:
            try:
                proc = subprocess.run(
                    [
                        msys2_executable,
                        '--login',
                        '-c',
                        (
                            f'export MSYSTEM=MINGW64; '
                            f'export N64_INST="{arm.utils.get_n64_toolchain_path()}"; '
                            f'export PATH="{arm.utils.get_n64_toolchain_path()}:{arm.utils.get_mingw64_path()}:$PATH"; '
                            f'cd "{os.path.abspath(arm.utils.build_dir())}/n64" && make'
                        )
                    ],
                    stdout=None,
                    stderr=None,
                    text=True
                )
            except Exception as e:
                log.error(f'Error running make: {e}')
                return False
            if proc.returncode != 0:
                log.error(f'Make process failed with exit code {proc.returncode}.')
                return False
        else:
            log.error('MSYS2 Bash executable path is not set in Armory preferences.')
            return False
        log.info('Info: N64 make process completed successfully.')
        return True


    def export(self):
        self.trait_info = codegen.get_trait_info()
        if not self.trait_info.get('traits'):
            log.warn("No traits found in n64_traits.json. Make sure arm_target_n64 is defined during build.")

        self.convert_materials_to_f3d()

        self.make_directories()
        self.export_meshes()

        # Build scene data early to determine if physics is needed
        for scene in bpy.data.scenes:
            if scene.library:
                continue
            self.build_scene_data(scene)

        # Compute is_static for all objects after trait_info is loaded
        n64_utils.compute_static_flags(self.scene_data, self.trait_info)

        # Detect UI canvas BEFORE write_traits so has_ui is set early
        self.detect_ui_canvas()

        # Write traits to detect feature usage (UI, physics from traits)
        self.write_traits()

        # Write autoloads (singletons with @:n64Autoload)
        self.write_autoloads()

        self.write_types()
        self.write_engine()
        self.write_physics()
        self.write_fonts()       # Must be before write_makefile (populates exported_fonts)
        self.write_makefile()    # Uses exported_fonts for font rules
        self.write_canvas()      # Generate canvas label data
        self.write_main()
        self.write_models()
        self.write_renderer()

        self.write_scenes()
        self.write_iron()
        self.write_signal()

        self.reset_materials_to_bsdf()
        log.info('Info: N64 export completed.')


    def publish(self):
        self.export()
        return self.run_make()


    def play(self):
        if not self.publish():
            return

        ares_emulator_executable = arm.utils.get_ares_emulator_executable()

        if not ares_emulator_executable:
            log.error('Ares emulator executable path is not set in Armory preferences.')
            return

        wrd = bpy.data.worlds['Arm']
        rom_path = os.path.join(arm.utils.build_dir(), 'n64', f'{arm.utils.safestr(wrd.arm_project_name)}.z64')

        subprocess.Popen(
            [ares_emulator_executable, rom_path],
            stdout=None,
            stderr=None,
            text=True
        )
