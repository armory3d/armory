#pragma once

#include "../types.h"

#ifdef __cplusplus
extern "C" {
#endif

void translate(ArmTransform *t, float x, float y, float z);
void rotate(ArmTransform *t, float x, float y, float z);
void set_loc(ArmTransform *t, float x, float y, float z);
void set_rot(ArmTransform *t, float x, float y, float z);
void set_scale(ArmTransform *t, float x, float y, float z);

#define TRANSFORM(entity) (&(entity)->transform)

#ifdef __cplusplus
}
#endif
