import os
import subprocess
import math
import shutil
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


class N64Exporter:
    """N64 Exporter - Exports Armory scenes to N64 C code."""

    def __init__(self):
        self.scene_data = {}
        self.exported_meshes = {}
        self.exported_fonts = {}    # Track exported fonts: {font_name: font_path}
        self.trait_info = {}        # Trait metadata from macro JSON
        self.has_physics = False    # Track if any rigid bodies are exported
        self.has_ui = False         # Track if any UI elements are used


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
                if trait.enabled_prop and trait.class_name_prop:
                    prop_data = n64_utils.extract_blender_trait_props(trait)
                    traits.append({
                        "class_name": trait.class_name_prop,
                        "type": trait.type_prop,
                        "props": prop_data['values'],
                        "type_overrides": prop_data['types']
                    })
        return traits


    def build_scene_data(self, scene):
        scene_name = arm.utils.safesrc(scene.name).lower()
        scene_traits = self._extract_traits(scene)

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
                        "is_kinematic": rb.kinematic,
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

        # UI source files (only if Koui UI elements are used)
        if self.has_ui:
            koui_sources = '''src +=\\
    src/koui/koui.c \\
    src/data/fonts.c'''
        else:
            koui_sources = '# No UI'

        output = tmpl_content.format(
            tiny3d_path=os.path.join(arm.utils.get_sdk_path(), 'lib', 'tiny3d').replace('\\', '/'),
            game_title=arm.utils.safestr(wrd.arm_project_name),
            scene_files=scene_files,
            physics_sources=physics_sources,
            koui_sources=koui_sources
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


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
        # Collect all type overrides from all trait instances across all scenes
        type_overrides = self._collect_type_overrides()
        features = codegen.write_traits_files(type_overrides)

        # Update feature flags based on trait analysis
        if features:
            if features.get('has_ui'):
                self.has_ui = True
            if features.get('has_physics'):
                self.has_physics = True

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
            enable_ui=1 if self.has_ui else 0
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def write_koui(self):
        """Copy Koui UI wrapper files if UI is used."""
        if not self.has_ui:
            return

        # Copy koui directory
        n64_utils.copy_dir('koui', 'src')

    def write_fonts(self):
        """Copy font files and generate fonts.c/fonts.h if UI is used."""
        if not self.has_ui:
            return

        # Copy font files from project's Assets folder to n64/assets
        project_assets = os.path.join(arm.utils.get_fp(), 'Assets')
        n64_assets = os.path.join(arm.utils.build_dir(), 'n64', 'assets')
        os.makedirs(n64_assets, exist_ok=True)

        if os.path.exists(project_assets):
            import glob
            # Search recursively in Assets and all subdirectories
            fonts = glob.glob(os.path.join(project_assets, '**', '*.ttf'), recursive=True)
            for i, font_path in enumerate(fonts):
                font_basename = os.path.splitext(os.path.basename(font_path))[0]
                # Store with index
                self.exported_fonts[font_basename] = font_basename
                # Copy with original name
                dst = os.path.join(n64_assets, f'{font_basename}.ttf')
                shutil.copy(font_path, dst)
                log.info(f'Copied font: {font_basename}.ttf')

        # Generate fonts.c and fonts.h
        if self.exported_fonts:
            self.write_fonts_c()
            self.write_fonts_h()

    def write_fonts_c(self):
        """Generate fonts.c from template."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'fonts.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'fonts.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        lines = []
        for font_name in self.exported_fonts.values():
            lines.append(f'    "rom:/{font_name}.font64"')
        font_paths = ',\n'.join(lines)

        output = tmpl_content.format(
            font_paths=font_paths,
            font_count=len(self.exported_fonts)
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def write_fonts_h(self):
        """Generate fonts.h from template."""
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'fonts.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'fonts.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        lines = []
        for i, font_name in enumerate(self.exported_fonts.values()):
            # Create a safe enum name (uppercase, replace special chars with _)
            enum_name = font_name.upper().replace('-', '_').replace(' ', '_')
            lines.append(f'    FONT_{enum_name} = {i},')
        font_enum_entries = '\n'.join(lines)

        output = tmpl_content.format(
            font_enum_entries=font_enum_entries,
            font_count=len(self.exported_fonts)
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

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

        output = tmpl_content.format(
            initial_scene_id=f'SCENE_{arm.utils.safesrc(wrd.arm_exporterlist[wrd.arm_exporterlist_index].arm_project_scene.name).upper()}',
            fixed_timestep=fixed_timestep,
            physics_debug_mode=physics_debug_mode
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
            init_lines.append(f'    scene_{scene_name}_init(&g_scenes[SCENE_{scene_name.upper()}]);')
            init_switch_cases_lines.append(f'        case SCENE_{scene_name.upper()}:\n'
                                           f'            scene_{scene_name}_init(&g_scenes[SCENE_{scene_name.upper()}]);\n'
                                           f'            break;')
            # For runtime string -> SceneId lookup
            name_entry_lines.append(f'    {{"{scene_name}", SCENE_{scene_name.upper()}}},')
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

        # Write traits FIRST to detect feature usage (UI, physics from traits)
        self.write_traits()

        self.write_makefile()
        self.write_types()
        self.write_engine()
        self.write_physics()
        self.write_koui()
        self.write_fonts()
        self.write_main()
        self.write_models()
        self.write_renderer()

        self.write_scenes()
        self.write_iron()

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
