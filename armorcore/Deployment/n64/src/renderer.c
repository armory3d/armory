#include <stdint.h>
#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmodel.h>

#include "types.h"
#include "iron/system/input.h"

static int frameIdx = 0;

void renderer_begin_frame(T3DViewport *viewport, ArmScene *scene)
{
    ArmCamera *cam = &scene->cameras[scene->active_camera_id];

    t3d_viewport_set_projection(
        viewport,
        T3D_DEG_TO_RAD(cam->fov),
        cam->near,
        cam->far
    );

	t3d_viewport_look_at(
		viewport,
        (T3DVec3*)&cam->transform.loc,
        &cam->target,
		&(T3DVec3){{0.0f, 1.0f, 0.0f}}
	);
}

void renderer_update_objects(ArmScene *scene)
{
    for (uint16_t i = 0; i < scene->object_count; i++) {
        ArmObject *obj = &scene->objects[i];
        if (obj->transform.dirty == 0) {
            continue;
        }
        t3d_mat4fp_from_srt_euler(
            &obj->model_mat[frameIdx],
            obj->transform.scale,
            obj->transform.rot,
            obj->transform.loc
        );
        obj->transform.dirty--;
    }
}

void renderer_draw_scene(T3DViewport *viewport, ArmScene *scene)
{
    frameIdx = (frameIdx + 1) % FB_COUNT;
    renderer_update_objects(scene);

    // ======== Draw (3D) ======== //
    rdpq_attach(display_get(), display_get_zbuf());
    t3d_frame_start();
    t3d_viewport_attach(viewport);

    t3d_screen_clear_color(RGBA32(
        scene->world.clear_color[0],
        scene->world.clear_color[1],
        scene->world.clear_color[2],
        scene->world.clear_color[3]
    ));
    t3d_screen_clear_depth();

    t3d_state_set_drawflags(T3D_FLAG_DEPTH | T3D_FLAG_CULL_BACK);

    t3d_light_set_ambient(scene->world.ambient_color);
    t3d_light_set_count(scene->light_count);
    for (uint8_t i = 0; i < scene->light_count; i++) {
        ArmLight *l = &scene->lights[i];
        t3d_light_set_directional(i, l->color, &l->dir);
    }

    // TODO: Frustum culling - skip objects outside camera view
    // TODO: Sectors/portals - for indoor environments, only render visible rooms
    // These optimizations are essential for larger N64 games
    t3d_matrix_push_pos(1);
    for (uint16_t i = 0; i < scene->object_count; i++) {
        ArmObject *obj = &scene->objects[i];
        if (!obj->visible) {
            continue;
        }
        t3d_matrix_set(&obj->model_mat[frameIdx], true);
        rspq_block_run(obj->dpl);
    }
    t3d_matrix_pop(1);

    // ======== Draw (2D) ======== //
    rdpq_sync_pipe();
	// TODO: set to `renderer.c.j2` and enable/disable FPS debug via Blender
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 200, 220, "FPS: %.2f", display_get_fps());

    // Input debug
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 10, 10, "Stick: %.2f, %.2f", input_stick_x(), input_stick_y());
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 10, 20,
        "A:%d B:%d Z:%d Start:%d",
        input_down(N64_BTN_A), input_down(N64_BTN_B), input_down(N64_BTN_Z), input_down(N64_BTN_START));
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 10, 30,
        "D: %d%d%d%d  C: %d%d%d%d",
        input_down(N64_BTN_DUP), input_down(N64_BTN_DDOWN), input_down(N64_BTN_DLEFT), input_down(N64_BTN_DRIGHT),
        input_down(N64_BTN_CUP), input_down(N64_BTN_CDOWN), input_down(N64_BTN_CLEFT), input_down(N64_BTN_CRIGHT));
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 10, 40, "L:%d R:%d", input_down(N64_BTN_L), input_down(N64_BTN_R));

    rdpq_detach_show();
}
