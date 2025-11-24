#pragma once

#include "types.h"

#ifdef __cplusplus
extern "C" {
#endif

void camera_on_ready(ArmCamera *camera);
void camera_on_update(ArmCamera *camera, float dt);
void camera_on_remove(ArmCamera *camera);

#ifdef __cplusplus
}
#endif
