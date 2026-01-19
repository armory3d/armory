#pragma once

#include "../../common/setting.h"
#include "../../common/vec3.h"

typedef struct OimoAabb {
    OimoVec3 min;  // Minimum corner
    OimoVec3 max;  // Maximum corner
} OimoAabb;

// Create empty AABB (both corners at zero)
static inline OimoAabb oimo_aabb_zero(void) {
    OimoAabb aabb;
    aabb.min = oimo_vec3_zero();
    aabb.max = oimo_vec3_zero();
    return aabb;
}

// Create AABB from min/max corners
static inline OimoAabb oimo_aabb(const OimoVec3* min, const OimoVec3* max) {
    OimoAabb aabb;
    aabb.min = oimo_vec3_copy(min);
    aabb.max = oimo_vec3_copy(max);
    return aabb;
}

// Create AABB from center and half-extents
static inline OimoAabb oimo_aabb_from_center_extents(const OimoVec3* center, const OimoVec3* half_extents) {
    OimoAabb aabb;
    oimo_vec3_sub_to(&aabb.min, center, half_extents);
    oimo_vec3_add_to(&aabb.max, center, half_extents);
    return aabb;
}

// Copy AABB
static inline OimoAabb oimo_aabb_copy(const OimoAabb* aabb) {
    OimoAabb result;
    result.min = oimo_vec3_copy(&aabb->min);
    result.max = oimo_vec3_copy(&aabb->max);
    return result;
}

// Get center of AABB: (min + max) / 2
static inline OimoVec3 oimo_aabb_get_center(const OimoAabb* aabb) {
    OimoVec3 center = oimo_vec3_add(aabb->min, aabb->max);
    return oimo_vec3_scale(center, 0.5f);
}

// Get half-extents of AABB: (max - min) / 2
static inline OimoVec3 oimo_aabb_get_extents(const OimoAabb* aabb) {
    OimoVec3 extents = oimo_vec3_sub(aabb->max, aabb->min);
    return oimo_vec3_scale(extents, 0.5f);
}

// Get size (full extents) of AABB: max - min
static inline OimoVec3 oimo_aabb_get_size(const OimoAabb* aabb) {
    return oimo_vec3_sub(aabb->max, aabb->min);
}

// Get surface area: 2 * (w*h + h*d + d*w)
static inline OimoScalar oimo_aabb_get_surface_area(const OimoAabb* aabb) {
    OimoVec3 size = oimo_aabb_get_size(aabb);
    return 2.0f * (size.x * size.y + size.y * size.z + size.z * size.x);
}

// Get volume: w * h * d
static inline OimoScalar oimo_aabb_get_volume(const OimoAabb* aabb) {
    OimoVec3 size = oimo_aabb_get_size(aabb);
    return size.x * size.y * size.z;
}

// Set min corner
static inline void oimo_aabb_set_min(OimoAabb* aabb, const OimoVec3* min) {
    oimo_vec3_copy_to(&aabb->min, min);
}

// Set max corner
static inline void oimo_aabb_set_max(OimoAabb* aabb, const OimoVec3* max) {
    oimo_vec3_copy_to(&aabb->max, max);
}

// Set both corners
static inline void oimo_aabb_set(OimoAabb* aabb, const OimoVec3* min, const OimoVec3* max) {
    oimo_vec3_copy_to(&aabb->min, min);
    oimo_vec3_copy_to(&aabb->max, max);
}

// Copy from another AABB
static inline void oimo_aabb_copy_to(OimoAabb* dst, const OimoAabb* src) {
    oimo_vec3_copy_to(&dst->min, &src->min);
    oimo_vec3_copy_to(&dst->max, &src->max);
}

// Check if two AABBs overlap
static inline int oimo_aabb_overlap(const OimoAabb* a, const OimoAabb* b) {
    // AABBs overlap if they overlap on all three axes
    return (a->min.x <= b->max.x && a->max.x >= b->min.x) &&
           (a->min.y <= b->max.y && a->max.y >= b->min.y) &&
           (a->min.z <= b->max.z && a->max.z >= b->min.z);
}

