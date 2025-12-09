#pragma once

#include "types.h"
#include <t3d/t3d.h>

#ifdef __cplusplus
extern "C" {
#endif

void renderer_begin_frame(T3DViewport *viewport, ArmScene *scene);
void renderer_update_objects(ArmScene *scene);
void renderer_draw_scene(T3DViewport *viewport, ArmScene *scene);
void renderer_end_frame(T3DViewport *viewport);
void renderer_build_static_dpl(ArmScene *scene);
void renderer_free_static_dpl(ArmScene *scene);

#ifdef __cplusplus
}
#endif