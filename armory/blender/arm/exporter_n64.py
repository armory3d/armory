import os
import shutil
import subprocess
import math
import bpy
import arm.utils


def copy_src(name, path=''):
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), path, name)
    out_path = os.path.join(arm.utils.build_dir(), 'n64', path, name)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    shutil.copyfile(tmpl_path, out_path)


def get_clear_color(scene):
    if scene.world is None:
        return [0.051, 0.051, 0.051, 1.0]

    if scene.world.node_tree is None:
        c = scene.world.color
        return [c[0], c[1], c[2], 1.0]

    if 'Background' in scene.world.node_tree.nodes:
        background_node = scene.world.node_tree.nodes['Background']
        col = background_node.inputs[0].default_value
        strength = background_node.inputs[1].default_value
        ar = [col[0] * strength, col[1] * strength, col[2] * strength, col[3]]
        ar[0] = max(min(ar[0], 1.0), 0.0)
        ar[1] = max(min(ar[1], 1.0), 0.0)
        ar[2] = max(min(ar[2], 1.0), 0.0)
        ar[3] = max(min(ar[3], 1.0), 0.0)
        return ar
    return [0.051, 0.051, 0.051, 1.0]


def to_uint8(value):
    return int(max(0, min(1, value)) * 255)


class N64Exporter:
    def __init__(self):
        self.scene_data = {}
        self.exported_meshes = {}


    @classmethod
    def export(cls):
        exporter = cls()
        exporter.execute()


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

        for scene in bpy.data.scenes:
            if scene.name.startswith('fast64'):
                continue

            main_scene = bpy.context.scene
            main_view_layer = bpy.context.view_layer

            for obj in scene.objects:
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

                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)

                bpy.ops.export_scene.gltf(
                    filepath=model_output_path,
                    export_format='GLTF_SEPARATE',
                    export_extras=True,
                    use_selection=True
                )

                obj.location = orig_loc
                obj.rotation_euler = orig_rot
                obj.scale = orig_scale

                bpy.context.view_layer.update()
                self.exported_meshes[mesh] = mesh_name

            bpy.context.window.scene = main_scene
            bpy.context.window.view_layer = main_view_layer


    def build_scene_data(self, scene):
        scene_name = arm.utils.safesrc(scene.name)
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
                    "scale": list(obj_scale)
                })


    def write_makefile(self):
        wrd = bpy.data.worlds['Arm']
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'Makefile.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'Makefile')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        scene_lines = []
        for scene in bpy.data.scenes:
            if scene.name.startswith('fast64'):
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

        # lines = []
        # trait_enum_entries = ''

        output = tmpl_content.format(
            max_traits='4',
            trait_enum_entries='TRAIT_NONE = 0'
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)


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
            initial_scene_id=f'SCENE_{arm.utils.safesrc(wrd.arm_exporterlist[wrd.arm_exporterlist_index].arm_project_scene.name.upper())}'
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
            if scene.name.startswith('fast64'):
                continue
            self.build_scene_data(scene)
            self.write_scene_c(scene)


    def write_scene_c(self, scene):
        clear_color = self.scene_data[scene.name]['world']['clear_color']
        cr = to_uint8(clear_color[0])
        cg = to_uint8(clear_color[1])
        cb = to_uint8(clear_color[2])
        ambient_color = self.scene_data[scene.name]['world']['ambient_color']
        ar = to_uint8(ambient_color[0])
        ag = to_uint8(ambient_color[1])
        ab = to_uint8(ambient_color[2])

        cam_pos = self.scene_data[scene.name]['cameras'][0]['pos']
        cam_target = self.scene_data[scene.name]['cameras'][0]['target']
        cam_fov = self.scene_data[scene.name]['cameras'][0]['fov']
        cam_near = self.scene_data[scene.name]['cameras'][0]['near']
        cam_far = self.scene_data[scene.name]['cameras'][0]['far']

        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'scenes', 'scene.c.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'scenes', f'{arm.utils.safesrc(scene.name).lower()}.c')
        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        light_block_lines = []
        for i, light in enumerate(self.scene_data[scene.name]['lights']):
            light_block_lines.append(f'    lights[{i}].color[0] = {to_uint8(light["color"][0])};')
            light_block_lines.append(f'    lights[{i}].color[1] = {to_uint8(light["color"][1])};')
            light_block_lines.append(f'    lights[{i}].color[2] = {to_uint8(light["color"][2])};')
            light_block_lines.append(f'    lights[{i}].dir = (T3DVec3){{{{{light["dir"][0]:.6f}f, {light["dir"][1]:.6f}f, {light["dir"][2]:.6f}f}}}};')
        lights_block = '\n'.join(light_block_lines)

        object_block_lines = []
        for i, object in enumerate(self.scene_data[scene.name]['objects']):
            object_block_lines.append(f'    objects[{i}].pos[0] = {object["pos"][0]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].pos[1] = { object["pos"][1]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].pos[2] = {object["pos"][2]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].rot[0] = {object["rot"][0]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].rot[1] = {object["rot"][1]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].rot[2] = {object["rot"][2]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].scale[0] = {object["scale"][0]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].scale[1] = {object["scale"][1]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].scale[2] = {object["scale"][2]:.6f}f;')
            object_block_lines.append(f'    objects[{i}].model = models_get({object["mesh"]});')
            object_block_lines.append(f'    objects[{i}].modelMat = malloc_uncached(sizeof(T3DMat4FP) * FB_COUNT);')
        objects_block = '\n'.join(object_block_lines)

        output = tmpl_content.format(
            scene_name=arm.utils.safesrc(scene.name).lower(),
            cr=cr,
            cg=cg,
            cb=cb,
            ar=ar,
            ag=ag,
            ab=ab,
            cam_pos_x=cam_pos[0],
            cam_pos_y=cam_pos[1],
            cam_pos_z=cam_pos[2],
            cam_target_x=cam_target[0],
            cam_target_y=cam_target[1],
            cam_target_z=cam_target[2],
            cam_fov=cam_fov,
            cam_near=cam_near,
            cam_far=cam_far,
            light_count=len(self.scene_data[scene.name]['lights']),
            lights_block=lights_block,
            object_count=len(self.scene_data[scene.name]['objects']),
            objects_block=objects_block
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
            if scene.name.startswith('fast64'):
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
        for i, scene in enumerate(bpy.data.scenes):
            if scene.name.startswith('fast64'):
                continue
            scene_name = arm.utils.safesrc(scene.name).upper()
            enum_lines.append(f'    SCENE_{scene_name} = {i},')
            declaration_lines.append(f'void scene_{scene_name}_init(ArmScene *scene);')
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
        pass


    def write_lights(self):
        pass


    def write_objects(self):
        pass


    def run_make(self):
        msys2_executable = arm.utils.get_msys2_bash_executable()
        if len(msys2_executable) > 0:
            subprocess.run(
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


    def reset_materials_to_bsdf(self):
        bpy.ops.scene.f3d_convert_to_bsdf(direction='BSDF', converter_type='All', backup=False, put_alpha_into_color=False, use_recommended=True, lights_for_colors=False, default_to_fog=False, set_rendermode_without_fog=False)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


    def execute(self):
        self.convert_materials_to_f3d()

        self.make_directories()
        self.export_meshes()

        self.write_makefile()
        self.write_types()
        self.write_engine()
        self.write_main()
        self.write_models()
        self.write_renderer()

        self.write_scenes()
        self.write_cameras()
        self.write_lights()
        self.write_objects()

        self.reset_materials_to_bsdf()

        self.run_make()