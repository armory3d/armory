#include "transform.h"
#include <t3d/t3dmath.h>

// FB_COUNT for triple buffering - matrix needs updating for all buffers
#define DIRTY_FRAMES 3

void it_translate(ArmTransform *t, float x, float y, float z)
{
	t->loc[0] += x;
	t->loc[1] += y;
	t->loc[2] += z;
	t->dirty = DIRTY_FRAMES;
}

void it_rotate_axis(ArmTransform *t, float ax, float ay, float az, float angle)
{
	// Local axis rotation: rot = rot * axis_rot
	float axis[3] = {ax, ay, az};
	t3d_quat_rotate_euler((T3DQuat*)t->rot, axis, angle);
	t->dirty = DIRTY_FRAMES;
}

void it_rotate_axis_global(ArmTransform *t, float ax, float ay, float az, float angle)
{
	// Global axis rotation: rot = axis_rot * rot
	// Build axis quaternion, then multiply in reverse order
	float axis[3] = {ax, ay, az};
	T3DQuat axis_rot;
	t3d_quat_from_rotation(&axis_rot, axis, angle);

	T3DQuat current = *(T3DQuat*)t->rot;
	t3d_quat_mul((T3DQuat*)t->rot, &axis_rot, &current);
	t->dirty = DIRTY_FRAMES;
}

void it_set_loc(ArmTransform *t, float x, float y, float z)
{
	t->loc[0] = x;
	t->loc[1] = y;
	t->loc[2] = z;
	t->dirty = DIRTY_FRAMES;
}

void it_set_rot(ArmTransform *t, float x, float y, float z, float w)
{
	t->rot[0] = x;
	t->rot[1] = y;
	t->rot[2] = z;
	t->rot[3] = w;
	t->dirty = DIRTY_FRAMES;
}

void it_set_scale(ArmTransform *t, float x, float y, float z)
{
	t->scale[0] = x;
	t->scale[1] = y;
	t->scale[2] = z;
	t->dirty = DIRTY_FRAMES;
}
