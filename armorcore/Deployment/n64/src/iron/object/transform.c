#include "transform.h"

// FB_COUNT for triple buffering - matrix needs updating for all buffers
#define DIRTY_FRAMES 3

void it_translate(ArmTransform *t, float x, float y, float z)
{
	t->loc[0] += x;
	t->loc[1] += y;
	t->loc[2] += z;
	t->dirty = DIRTY_FRAMES;
}

void it_rotate(ArmTransform *t, float x, float y, float z)
{
	t->rot[0] += x;
	t->rot[1] += y;
	t->rot[2] += z;
	t->dirty = DIRTY_FRAMES;
}

void it_rotate_axis(ArmTransform *t, float ax, float ay, float az, float angle)
{
	// Simplified axis-angle rotation - apply to the dominant axis
	// For (0,0,1) this rotates around Z, for (0,1,0) around Y, etc.
	t->rot[0] += ax * angle;
	t->rot[1] += ay * angle;
	t->rot[2] += az * angle;
	t->dirty = DIRTY_FRAMES;
}

void it_set_loc(ArmTransform *t, float x, float y, float z)
{
	t->loc[0] = x;
	t->loc[1] = y;
	t->loc[2] = z;
	t->dirty = DIRTY_FRAMES;
}

void it_set_rot(ArmTransform *t, float x, float y, float z)
{
	t->rot[0] = x;
	t->rot[1] = y;
	t->rot[2] = z;
	t->dirty = DIRTY_FRAMES;
}

void it_set_scale(ArmTransform *t, float x, float y, float z)
{
	t->scale[0] = x;
	t->scale[1] = y;
	t->scale[2] = z;
	t->dirty = DIRTY_FRAMES;
}
