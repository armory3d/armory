#pragma once

#include "../types.h"
#include <t3d/t3d.h>

#ifdef __cplusplus
extern "C" {
#endif

void renderer_begin_frame(T3DViewport *viewport, Scene *scene);
void renderer_update_objects(Scene *scene);
void renderer_draw_scene(T3DViewport *viewport, Scene *scene);

#ifdef __cplusplus
}
#endif