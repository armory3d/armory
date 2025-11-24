#pragma once

#include "types.h"

#ifdef __cplusplus
extern "C" {
#endif

void object_on_ready(ArmObject *obj);
void object_on_update(ArmObject *obj, float dt);
void object_on_remove(ArmObject *obj);

#ifdef __cplusplus
}
#endif
