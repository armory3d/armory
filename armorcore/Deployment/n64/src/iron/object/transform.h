#pragma once

#include "../../types.h"

#ifdef __cplusplus
extern "C" {
#endif

// Transform manipulation
void it_translate(ArmTransform *t, float x, float y, float z);
void it_move(ArmTransform *t, float dx, float dy, float dz, float scale);
void it_rotate_axis(ArmTransform *t, float ax, float ay, float az, float angle);
void it_rotate_axis_global(ArmTransform *t, float ax, float ay, float az, float angle);

// Setters
void it_set_loc(ArmTransform *t, float x, float y, float z);
void it_set_rot(ArmTransform *t, float x, float y, float z, float w);
void it_set_rot_euler(ArmTransform *t, float x, float y, float z);
void it_set_scale(ArmTransform *t, float x, float y, float z);
void it_reset(ArmTransform *t);

// Direction vectors (returns in provided out vector)
void it_look(const ArmTransform *t, T3DVec3 *out);
void it_right(const ArmTransform *t, T3DVec3 *out);
void it_up(const ArmTransform *t, T3DVec3 *out);

// World position getters
static inline float it_world_x(const ArmTransform *t) { return t->loc.x; }
static inline float it_world_y(const ArmTransform *t) { return t->loc.y; }
static inline float it_world_z(const ArmTransform *t) { return t->loc.z; }

#ifdef __cplusplus
}
#endif
