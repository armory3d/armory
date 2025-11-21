import os
import subprocess
import math
import bpy
import arm.utils


def to_uint8(value):
    return int(max(0, min(1, value)) * 255)


class N64Exporter:
    def __init__(self, scene):
        self.scene = scene
        self.data = {}
        self.exported_meshes = {}


    @classmethod
    def export_scene(cls, scene):
        exporter = cls(scene)
        exporter.execute()


    def make_directories(self):
        build_dir = arm.utils.build_dir()
        os.makedirs(f'{build_dir}/n64', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/assets', exist_ok=True)
        os.makedirs(f'{build_dir}/n64/src', exist_ok=True)


    def export_meshes(self):
        build_dir = arm.utils.build_dir()
        assets_dir = f'{build_dir}/n64/assets'

        self.exported_meshes = {}

        for obj in self.scene.objects:
            if obj.type != 'MESH':
                continue

            mesh = obj.data
            if mesh in self.exported_meshes:
                continue

            mesh_name = mesh.name.replace(" ", "_").lower()
            model_output_path = os.path.join(assets_dir, f'{mesh_name}.gltf')

            orig_loc = obj.location.copy()
            orig_rot = obj.rotation_euler.copy()
            orig_scale = obj.scale.copy()

            obj.location = (0.0, 0.0, 0.0)
            obj.rotation_euler = (0.0, 0.0, 0.0)
            obj.scale = (1.0, 1.0, 1.0)

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


    def build_scene_data(self):
        self.data = {
            "world": {
                "clear_color": self.get_clear_color(),
                "ambient_color": list(self.scene.fast64.renderSettings.ambientColor)
            },
            "cameras": [],
            "lights": [],
            "objects": []
        }

        for obj in self.scene.objects:
            if obj.type == 'CAMERA':
                cam_pos = (obj.location[0], obj.location[2], -obj.location[1])
                cam_dir = obj.rotation_euler.to_matrix().col[2]
                cam_target = (obj.location[0] - cam_dir[0], obj.location[2] - cam_dir[2], -obj.location[1] + cam_dir[1])
                sensor = max(obj.data.sensor_width, obj.data.sensor_height)
                cam_fov = math.degrees(2 * math.atan((sensor * 0.5) / obj.data.lens))

                self.data["cameras"].append({
                    "name": obj.name.replace(" ", "_").lower(),
                    "pos": list(cam_pos),
                    "target": list(cam_target),
                    "fov": cam_fov,
                    "near": obj.data.clip_start,
                    "far": obj.data.clip_end
                })
            elif obj.type == 'LIGHT': #TODO: support multiple light types [Point and Sun]
                light_dir = obj.rotation_euler.to_matrix().col[2]
                dir_vec = (light_dir[0], light_dir[2], -light_dir[1])

                self.data["lights"].append({
                    "name": obj.name.replace(" ", "_").lower(),
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

                self.data["objects"].append({
                    "name": obj.name.replace(" ", "_").lower(),
                    "mesh": "rom:/" + mesh_name + ".t3dm",
                    "pos": list(obj_pos),
                    "rot": list(obj_rot),
                    "scale": list(obj_scale)
                })


    def create_make_file(self):
        wrd = bpy.data.worlds['Arm']

        sdk_path = arm.utils.get_sdk_path()
        # libdragon_path = os.path.join(sdk_path, 'lib', 'libdragon').replace('\\', '/')
        tiny3d_path = os.path.join(sdk_path, 'lib', 'tiny3d').replace('\\', '/')

        make_file_content = f'''BUILD_DIR=build

T3D_INST={tiny3d_path}

include $(N64_INST)/include/n64.mk
include $(T3D_INST)/t3d.mk

GAME_TITLE := {arm.utils.safestr(wrd.arm_project_name)}
ROM_NAME := {arm.utils.safestr(wrd.arm_project_name)}

N64_CFLAGS += -std=gnu2x

src = src/main.c

assets_png = $(wildcard assets/*.png)
assets_gltf = $(wildcard assets/*.gltf)
assets_conv = $(addprefix filesystem/,$(notdir $(assets_png:%.png=%.sprite))) \\
			  $(addprefix filesystem/,$(notdir $(assets_ttf:%.ttf=%.font64))) \\
			  $(addprefix filesystem/,$(notdir $(assets_gltf:%.gltf=%.t3dm)))

all: $(ROM_NAME).z64

filesystem/%.sprite: assets/%.png
	@mkdir -p $(dir $@)
	@echo "    [SPRITE] $@"
	$(N64_MKSPRITE) $(MKSPRITE_FLAGS) -o filesystem "$<"

filesystem/%.t3dm: assets/%.gltf
	@mkdir -p $(dir $@)
	@echo "    [T3D-MODEL] $@"
	$(T3D_GLTF_TO_3D) "$<" $@
	$(N64_BINDIR)/mkasset -c 2 -o filesystem $@

$(BUILD_DIR)/$(ROM_NAME).dfs: $(assets_conv)
$(BUILD_DIR)/$(ROM_NAME).elf: $(src:%.c=$(BUILD_DIR)/%.o)

$(ROM_NAME).z64: N64_ROM_TITLE=$(GAME_TITLE)
$(ROM_NAME).z64: $(BUILD_DIR)/$(ROM_NAME).dfs

clean:
	rm -rf $(BUILD_DIR) *.z64
	rm -rf filesystem

build_lib:
	rm -rf $(BUILD_DIR) *.z64
	make -C $(T3D_INST)
	make all

-include $(wildcard $(BUILD_DIR)/*.d)

.PHONY: all clean
'''
        make_file_path = os.path.join(arm.utils.build_dir(), 'n64', 'Makefile')
        with open(make_file_path, 'w', encoding='utf-8') as f:
            f.write(make_file_content)

    def create_main_c(self):
        camera_pos = self.data["cameras"][0]["pos"]
        camera_target = self.data["cameras"][0]["target"]
        camera_fov = self.data["cameras"][0]["fov"]
        camera_near = self.data["cameras"][0]["near"]
        camera_far = self.data["cameras"][0]["far"]

        world_clear_color = self.data["world"]["clear_color"]
        cr = to_uint8(world_clear_color[0])
        cg = to_uint8(world_clear_color[1])
        cb = to_uint8(world_clear_color[2])
        world_ambient_color = self.data["world"]["ambient_color"]
        ar = to_uint8(world_ambient_color[0])
        ag = to_uint8(world_ambient_color[1])
        ab = to_uint8(world_ambient_color[2])

        light_count = len(self.data["lights"])
        object_count = len(self.data["objects"])

        main_file_content = f'''#include <stdio.h>
#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmath.h>
#include <t3d/t3dmodel.h>

#define FB_COUNT 3
'''
        if object_count > 0:
            main_file_content += f'''#define OBJECT_COUNT {object_count}
'''
        if light_count > 0:
            main_file_content += f'''#define LIGHT_COUNT {light_count}
'''
        main_file_content += f'''
static int frameIdx = 0;

'''
        if object_count > 0:
            main_file_content += f'''typedef struct {{
    float pos[3];
    float rot[3];
    float scale[3];
    T3DModel *model;
    T3DMat4FP *modelMat;
}} ArmObject;

ArmObject arm_object_create(const char *mesh, float pos[3], float rot[3], float scale[3]) {{
    ArmObject armObject = (ArmObject){{
        .pos = {{pos[0], pos[1], pos[2]}},
        .rot = {{rot[0], rot[1], rot[2]}},
        .scale = {{scale[0], scale[1], scale[2]}},
        .model = t3d_model_load(mesh),
        .modelMat = malloc_uncached(sizeof(T3DMat4FP) * FB_COUNT)
    }};
    return armObject;
}}

void arm_object_update(ArmObject *armObject) {{
    t3d_mat4fp_from_srt_euler(
        &armObject->modelMat[frameIdx],
        armObject->scale,
        armObject->rot,
        armObject->pos
    );
}}
'''
        if light_count > 0:
            main_file_content += f'''
typedef struct {{
    uint8_t color[4];
    T3DVec3 dir;
}} ArmLight;

ArmLight arm_light_create(uint8_t color[4], float dir[3]) {{
    ArmLight armLight = {{
        .color = {{color[0], color[1], color[2], color[3]}},
        .dir = {{{{dir[0], dir[1], dir[2]}}}}
    }};
    return armLight;
}}
'''

        main_file_content += f'''
int main(void)
{{
    debug_init_isviewer();
    debug_init_usblog();
    asset_init_compression(2);

    dfs_init(DFS_DEFAULT_LOCATION);

    display_init(RESOLUTION_320x240, DEPTH_16_BPP, FB_COUNT, GAMMA_NONE, FILTERS_RESAMPLE_ANTIALIAS);

    rdpq_init();

    t3d_init((T3DInitParams){{}});
    T3DViewport viewport = t3d_viewport_create_buffered(FB_COUNT);
    rdpq_text_register_font(FONT_BUILTIN_DEBUG_MONO, rdpq_font_load_builtin(FONT_BUILTIN_DEBUG_MONO));

    T3DVec3 camPos = {{{{{camera_pos[0]}f, {camera_pos[1]}f, {camera_pos[2]}f}}}};
    T3DVec3 camTarget = {{{{{camera_target[0]}f, {camera_target[1]}f, {camera_target[2]}f}}}};

    uint8_t colorClear[4] = {{{cr}, {cg}, {cb}, 0xFF}};
    uint8_t colorAmbient[4] = {{{ar}, {ag}, {ab}, 0xFF}};
'''
        if object_count > 0:
            main_file_content += f'''
    ArmObject armObjects[OBJECT_COUNT];
'''
            for i in range(object_count):
                mesh = self.data["objects"][i]["mesh"]
                pos = self.data["objects"][i]["pos"]
                rot = self.data["objects"][i]["rot"]
                scale = self.data["objects"][i]["scale"]
                main_file_content += f'''    armObjects[{i}] = arm_object_create("{mesh}", (float[3]){{{pos[0]}f, {pos[1]}f, {pos[2]}f}}, (float[3]){{{rot[0]}f, {rot[1]}f, {rot[2]}f}}, (float[3]){{{scale[0]}f, {scale[1]}f, {scale[2]}f}});
'''
        if light_count > 0:
            main_file_content += f'''
    ArmLight armLights[LIGHT_COUNT];
'''
            for i in range(light_count):
                color = self.data["lights"][i]["color"]
                r = to_uint8(color[0])
                g = to_uint8(color[1])
                b = to_uint8(color[2])
                dir = self.data["lights"][i]["dir"]
                main_file_content += f'''    armLights[{i}] = arm_light_create((uint8_t[4]){{{r}, {g}, {b}, 0xFF}}, (float[3]){{{dir[0]}f, {dir[1]}f, {dir[2]}f}});
'''

        main_file_content += f'''
    rspq_block_t *dplDraw = NULL;

    while(1)
    {{
        frameIdx = (frameIdx + 1) % FB_COUNT;

        t3d_viewport_set_projection(&viewport, T3D_DEG_TO_RAD({camera_fov}), {camera_near}f, {camera_far}f);
        t3d_viewport_look_at(&viewport, &camPos, &camTarget, &(T3DVec3){{{{0, 1, 0}}}});
'''
        if object_count > 0:
            main_file_content += f'''
        for (int i = 0; i < OBJECT_COUNT; i++)
        {{
            arm_object_update(&armObjects[i]);
        }}
'''
        main_file_content += f'''
        rdpq_attach(display_get(), display_get_zbuf());
        t3d_frame_start();
        t3d_viewport_attach(&viewport);

        t3d_screen_clear_color(RGBA32(colorClear[0], colorClear[1], colorClear[2], colorClear[3]));
        t3d_screen_clear_depth();
        t3d_light_set_ambient(colorAmbient);
'''
        if light_count > 0:
            main_file_content += f'''
        t3d_light_set_count(LIGHT_COUNT);

        for (int i = 0; i < LIGHT_COUNT; i++)
        {{
            t3d_light_set_directional(i, armLights[i].color, &armLights[i].dir);
        }}
'''

        main_file_content += f'''
        if (!dplDraw)
        {{
            rspq_block_begin();'''

        if object_count > 0:
            main_file_content += f'''
            for (int i = 0; i < OBJECT_COUNT; i++)
            {{
                t3d_matrix_push(&armObjects[i].modelMat[frameIdx]);
                t3d_model_draw(armObjects[i].model);
                t3d_matrix_pop(1);
            }}
'''
        main_file_content += f'''
            dplDraw = rspq_block_end();
        }}

        rspq_block_run(dplDraw);

        rdpq_sync_pipe();
        rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 200, 220, "FPS   : %.2f", display_get_fps());

        rdpq_detach_show();
    }}

    t3d_destroy();
    return 0;
}}
'''

        main_file_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'main.c')
        with open(main_file_path, 'w', encoding='utf-8') as f:
            f.write(main_file_content)


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


    def get_clear_color(self):
        if self.scene.world is None:
            return [0.051, 0.051, 0.051, 1.0]

        if self.scene.world.node_tree is None:
            c = self.scene.world.color
            return [c[0], c[1], c[2], 1.0]

        if 'Background' in self.scene.world.node_tree.nodes:
            background_node = self.scene.world.node_tree.nodes['Background']
            col = background_node.inputs[0].default_value
            strength = background_node.inputs[1].default_value
            ar = [col[0] * strength, col[1] * strength, col[2] * strength, col[3]]
            ar[0] = max(min(ar[0], 1.0), 0.0)
            ar[1] = max(min(ar[1], 1.0), 0.0)
            ar[2] = max(min(ar[2], 1.0), 0.0)
            ar[3] = max(min(ar[3], 1.0), 0.0)
            return ar
        return [0.051, 0.051, 0.051, 1.0]


    def execute(self):
        self.make_directories()
        self.export_meshes()
        self.build_scene_data()
        self.create_make_file()
        self.create_main_c()
        self.run_make()