#ifndef _AABB_GLSL
#define _AABB_GLSL

bool IntersectAABB(vec3[2] a, vec3[2] b) {
    const float EPSILON = 0.001; // Small tolerance to prevent false negatives
    if (abs(a[0].x - b[0].x) > (a[1].x + b[1].x + EPSILON)) return false;
    if (abs(a[0].y - b[0].y) > (a[1].y + b[1].y + EPSILON)) return false;
    if (abs(a[0].z - b[0].z) > (a[1].z + b[1].z + EPSILON)) return false;
    return true;
}

void AABBfromMinMax(inout vec3[2] aabb, vec3 _min, vec3 _max)
{
	aabb[0] = (_min + _max) * 0.5f;
	aabb[1] = abs(_max - aabb[0]);
}

#endif
