#include <stdint.h>
#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmodel.h>

#include "../types.h"

static int frameIdx = 0;

void renderer_begin_frame(T3DViewport *viewport, Scene *scene)
{
    frameIdx = (frameIdx + 1) % FB_COUNT;

    t3d_viewport_set_projection(
        viewport,
        T3D_DEG_TO_RAD(scene->camera.fov),
        scene->camera.near,
        scene->camera.far
    );

	t3d_viewport_look_at(
		viewport,
		&scene->camera.pos,
		&scene->camera.target,
		&(T3DVec3){{0.0f, 1.0f, 0.0f}}
	);
}

void renderer_update_objects(Scene *scene)
{
    for (int i = 0; i < scene->objectCount; i++) {
        ArmObject *obj = &scene->objects[i];
        t3d_mat4fp_from_srt_euler(
            &obj->modelMat[frameIdx],
            obj->scale,
            obj->rot,
            obj->pos
        );
    }
}

void renderer_draw_scene(T3DViewport *viewport, Scene *scene)
{
    (void)viewport;

    rdpq_attach(display_get(), display_get_zbuf());
    t3d_frame_start();
    t3d_viewport_attach(viewport);

    t3d_screen_clear_color(RGBA32(
        scene->world.clearColor[0],
        scene->world.clearColor[1],
        scene->world.clearColor[2],
        scene->world.clearColor[3]
    ));
    t3d_screen_clear_depth();

    t3d_light_set_ambient(scene->world.ambientColor);

    t3d_light_set_count(scene->lightCount);
    for (int i = 0; i < scene->lightCount; i++) {
        ArmLight *l = &scene->lights[i];
        t3d_light_set_directional(i, l->color, &l->dir);
    }

    for (int i = 0; i < scene->objectCount; i++) {
        ArmObject *obj = &scene->objects[i];
        t3d_matrix_push(&obj->modelMat[frameIdx]);
        t3d_model_draw(obj->model);
        t3d_matrix_pop(1);
    }

    rdpq_sync_pipe();
	// TODO: set to `renderer.c.j2` and enable/disable FPS debug via Blender
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 200, 220,
        "FPS   : %.2f", display_get_fps());

    rdpq_detach_show();
}
