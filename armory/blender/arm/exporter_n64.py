import os
import subprocess
import bpy
import arm.utils

class N64Exporter:
    def __init__(self, scene):
        self.scene = scene

    @classmethod
    def export_scene(cls, scene):
        """Export N64 scene - main entry point matching exporter.py pattern"""
        exporter = cls(scene)
        exporter.execute()

    def make_directories(self):
        os.makedirs(arm.utils.build_dir() + '/n64', exist_ok=True)
        os.makedirs(arm.utils.build_dir() + '/n64/assets', exist_ok=True)
        os.makedirs(arm.utils.build_dir() + '/n64/src', exist_ok=True)

    def export_glb_scene(self):
        model_name = self.scene.name.replace(" ", "_").lower()
        model_output_path = os.path.join(arm.utils.build_dir(), 'n64', 'assets', f'{model_name}.glb')

        bpy.ops.export_scene.gltf(
            filepath=model_output_path,
            export_format='GLB',
            export_extras=True,
        )

    def create_make_file(self):
        wrd = bpy.data.worlds['Arm']

        sdk_path = arm.utils.get_sdk_path()
        libdragon_path = os.path.join(sdk_path, 'lib', 'libdragon').replace('\\', '/')
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
assets_gltf = $(wildcard assets/*.glb)
assets_conv = $(addprefix filesystem/,$(notdir $(assets_png:%.png=%.sprite))) \\
			  $(addprefix filesystem/,$(notdir $(assets_ttf:%.ttf=%.font64))) \\
			  $(addprefix filesystem/,$(notdir $(assets_gltf:%.glb=%.t3dm)))

all: $(ROM_NAME).z64

filesystem/%.sprite: assets/%.png
	@mkdir -p $(dir $@)
	@echo "    [SPRITE] $@"
	$(N64_MKSPRITE) $(MKSPRITE_FLAGS) -o filesystem "$<"

filesystem/%.t3dm: assets/%.glb
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
        scene = self.scene
        camera = scene.camera
        light = None
        model_name = scene.name.replace(" ", "_").lower()

        for obj in scene.objects:
            if obj.type == 'LIGHT':
                light = obj
                break

        cam_loc = (0, 0, 0)
        cam_dir = (0, 0, 0)
        cam_fov = 50.0
        light_dir = (0, 0, 0)

        if camera:
            cam_loc = camera.location
            rot_matrix = camera.rotation_euler.to_matrix()
            cam_dir = rot_matrix.col[2]
            cam_fov = camera.data.lens
        else:
            print(f"[N64 Export] WARNING: No camera found in scene '{scene.name}'")

        if light:
            rot_matrix = light.rotation_euler.to_matrix()
            light_dir = rot_matrix.col[2]
        else:
            print(f"[N64 Export] WARNING: No light found in scene '{scene.name}'")

        main_file_content = f'''#include <stdio.h>
#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmath.h>
#include <t3d/t3dmodel.h>
#include <t3d/t3ddebug.h>

int main(void)
{{
    joypad_inputs_t inputs;
    joypad_init();

    debug_init_isviewer();
    debug_init_usblog();

    asset_init_compression(2);
    dfs_init(DFS_DEFAULT_LOCATION);
    display_init(RESOLUTION_320x240, DEPTH_16_BPP, 3, GAMMA_NONE, FILTERS_RESAMPLE_ANTIALIAS);
    rdpq_init();

    t3d_init((T3DInitParams){{}});
    T3DViewport viewport = t3d_viewport_create();
    rdpq_text_register_font(FONT_BUILTIN_DEBUG_MONO, rdpq_font_load_builtin(FONT_BUILTIN_DEBUG_MONO));

    T3DMat4 modelMat;
    t3d_mat4_identity(&modelMat);
    T3DMat4FP* modelMatFP = malloc_uncached(sizeof(T3DMat4FP));

    const T3DVec3 camPos = {{{{{cam_loc[0]}f, {cam_loc[2]}f, {-cam_loc[1]}f}}}};
    const T3DVec3 camTarget = {{{{{cam_loc[0] - cam_dir[0]}f, {cam_loc[2] - cam_dir[2]}f, {-(cam_loc[1] - cam_dir[1])}f}}}};

    uint8_t colorAmbient[4] = {{80, 80, 100, 0xff}};
    uint8_t colorDir[4] = {{0xEE, 0xAA, 0xAA, 0xFF}};

    T3DVec3 lightDirVec = {{{{{light_dir[0]}f, {light_dir[2]}f, {-light_dir[1]}f}}}};
    t3d_vec3_norm(&lightDirVec);

    T3DModel *model = t3d_model_load("rom:/{model_name}.t3dm");
    T3DVec3 modelPos = {{{{0.0f, 0.0f, 0.0f}}}};
    float modelScale = 0.025f;

    float rotAngle = 0.0f;
    rspq_block_t *dplDraw = NULL;

    while(1)
    {{
        joypad_poll();
        inputs = joypad_get_inputs(JOYPAD_PORT_1);

        if (inputs.btn.a)
        {{
            rotAngle += 0.03f;
        }}

        modelPos.x += inputs.stick_x * 0.05f;
        modelPos.z -= inputs.stick_y * 0.05f;

        t3d_viewport_set_projection(&viewport, T3D_DEG_TO_RAD({cam_fov}), 10.0f, 150.0f);
        t3d_viewport_look_at(&viewport, &camPos, &camTarget, &(T3DVec3){{{{0, 1, 0}}}});

        t3d_mat4_from_srt_euler(&modelMat,
            (float[3]){{modelScale, modelScale, modelScale}},
            (float[3]){{0.0f, rotAngle, 0.0f}},
            (float[3]){{modelPos.x, modelPos.y, modelPos.z}}
        );
        t3d_mat4_to_fixed(modelMatFP, &modelMat);

        rdpq_attach(display_get(), display_get_zbuf());
        t3d_frame_start();
        t3d_viewport_attach(&viewport);

        t3d_screen_clear_color(RGBA32(100, 80, 80, 0xFF));
        t3d_screen_clear_depth();

        t3d_light_set_ambient(colorAmbient);
        t3d_light_set_directional(0, colorDir, &lightDirVec);
        t3d_light_set_count(1);

        if (!dplDraw)
        {{
            rspq_block_begin();
            t3d_matrix_push(modelMatFP);
            t3d_model_draw(model);
            t3d_matrix_pop(1);
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

    def execute(self):
        """Main export workflow"""
        self.make_directories()
        self.export_glb_scene()
        self.create_make_file()
        self.create_main_c()