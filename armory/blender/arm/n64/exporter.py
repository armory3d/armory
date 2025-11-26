import os
import subprocess
import math
import bpy
import arm.utils
import arm.log as log

from arm.n64.input_mapping import GAMEPAD_TO_N64_MAP, INPUT_STATE_MAP
from arm.n64.utils import copy_src, get_clear_color, deselect_from_all_viewlayers, to_uint8


class N64Exporter:
    def __init__(self):
        self.scene_data = {}
        self.exported_meshes = {}
        self.trait_list = {}

        # trait_list = {
        #     "TraitName" : {
        #         "on_ready": [
        #             {
        #                 "action": { }
        #             }
        #         ],
        #         "on_update": [
        #             {
        #                 "condition": { "type": "button", "button": "a", "state": "started" },
        #                 "action": { "type": "scene_switch", "target": "Level_02" }
        #             }
        #         ],
        #         "on_remove": [
        #             {
        #                 "action": { }
        #             }
        #         ]
        #     }
        # }


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
        bpy.ops.scene.f3d_convert_to_bsdf(direction='F3D', converter_type='All', backup=False, put_alpha_into_color=False, use_recommended=True, lights_for_colors=False, default_to_fog=False, set_rendermode_without_fog=False)


    def make_directories(self):
        build_dir = arm.utils.build_dir()
        os.makedirs(f'{build_dir}/n64', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/assets', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/scenes', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src', exist_ok=True)


    def export_meshes(self):
        build_dir = arm.utils.build_dir()
        assets_dir = f'{build_dir}/n64/assets'

        self.exported_meshes = {}
        deselect_from_all_viewlayers()

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

        self.scene_data[scene_name] = {
            "world": {
                "clear_color": get_clear_color(scene),
                "ambient_color": list(scene.fast64.renderSettings.ambientColor)
            },
            "cameras": [],
            "lights": [],
            "objects": []
        }

        for obj in scene.objects:
            if obj.type == 'CAMERA':
                cam_pos = (obj.location[0], obj.location[2], -obj.location[1])
                cam_dir = obj.rotation_euler.to_matrix().col[2]
                cam_target = (obj.location[0] - cam_dir[0], obj.location[2] - cam_dir[2], -obj.location[1] + cam_dir[1])
                sensor = max(obj.data.sensor_width, obj.data.sensor_height)
                cam_fov = math.degrees(2 * math.atan((sensor * 0.5) / obj.data.lens))

                self.scene_data[scene_name]["cameras"].append({
                    "name": arm.utils.safesrc(obj.name),
                    "pos": list(cam_pos),
                    "target": list(cam_target),
                    "fov": cam_fov,
                    "near": obj.data.clip_start,
                    "far": obj.data.clip_end
                })
            elif obj.type == 'LIGHT': #TODO: support multiple light types [Point and Sun]
                light_dir = obj.rotation_euler.to_matrix().col[2]
                dir_vec = (light_dir[0], light_dir[2], -light_dir[1])
                length = math.sqrt(dir_vec[0]**2 + dir_vec[1]**2 + dir_vec[2]**2)
                if length > 0:
                    dir_vec = (dir_vec[0]/length, dir_vec[1]/length, dir_vec[2]/length)

                self.scene_data[scene_name]["lights"].append({
                    "name": arm.utils.safesrc(obj.name),
                    "color": list(obj.data.color),
                    "dir": list(dir_vec)
                })
            elif obj.type == 'MESH':
                mesh = obj.data
                mesh_name = self.exported_meshes[mesh]

                obj_pos = (obj.location[0], obj.location[2], -obj.location[1])
                e = obj.matrix_world.to_quaternion().to_euler('YZX')
                obj_rot = (-e.x, -e.z, e.y)
                obj_scale = (obj.scale[0] * 0.015, obj.scale[2] * 0.015, obj.scale[1] * 0.015)

                self.scene_data[scene_name]["objects"].append({
                    "name": arm.utils.safesrc(obj.name),
                    "mesh": f'MODEL_{mesh_name.upper()}',
                    "pos": list(obj_pos),
                    "rot": list(obj_rot),
                    "scale": list(obj_scale),
                    "visible": not obj.hide_render
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
            scene_lines.append(f'    scenes/{scene_name}.c')
        scene_files = '\\\n'.join(scene_lines)

        output = tmpl_content.format(
            tiny3d_path=os.path.join(arm.utils.get_sdk_path(), 'lib', 'tiny3d').replace('\\', '/'),
            game_title=arm.utils.safestr(wrd.arm_project_name),
            scene_files=scene_files
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_types(self):
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'types.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'types.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        output = tmpl_content.format(
            max_traits='4'
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_input(self):
        copy_src('input.c', 'src')
        copy_src('input.h', 'src')


    def write_engine(self):
        copy_src('engine.c', 'src')
        copy_src('engine.h', 'src')


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
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'models.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'models.c')

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
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'models.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'models.h')

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
        copy_src('renderer.c', 'src')
        copy_src('renderer.h', 'src')


    def write_scenes(self):
        self.write_scenes_c()
        self.write_scenes_h()

        for scene in bpy.data.scenes:
            if scene.library:
                continue
            self.build_scene_data(scene)
            self.write_scene_c(scene)


    def write_scene_c(self, scene):
        scene_name = arm.utils.safesrc(scene.name).lower()

        clear_color = self.scene_data[scene_name]['world']['clear_color']
        cr = to_uint8(clear_color[0])
        cg = to_uint8(clear_color[1])
        cb = to_uint8(clear_color[2])
        ambient_color = self.scene_data[scene_name]['world']['ambient_color']
        ar = to_uint8(ambient_color[0])
        ag = to_uint8(ambient_color[1])
        ab = to_uint8(ambient_color[2])

        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'scenes', 'scene.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'scenes', f'{arm.utils.safesrc(scene_name).lower()}.c')
        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        camera_block_lines = []
        for i, camera in enumerate(self.scene_data[scene_name]['cameras']):
            camera_block_lines.append(f'    cameras[{i}].pos = (T3DVec3){{{{{camera["pos"][0]:.6f}f, {camera["pos"][1]:.6f}f, {camera["pos"][2]:.6f}f}}}};')
            camera_block_lines.append(f'    cameras[{i}].target = (T3DVec3){{{{{camera["target"][0]:.6f}f, {camera["target"][1]:.6f}f, {camera["target"][2]:.6f}f}}}};')
            camera_block_lines.append(f'    cameras[{i}].fov = {camera["fov"]:.6f}f;')
            camera_block_lines.append(f'    cameras[{i}].near = {camera["near"]:.6f}f;')
            camera_block_lines.append(f'    cameras[{i}].far = {camera["far"]:.6f}f;')
            camera_block_lines.append(f'    cameras[{i}].trait_count = 0;')
        cameras_block = '\n'.join(camera_block_lines)

        light_block_lines = []
        for i, light in enumerate(self.scene_data[scene_name]['lights']):
            light_block_lines.append(f'    lights[{i}].color[0] = {to_uint8(light["color"][0])};')
            light_block_lines.append(f'    lights[{i}].color[1] = {to_uint8(light["color"][1])};')
            light_block_lines.append(f'    lights[{i}].color[2] = {to_uint8(light["color"][2])};')
            light_block_lines.append(f'    lights[{i}].dir = (T3DVec3){{{{{light["dir"][0]:.6f}f, {light["dir"][1]:.6f}f, {light["dir"][2]:.6f}f}}}};')
            light_block_lines.append(f'    lights[{i}].trait_count = 0;')
        lights_block = '\n'.join(light_block_lines)

        object_block_lines = []
        for i, object in enumerate(self.scene_data[scene_name]['objects']):
            object_block_lines.append(f'    objects[{i}].pos[0] = {object["pos"][0]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].pos[1] = { object["pos"][1]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].pos[2] = {object["pos"][2]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].rot[0] = {object["rot"][0]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].rot[1] = {object["rot"][1]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].rot[2] = {object["rot"][2]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].scale[0] = {object["scale"][0]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].scale[1] = {object["scale"][1]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].scale[2] = {object["scale"][2]:.6f}f;')
            object_block_lines.append(f'    models_get({object["mesh"]});')
            object_block_lines.append(f'    objects[{i}].dpl = models_get_dpl({object["mesh"]});')
            object_block_lines.append(f'    objects[{i}].model_mat = malloc_uncached(sizeof(T3DMat4FP) * FB_COUNT);')
            object_block_lines.append(f'    objects[{i}].visible = {str(object["visible"]).lower()};')
            object_block_lines.append(f'    objects[{i}].trait_count = 0;')
        objects_block = '\n'.join(object_block_lines)

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
            scene_trait_count=0,
            scene_traits_block=''
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


    def write_scenes_c(self):
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'scenes.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'scenes.c')

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
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'scenes.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'scenes.h')

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


    def write_cameras(self):
        copy_src('cameras.h', 'src')
        copy_src('cameras.c', 'src')


    def write_lights(self):
        copy_src('lights.h', 'src')
        copy_src('lights.c', 'src')


    def write_objects(self):
        copy_src('objects.h', 'src')
        copy_src('objects.c', 'src')


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
        bpy.ops.scene.f3d_convert_to_bsdf(direction='BSDF', converter_type='All', backup=False, put_alpha_into_color=False, use_recommended=True, lights_for_colors=False, default_to_fog=False, set_rendermode_without_fog=False)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


    def build(self):
        self.convert_materials_to_f3d()

        self.make_directories()
        self.export_meshes()

        self.write_makefile()
        self.write_types()
        self.write_input()
        self.write_engine()
        self.write_main()
        self.write_models()
        self.write_renderer()

        self.write_scenes()
        self.write_cameras()
        self.write_lights()
        self.write_objects()

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