// Check if point is inside AABB
static inline int oimo_aabb_contains_point(const OimoAabb* aabb, const OimoVec3* point) {
    return (point->x >= aabb->min.x && point->x <= aabb->max.x) &&
           (point->y >= aabb->min.y && point->y <= aabb->max.y) &&
           (point->z >= aabb->min.z && point->z <= aabb->max.z);
}

// Check if AABB a contains AABB b entirely
static inline int oimo_aabb_contains(const OimoAabb* a, const OimoAabb* b) {
    return (a->min.x <= b->min.x && a->max.x >= b->max.x) &&
           (a->min.y <= b->min.y && a->max.y >= b->max.y) &&
           (a->min.z <= b->min.z && a->max.z >= b->max.z);
}

// Combine two AABBs into one that contains both
static inline OimoAabb oimo_aabb_combine(const OimoAabb* a, const OimoAabb* b) {
    OimoAabb result;
    result.min.x = oimo_min(a->min.x, b->min.x);
    result.min.y = oimo_min(a->min.y, b->min.y);
    result.min.z = oimo_min(a->min.z, b->min.z);
    result.max.x = oimo_max(a->max.x, b->max.x);
    result.max.y = oimo_max(a->max.y, b->max.y);
    result.max.z = oimo_max(a->max.z, b->max.z);
    return result;
}

// Combine AABB b into a (modify a in-place)
static inline void oimo_aabb_combine_eq(OimoAabb* a, const OimoAabb* b) {
    a->min.x = oimo_min(a->min.x, b->min.x);
    a->min.y = oimo_min(a->min.y, b->min.y);
    a->min.z = oimo_min(a->min.z, b->min.z);
    a->max.x = oimo_max(a->max.x, b->max.x);
    a->max.y = oimo_max(a->max.y, b->max.y);
    a->max.z = oimo_max(a->max.z, b->max.z);
}

// Expand AABB to include point
static inline void oimo_aabb_include_point(OimoAabb* aabb, const OimoVec3* point) {
    aabb->min.x = oimo_min(aabb->min.x, point->x);
    aabb->min.y = oimo_min(aabb->min.y, point->y);
    aabb->min.z = oimo_min(aabb->min.z, point->z);
    aabb->max.x = oimo_max(aabb->max.x, point->x);
    aabb->max.y = oimo_max(aabb->max.y, point->y);
    aabb->max.z = oimo_max(aabb->max.z, point->z);
}

// Get intersection of two AABBs (result may be invalid if they don't overlap)
static inline OimoAabb oimo_aabb_intersection(const OimoAabb* a, const OimoAabb* b) {
    OimoAabb result;
    result.min.x = oimo_max(a->min.x, b->min.x);
    result.min.y = oimo_max(a->min.y, b->min.y);
    result.min.z = oimo_max(a->min.z, b->min.z);
    result.max.x = oimo_min(a->max.x, b->max.x);
    result.max.y = oimo_min(a->max.y, b->max.y);
    result.max.z = oimo_min(a->max.z, b->max.z);
    return result;
}

// Check if intersection is valid (min <= max on all axes)
static inline int oimo_aabb_is_valid(const OimoAabb* aabb) {
    return (aabb->min.x <= aabb->max.x) &&
           (aabb->min.y <= aabb->max.y) &&
           (aabb->min.z <= aabb->max.z);
}

// Expand AABB by margin on all sides
static inline OimoAabb oimo_aabb_expand(const OimoAabb* aabb, OimoScalar margin) {
    OimoAabb result;
    result.min.x = aabb->min.x - margin;
    result.min.y = aabb->min.y - margin;
    result.min.z = aabb->min.z - margin;
    result.max.x = aabb->max.x + margin;
    result.max.y = aabb->max.y + margin;
    result.max.z = aabb->max.z + margin;
    return result;
}

