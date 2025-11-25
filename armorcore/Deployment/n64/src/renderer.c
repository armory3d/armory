#include <stdint.h>
#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmodel.h>

#include "types.h"

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
        &cam->pos,
        &cam->target,
		&(T3DVec3){{0.0f, 1.0f, 0.0f}}
	);
}

void renderer_update_objects(ArmScene *scene)
{
    for (uint16_t i = 0; i < scene->object_count; i++) {
        ArmObject *obj = &scene->objects[i];
        t3d_mat4fp_from_srt_euler(
            &obj->model_mat[frameIdx],
            obj->scale,
            obj->rot,
            obj->pos
        );
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

    t3d_matrix_push_pos(1);
    for (uint16_t i = 0; i < scene->object_count; i++) {
        ArmObject *obj = &scene->objects[i];
        t3d_matrix_set(&obj->model_mat[frameIdx], true);
        rspq_block_run(obj->dpl);
    }
    t3d_matrix_pop(1);

    // ======== Draw (2D) ======== //
    rdpq_sync_pipe();
	// TODO: set to `renderer.c.j2` and enable/disable FPS debug via Blender
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 200, 220, "FPS   : %.2f", display_get_fps());
	rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 10, 10, "objects: %u", scene->object_count);

    rdpq_detach_show();
}
