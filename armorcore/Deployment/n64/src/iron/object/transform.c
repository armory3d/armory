#include "transform.h"
#include "../../types.h"
#include <t3d/t3dmath.h>
#include <math.h>

void it_translate(ArmTransform *t, float x, float y, float z)
{
	t->loc.x += x;
	t->loc.y += y;
	t->loc.z += z;
	t->dirty = FB_COUNT;
}

void it_move(ArmTransform *t, float dx, float dy, float dz, float scale)
{
	t->loc.x += dx * scale;
	t->loc.y += dy * scale;
	t->loc.z += dz * scale;
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

void it_set_rot_euler(ArmTransform *t, float x, float y, float z)
{
	// Convert Euler angles (radians) to quaternion
	float cx = cosf(x * 0.5f), sx = sinf(x * 0.5f);
	float cy = cosf(y * 0.5f), sy = sinf(y * 0.5f);
	float cz = cosf(z * 0.5f), sz = sinf(z * 0.5f);

	t->rot.w = cx * cy * cz + sx * sy * sz;
	t->rot.x = sx * cy * cz - cx * sy * sz;
	t->rot.y = cx * sy * cz + sx * cy * sz;
	t->rot.z = cx * cy * sz - sx * sy * cz;
	t->dirty = FB_COUNT;
}

void it_set_scale(ArmTransform *t, float x, float y, float z)
{
	t->scale.x = x;
	t->scale.y = y;
	t->scale.z = z;
	t->dirty = FB_COUNT;
}

void it_reset(ArmTransform *t)
{
	t->loc.v[0] = 0.0f; t->loc.v[1] = 0.0f; t->loc.v[2] = 0.0f;
	t->rot.x = 0.0f; t->rot.y = 0.0f; t->rot.z = 0.0f; t->rot.w = 1.0f;
	t->scale.v[0] = 1.0f; t->scale.v[1] = 1.0f; t->scale.v[2] = 1.0f;
	t->dirty = FB_COUNT;
}

void it_look(const ArmTransform *t, T3DVec3 *out)
{
	// Forward direction from quaternion (local +Y rotated by quaternion)
	const T3DQuat *q = &t->rot;
	out->v[0] = 2.0f * (q->x * q->y + q->w * q->z);
	out->v[1] = 1.0f - 2.0f * (q->x * q->x + q->z * q->z);
	out->v[2] = 2.0f * (q->y * q->z - q->w * q->x);
}

void it_right(const ArmTransform *t, T3DVec3 *out)
{
	// Right direction from quaternion (local +X rotated by quaternion)
	const T3DQuat *q = &t->rot;
	out->v[0] = 1.0f - 2.0f * (q->y * q->y + q->z * q->z);
	out->v[1] = 2.0f * (q->x * q->y - q->w * q->z);
	out->v[2] = 2.0f * (q->x * q->z + q->w * q->y);
}

void it_up(const ArmTransform *t, T3DVec3 *out)
{
	// Up direction from quaternion (local +Z rotated by quaternion)
	const T3DQuat *q = &t->rot;
	out->v[0] = 2.0f * (q->x * q->z - q->w * q->y);
	out->v[1] = 2.0f * (q->y * q->z + q->w * q->x);
	out->v[2] = 1.0f - 2.0f * (q->x * q->x + q->y * q->y);
}
