#pragma once

#include "types.h"

#ifdef __cplusplus
extern "C" {
#endif

void light_on_ready(ArmLight *light);
void light_on_update(ArmLight *light, float dt);
void light_on_remove(ArmLight *light);

#ifdef __cplusplus
}
#endif
