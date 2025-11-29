import os
import subprocess
import math
import bpy

import arm
import arm.utils
import arm.log as log

from arm.n64 import codegen
from arm.n64 import converter as n64_converter
from arm.n64 import utils as n64_utils

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    log = arm.reload_module(log)
    codegen = arm.reload_module(codegen)
    n64_converter = arm.reload_module(n64_converter)
    n64_utils = arm.reload_module(n64_utils)
else:
    arm.enable_reload(__name__)


class N64Exporter:
    """
    N64 Exporter - Exports Armory scenes to N64 C code.

    Architecture:
    - Haxe macro does ALL trait analysis (members, buttons, scenes, C code)
    - codegen.py reads macro JSON and generates traits.h/c
    - This exporter handles mesh/scene/camera export and wires up trait pointers
    """

    def __init__(self):
        self.scene_data = {}
        self.exported_meshes = {}
        self.trait_info = {}        # Trait metadata from macro JSON


    @classmethod
    def build_project(cls):
        exporter = cls()
        exporter.build()


    @classmethod
    def publish_project(cls):
        exporter = cls()
        exporter.publish()


    @classmethod
    def play_project(cls):
        exporter = cls()
        exporter.play()


    def convert_materials_to_f3d(self):
        """Convert materials to F3D format. Requires Fast64 addon."""
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
        os.makedirs(f'{build_dir}/n64/src/iron', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/iron/object', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/iron/system', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src/scenes', exist_ok=True)


    def export_meshes(self):
        build_dir = arm.utils.build_dir()
        assets_dir = f'{build_dir}/n64/assets'

        self.exported_meshes = {}
        n64_utils.deselect_from_all_viewlayers()

        for scene in bpy.data.scenes:
            if scene.library:
                continue

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


    def build_scene_data(self, scene):
        scene_name = arm.utils.safesrc(scene.name).lower()

        # Extract scene-level traits with per-instance property values
        scene_traits = []
        if hasattr(scene, 'arm_traitlist'):
            for trait in scene.arm_traitlist:
                if trait.enabled_prop and trait.class_name_prop:
                    props = n64_utils.extract_blender_trait_props(trait)
                    scene_traits.append({
                        "class_name": trait.class_name_prop,
                        "type": trait.type_prop,
                        "props": props
                    })

        self.scene_data[scene_name] = {
            "world": {
                "clear_color": n64_utils.get_clear_color(scene),
                "ambient_color": list(scene.fast64.renderSettings.ambientColor)
            },
            "cameras": [],
            "lights": [],
            "objects": [],
            "traits": scene_traits
        }

        for obj in scene.objects:
            if obj.type == 'CAMERA':
                # Raw Blender coordinates - converter.py will transform later
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
                    "pos": list(obj.location),
                    "target": cam_target,
                    "fov": cam_fov,
                    "near": obj.data.clip_start,
                    "far": obj.data.clip_end
                })
            elif obj.type == 'LIGHT':  # TODO: support multiple light types [Point and Sun]
                # Raw Blender direction - converter.py will transform and normalize
                light_dir = obj.rotation_euler.to_matrix().col[2]

                self.scene_data[scene_name]["lights"].append({
                    "name": arm.utils.safesrc(obj.name),
                    "color": list(obj.data.color),
                    "dir": list(light_dir)
                })
            elif obj.type == 'MESH':
                mesh = obj.data
                mesh_name = self.exported_meshes[mesh]

                # Raw Blender coordinates - converter.py will transform later
                # Euler from matrix for consistent rotation handling
                euler = obj.matrix_world.to_quaternion().to_euler('YZX')

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

                # Extract traits from object with their per-instance property values
                obj_traits = []
                if hasattr(obj, 'arm_traitlist'):
                    for trait in obj.arm_traitlist:
                        if trait.enabled_prop and trait.class_name_prop:
                            props = n64_utils.extract_blender_trait_props(trait)
                            obj_traits.append({
                                "class_name": trait.class_name_prop,
                                "type": trait.type_prop,
                                "props": props
                            })

                self.scene_data[scene_name]["objects"].append({
                    "name": arm.utils.safesrc(obj.name),
                    "mesh": f'MODEL_{mesh_name.upper()}',
                    "pos": list(obj.location),
                    "rot": [euler.x, euler.y, euler.z],
                    "scale": list(obj.scale),
                    "visible": not obj.hide_render,
                    "bounds_center": bounds_center,
                    "bounds_radius": bounds_radius,
                    "traits": obj_traits
                })


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

        output = tmpl_content.format(
            tiny3d_path=os.path.join(arm.utils.get_sdk_path(), 'lib', 'tiny3d').replace('\\', '/'),
            game_title=arm.utils.safestr(wrd.arm_project_name),
            scene_files=scene_files
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_types(self):
        wrd = bpy.data.worlds['Arm']
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'types.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'types.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        debug_hud_define = '\n#define ARM_DEBUG_HUD' if wrd.arm_debug_console else ''
        output = tmpl_content.format(debug_hud_define=debug_hud_define)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_input(self):
        n64_utils.copy_src('iron/system/input.c', 'src')
        n64_utils.copy_src('iron/system/input.h', 'src')


    def write_traits(self):
        codegen.write_traits_files()


    def write_engine(self):
        n64_utils.copy_src('engine.c', 'src')
        n64_utils.copy_src('engine.h', 'src')


    def write_main(self):
        wrd = bpy.data.worlds['Arm']
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'main.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'main.c')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        output = tmpl_content.format(
            initial_scene_id=f'SCENE_{arm.utils.safesrc(wrd.arm_exporterlist[wrd.arm_exporterlist_index].arm_project_scene.name).upper()}'
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


    def write_scenes(self):
        self.write_scenes_c()
        self.write_scenes_h()

        # Build raw scene data from Blender
        for scene in bpy.data.scenes:
            if scene.library:
                continue
            self.build_scene_data(scene)

        # Apply coordinate conversion using rules from macro JSON
        n64_converter.convert_scene_data(self.scene_data)

        # Write converted scene data to C files
        for scene in bpy.data.scenes:
            if scene.library:
                continue
            self.write_scene_c(scene)


    def write_scene_c(self, scene):
        scene_name = arm.utils.safesrc(scene.name).lower()

        clear_color = self.scene_data[scene_name]['world']['clear_color']
        cr = n64_utils.to_uint8(clear_color[0])
        cg = n64_utils.to_uint8(clear_color[1])
        cb = n64_utils.to_uint8(clear_color[2])
        ambient_color = self.scene_data[scene_name]['world']['ambient_color']
        ar = n64_utils.to_uint8(ambient_color[0])
        ag = n64_utils.to_uint8(ambient_color[1])
        ab = n64_utils.to_uint8(ambient_color[2])

        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'scenes', 'scene.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'scenes', f'{arm.utils.safesrc(scene_name).lower()}.c')
        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        camera_block_lines = []
        for i, camera in enumerate(self.scene_data[scene_name]['cameras']):
            prefix = f'cameras[{i}]'
            camera_block_lines.extend(codegen.generate_transform_block(prefix, camera["pos"]))
            camera_block_lines.append(f'    {prefix}.target = (T3DVec3){{{{{camera["target"][0]:.6f}f, {camera["target"][1]:.6f}f, {camera["target"][2]:.6f}f}}}};')
            camera_block_lines.append(f'    {prefix}.fov = {camera["fov"]:.6f}f;')
            camera_block_lines.append(f'    {prefix}.near = {camera["near"]:.6f}f;')
            camera_block_lines.append(f'    {prefix}.far = {camera["far"]:.6f}f;')
            camera_block_lines.extend(codegen.generate_trait_block(prefix, camera.get("traits", []), self.trait_info, scene_name))
        cameras_block = '\n'.join(camera_block_lines)

        light_block_lines = []
        for i, light in enumerate(self.scene_data[scene_name]['lights']):
            prefix = f'lights[{i}]'
            light_block_lines.append(f'    {prefix}.color[0] = {n64_utils.to_uint8(light["color"][0])};')
            light_block_lines.append(f'    {prefix}.color[1] = {n64_utils.to_uint8(light["color"][1])};')
            light_block_lines.append(f'    {prefix}.color[2] = {n64_utils.to_uint8(light["color"][2])};')
            light_block_lines.append(f'    {prefix}.dir = (T3DVec3){{{{{light["dir"][0]:.6f}f, {light["dir"][1]:.6f}f, {light["dir"][2]:.6f}f}}}};')
            light_block_lines.extend(codegen.generate_trait_block(prefix, light.get("traits", []), self.trait_info, scene_name))
        lights_block = '\n'.join(light_block_lines)

        object_block_lines = []
        for i, obj in enumerate(self.scene_data[scene_name]['objects']):
            prefix = f'objects[{i}]'
            object_block_lines.extend(codegen.generate_transform_block(prefix, obj["pos"], obj["rot"], obj["scale"]))
            object_block_lines.append(f'    models_get({obj["mesh"]});')
            object_block_lines.append(f'    {prefix}.dpl = models_get_dpl({obj["mesh"]});')
            object_block_lines.append(f'    {prefix}.model_mat = malloc_uncached(sizeof(T3DMat4FP) * FB_COUNT);')
            object_block_lines.append(f'    {prefix}.visible = {str(obj["visible"]).lower()};')
            # Bounding sphere for frustum culling
            bc = obj.get("bounds_center", [0, 0, 0])
            br = obj.get("bounds_radius", 1.0)
            object_block_lines.append(f'    {prefix}.bounds_center = (T3DVec3){{{{ {bc[0]:.6f}f, {bc[1]:.6f}f, {bc[2]:.6f}f }}}};')
            object_block_lines.append(f'    {prefix}.bounds_radius = {br:.6f}f;')
            object_block_lines.extend(codegen.generate_trait_block(prefix, obj.get("traits", []), self.trait_info, scene_name))
        objects_block = '\n'.join(object_block_lines)

        # Generate scene trait assignments
        scene_traits = self.scene_data[scene_name].get('traits', [])
        scene_traits_block_lines = codegen.generate_trait_block('(*scene)', scene_traits, self.trait_info, scene_name)
        scene_traits_block = '\n'.join(scene_traits_block_lines)

        output = tmpl_content.format(
            scene_name=scene_name,
            cr=cr,
            cg=cg,
            cb=cb,
            ar=ar,
            ag=ag,
            ab=ab,
            camera_count=len(self.scene_data[scene_name]['cameras']),
            cameras_block=cameras_block,
            light_count=len(self.scene_data[scene_name]['lights']),
            lights_block=lights_block,
            object_count=len(self.scene_data[scene_name]['objects']),
            objects_block=objects_block,
            scene_trait_count=len(scene_traits),
            scene_traits_block=scene_traits_block
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

        for scene in bpy.data.scenes:
            if scene.library:
                continue
            scene_name = arm.utils.safesrc(scene.name).lower()
            init_lines.append(f'    scene_{scene_name}_init(&g_scenes[SCENE_{scene_name.upper()}]);')
            init_switch_cases_lines.append(f'        case SCENE_{scene_name.upper()}:\n'
                                           f'            scene_{scene_name}_init(&g_scenes[SCENE_{scene_name.upper()}]);\n'
                                           f'            break;')

        scene_inits = '\n'.join(init_lines)
        scene_init_switch_cases = '\n'.join(init_switch_cases_lines)

        output = tmpl_content.format(
            scene_inits=scene_inits,
            scene_init_switch_cases=scene_init_switch_cases
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
        n64_utils.copy_src('iron/object/transform.h', 'src')
        n64_utils.copy_src('iron/object/transform.c', 'src')


    def run_make(self):
        msys2_executable = arm.utils.get_msys2_bash_executable()
        if len(msys2_executable) > 0:
            try:
                proc = subprocess.run(
                    [
                        rf'{msys2_executable}',
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
        return True


    def reset_materials_to_bsdf(self):
        """Reset materials back to BSDF format. Requires Fast64 addon."""
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


    def build(self):
        # Step 1: Load trait metadata from macro-generated JSON
        log.info('Loading trait metadata from Haxe macro...')
        self.trait_info = codegen.get_trait_info()

        # Get list of valid Blender scene names for validation
        blender_scenes = [arm.utils.safesrc(s.name).lower() for s in bpy.data.scenes if not s.library]
        log.info(f"Blender scenes: {blender_scenes}")

        if not self.trait_info.get('traits'):
            log.warn("No traits found in macro JSON. Make sure to compile with arm_target_n64 defined.")
        else:
            log.info(f"Found traits: {list(self.trait_info['traits'].keys())}")
            log.info(f"Input buttons used: {self.trait_info.get('input_buttons', [])}")
            if self.trait_info.get('has_transform'):
                log.info("Transform operations detected")
            if self.trait_info.get('has_scene'):
                scene_names = self.trait_info.get('scene_names', [])
                log.info(f"Scene names detected: {scene_names}")

                # Validate detected scene names against Blender scenes
                literal_scenes = [s for s in scene_names if not s.startswith('member:')]
                invalid_scenes = [s for s in literal_scenes if s not in blender_scenes and s != 'unknown']
                if invalid_scenes:
                    log.warn(f"Invalid scene names detected: {invalid_scenes}")
                    log.warn(f"Valid scene names are: {blender_scenes}")
                    log.warn("Scene switching may use wrong scene IDs. Check your Haxe trait code.")

        # Step 2: Convert materials for N64
        self.convert_materials_to_f3d()

        # Step 3: Export assets
        self.make_directories()
        self.export_meshes()

        # Step 4: Generate C code
        self.write_makefile()
        self.write_types()
        self.write_input()
        self.write_engine()
        self.write_main()
        self.write_models()
        self.write_renderer()

        self.write_scenes()
        self.write_traits()  # Reads from macro JSON via codegen
        self.write_iron()

        self.reset_materials_to_bsdf()


    def publish(self):
        self.build()
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
            [
                rf'{ares_emulator_executable}',
                rf'{rom_path}'
            ],
            stdout=None,
            stderr=None,
            text=True
        )
