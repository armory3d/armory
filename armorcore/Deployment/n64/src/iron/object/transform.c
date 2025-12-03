#include "transform.h"
#include "../../types.h"
#include <t3d/t3dmath.h>

void it_translate(ArmTransform *t, float x, float y, float z)
{
	t->loc.x += x;
	t->loc.y += y;
	t->loc.z += z;
	t->dirty = FB_COUNT;
}

void it_rotate_axis(ArmTransform *t, float ax, float ay, float az, float angle)
{
	float axis[3] = {ax, ay, az};
	t3d_quat_rotate_euler(&t->rot, axis, angle);
	t->dirty = FB_COUNT;
}

void it_rotate_axis_global(ArmTransform *t, float ax, float ay, float az, float angle)
{
	fm_vec3_t axis = {{ax, ay, az}};
	fm_quat_t axis_rot;
	fm_quat_from_axis_angle(&axis_rot, &axis, angle);

	fm_quat_t current = t->rot;
	fm_quat_mul(&t->rot, &axis_rot, &current);

	t->dirty = FB_COUNT;
}

void it_set_loc(ArmTransform *t, float x, float y, float z)
{
	t->loc.x = x;
	t->loc.y = y;
	t->loc.z = z;
	t->dirty = FB_COUNT;
}

void it_set_rot(ArmTransform *t, float x, float y, float z, float w)
{
	t->rot.x = x;
	t->rot.y = y;
	t->rot.z = z;
	t->rot.w = w;
	t->dirty = FB_COUNT;
}

void it_set_scale(ArmTransform *t, float x, float y, float z)
{
	t->scale.x = x;
	t->scale.y = y;
	t->scale.z = z;
	t->dirty = FB_COUNT;
}
