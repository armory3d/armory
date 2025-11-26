#pragma once

#include "../../types.h"

#ifdef __cplusplus
extern "C" {
#endif

void it_translate(ArmTransform *t, float x, float y, float z);
void it_rotate(ArmTransform *t, float x, float y, float z);
void it_set_loc(ArmTransform *t, float x, float y, float z);
void it_set_rot(ArmTransform *t, float x, float y, float z);
void it_set_scale(ArmTransform *t, float x, float y, float z);

#ifdef __cplusplus
}
#endif
