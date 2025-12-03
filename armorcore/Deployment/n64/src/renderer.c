#include <stdint.h>
#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmath.h>
#include <t3d/t3dmodel.h>

#include "engine.h"
#include "types.h"
#include "utils.h"
#include "iron/system/input.h"

#if ENGINE_ENABLE_PHYSICS
#include "physics.h"
#if ENGINE_ENABLE_PHYSICS_DEBUG
#include "physics_debug.h"
#endif
#endif

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

        // Safety check: skip objects with invalid transform values to prevent FPU overflow
        if (!transform_is_safe(obj->transform.loc, obj->transform.scale)) {
            // Reset to origin if values are invalid (object fell off world, etc.)
            obj->transform.loc[0] = 0.0f;
            obj->transform.loc[1] = 0.0f;
            obj->transform.loc[2] = 0.0f;
            obj->visible = false;  // Hide the object
        }

        t3d_mat4fp_from_srt(
            &obj->model_mat[frameIdx],
            obj->transform.scale,
            obj->transform.rot,
            obj->transform.loc
        );

        // Decrement dirty counter (static objects will reach 0 and stay there)
        obj->transform.dirty--;
    }
}

void renderer_draw_scene(T3DViewport *viewport, ArmScene *scene)
{
    frameIdx = (frameIdx + 1) % FB_COUNT;
    renderer_update_objects(scene);

    // Get surface BEFORE rdpq_attach - we need this reference for debug drawing later
    surface_t *surface = display_get();
    rdpq_attach(surface, display_get_zbuf());
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

    const T3DFrustum *frustum = &viewport->viewFrustum;
    int visible_count = 0;
    int static_rendered = 0;

    // Render batched static objects if available
    if (scene->static_dpl) {
        rspq_block_run(scene->static_dpl);
        static_rendered = scene->static_count;
        visible_count += static_rendered;
    }

    // Render dynamic objects (and unbatched static objects if threshold not met)
    t3d_matrix_push_pos(1);
    for (uint16_t i = 0; i < scene->object_count; i++) {
        ArmObject *obj = &scene->objects[i];
        if (!obj->visible) {
            continue;
        }

        // Skip static objects if they were rendered via combined display list
        if (obj->is_static && scene->static_dpl) {
            continue;
        }

        T3DVec3 world_center = {{
            obj->transform.loc[0] + obj->bounds_center.v[0],
            obj->transform.loc[1] + obj->bounds_center.v[1],
            obj->transform.loc[2] + obj->bounds_center.v[2]
        }};

        float max_scale = obj->transform.scale[0];
        if (obj->transform.scale[1] > max_scale) max_scale = obj->transform.scale[1];
        if (obj->transform.scale[2] > max_scale) max_scale = obj->transform.scale[2];
        float world_radius = obj->bounds_radius * max_scale;

        if (!t3d_frustum_vs_sphere(frustum, &world_center, world_radius)) {
            continue;
        }

        visible_count++;
        t3d_matrix_set(&obj->model_mat[frameIdx], true);
        rspq_block_run(obj->dpl);
    }
    t3d_matrix_pop(1);

#ifdef ARM_DEBUG_HUD
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 200, 220, "FPS: %.2f", display_get_fps());
    rdpq_text_printf(NULL, FONT_BUILTIN_DEBUG_MONO, 200, 230, "Obj: %d/%d (S:%d)", visible_count, scene->object_count, scene->static_count);

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
#endif

    // Physics debug drawing after GPU work is complete
    {
        rdpq_detach_wait();

#if ENGINE_ENABLE_PHYSICS && ENGINE_ENABLE_PHYSICS_DEBUG
        physics_debug_draw(surface, viewport, physics_get_world());
#endif
        display_show(surface);
    }
}

void renderer_build_static_dpl(ArmScene *scene)
{
    // Count static objects
    uint16_t static_count = 0;
    for (uint16_t i = 0; i < scene->object_count; i++) {
        if (scene->objects[i].is_static && scene->objects[i].visible) {
            static_count++;
        }
    }
    scene->static_count = static_count;

    // Only batch if we have enough static objects to make it worthwhile
    if (static_count < STATIC_BATCH_THRESHOLD) {
        scene->static_dpl = NULL;
        return;
    }

    // Build combined display list for all static objects
    // Note: This must be called AFTER initial matrix computation (after first few frames)
    rspq_block_begin();
    t3d_matrix_push_pos(1);
    for (uint16_t i = 0; i < scene->object_count; i++) {
        ArmObject *obj = &scene->objects[i];
        if (!obj->is_static || !obj->visible) {
            continue;
        }
        // Use frame 0 matrix (all frames should be identical for static objects)
        t3d_matrix_set(&obj->model_mat[0], true);
        rspq_block_run(obj->dpl);
    }
    t3d_matrix_pop(1);
    scene->static_dpl = rspq_block_end();
}

void renderer_free_static_dpl(ArmScene *scene)
{
    if (scene->static_dpl) {
        rspq_block_free(scene->static_dpl);
        scene->static_dpl = NULL;
    }
    scene->static_count = 0;
}