// Expand AABB in-place
static inline void oimo_aabb_expand_eq(OimoAabb* aabb, OimoScalar margin) {
    aabb->min.x -= margin;
    aabb->min.y -= margin;
    aabb->min.z -= margin;
    aabb->max.x += margin;
    aabb->max.y += margin;
    aabb->max.z += margin;
}

// Ray-AABB intersection test
// Returns 1 if ray intersects, 0 otherwise
// t_near and t_far are set to the intersection parameters (0 <= t_near <= t_far <= 1 for hit)
static inline int oimo_aabb_ray_cast(
    const OimoAabb* aabb,
    const OimoVec3* ray_origin,
    const OimoVec3* ray_dir,    // Direction (end - origin)
    OimoScalar* t_near,
    OimoScalar* t_far
) {
    OimoScalar tmin = 0.0f;
    OimoScalar tmax = 1.0f;

    // X axis
    if (oimo_abs(ray_dir->x) < OIMO_EPSILON) {
        if (ray_origin->x < aabb->min.x || ray_origin->x > aabb->max.x) {
            return 0;
        }
    } else {
        OimoScalar inv_d = 1.0f / ray_dir->x;
        OimoScalar t1 = (aabb->min.x - ray_origin->x) * inv_d;
        OimoScalar t2 = (aabb->max.x - ray_origin->x) * inv_d;
        if (t1 > t2) { OimoScalar tmp = t1; t1 = t2; t2 = tmp; }
        if (t1 > tmin) tmin = t1;
        if (t2 < tmax) tmax = t2;
        if (tmin > tmax) return 0;
    }

    // Y axis
    if (oimo_abs(ray_dir->y) < OIMO_EPSILON) {
        if (ray_origin->y < aabb->min.y || ray_origin->y > aabb->max.y) {
            return 0;
        }
    } else {
        OimoScalar inv_d = 1.0f / ray_dir->y;
        OimoScalar t1 = (aabb->min.y - ray_origin->y) * inv_d;
        OimoScalar t2 = (aabb->max.y - ray_origin->y) * inv_d;
        if (t1 > t2) { OimoScalar tmp = t1; t1 = t2; t2 = tmp; }
        if (t1 > tmin) tmin = t1;
        if (t2 < tmax) tmax = t2;
        if (tmin > tmax) return 0;
    }

    // Z axis
    if (oimo_abs(ray_dir->z) < OIMO_EPSILON) {
        if (ray_origin->z < aabb->min.z || ray_origin->z > aabb->max.z) {
            return 0;
        }
    } else {
        OimoScalar inv_d = 1.0f / ray_dir->z;
        OimoScalar t1 = (aabb->min.z - ray_origin->z) * inv_d;
        OimoScalar t2 = (aabb->max.z - ray_origin->z) * inv_d;
        if (t1 > t2) { OimoScalar tmp = t1; t1 = t2; t2 = tmp; }
        if (t1 > tmin) tmin = t1;
        if (t2 < tmax) tmax = t2;
        if (tmin > tmax) return 0;
    }

    *t_near = tmin;
    *t_far = tmax;
    return 1;
}

// Initialize AABB to "empty" state (inverted bounds for expansion)
static inline void oimo_aabb_init(OimoAabb* aabb) {
    aabb->min.x = 1e30f;
    aabb->min.y = 1e30f;
    aabb->min.z = 1e30f;
    aabb->max.x = -1e30f;
    aabb->max.y = -1e30f;
    aabb->max.z = -1e30f;
}

// Merge AABB b into result (result = union of result and b)
static inline void oimo_aabb_merge(OimoAabb* result, const OimoAabb* a, const OimoAabb* b) {
    result->min.x = oimo_min(a->min.x, b->min.x);
    result->min.y = oimo_min(a->min.y, b->min.y);
    result->min.z = oimo_min(a->min.z, b->min.z);
    result->max.x = oimo_max(a->max.x, b->max.x);
    result->max.y = oimo_max(a->max.y, b->max.y);
    result->max.z = oimo_max(a->max.z, b->max.z);
}

