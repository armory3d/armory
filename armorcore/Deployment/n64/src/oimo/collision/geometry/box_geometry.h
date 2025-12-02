#ifndef OIMO_COLLISION_GEOMETRY_BOX_GEOMETRY_H
#define OIMO_COLLISION_GEOMETRY_BOX_GEOMETRY_H

#include "../../common/setting.h"
#include "../../common/math_util.h"
#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/transform.h"
#include "geometry_type.h"
#include "aabb.h"
#include "geometry.h"

typedef struct OimoBoxGeometry {
    OimoGeometry base;
    OimoVec3 half_extents;
} OimoBoxGeometry;

static inline void oimo_box_geometry_init(OimoBoxGeometry* box, const OimoVec3* half_extents) {
    oimo_geometry_init(&box->base, OIMO_GEOMETRY_BOX);
    box->half_extents = oimo_vec3_copy(half_extents);

    OimoScalar w = half_extents->x;
    OimoScalar h = half_extents->y;
    OimoScalar d = half_extents->z;

    // Compute volume: V = 8 * w * h * d
    box->base.volume = 8.0f * w * h * d;

    // Compute inertia coefficient: I/m for a box
    // Ixx/m = (1/3) * (h^2 + d^2)
    // Iyy/m = (1/3) * (w^2 + d^2)
    // Izz/m = (1/3) * (w^2 + h^2)
    OimoScalar w2 = w * w;
    OimoScalar h2 = h * h;
    OimoScalar d2 = d * d;

    box->base.inertia_coeff = oimo_mat3(
        (1.0f / 3.0f) * (h2 + d2), 0, 0,
        0, (1.0f / 3.0f) * (w2 + d2), 0,
        0, 0, (1.0f / 3.0f) * (w2 + h2)
    );
}

// Initialize box geometry with components
static inline void oimo_box_geometry_init3(OimoBoxGeometry* box, OimoScalar hw, OimoScalar hh, OimoScalar hd) {
    OimoVec3 half_ext = oimo_vec3(hw, hh, hd);
    oimo_box_geometry_init(box, &half_ext);
}

// Create box geometry (returns by value)
static inline OimoBoxGeometry oimo_box_geometry(const OimoVec3* half_extents) {
    OimoBoxGeometry box;
    oimo_box_geometry_init(&box, half_extents);
    return box;
}

// Create box geometry with components
static inline OimoBoxGeometry oimo_box_geometry3(OimoScalar hw, OimoScalar hh, OimoScalar hd) {
    OimoVec3 half_ext = oimo_vec3(hw, hh, hd);
    return oimo_box_geometry(&half_ext);
}

// Get half-extents
static inline OimoVec3 oimo_box_geometry_get_half_extents(const OimoBoxGeometry* box) {
    return oimo_vec3_copy(&box->half_extents);
}

// Get width (full width = 2 * half_extents.x)
static inline OimoScalar oimo_box_geometry_get_width(const OimoBoxGeometry* box) {
    return 2.0f * box->half_extents.x;
}

// Get height (full height = 2 * half_extents.y)
static inline OimoScalar oimo_box_geometry_get_height(const OimoBoxGeometry* box) {
    return 2.0f * box->half_extents.y;
}

// Get depth (full depth = 2 * half_extents.z)
static inline OimoScalar oimo_box_geometry_get_depth(const OimoBoxGeometry* box) {
    return 2.0f * box->half_extents.z;
}

// Set half-extents and update mass properties
static inline void oimo_box_geometry_set_half_extents(OimoBoxGeometry* box, const OimoVec3* half_extents) {
    box->half_extents = oimo_vec3_copy(half_extents);

    OimoScalar w = half_extents->x;
    OimoScalar h = half_extents->y;
    OimoScalar d = half_extents->z;

    // Update volume
    box->base.volume = 8.0f * w * h * d;

    // Update inertia coefficient
    OimoScalar w2 = w * w;
    OimoScalar h2 = h * h;
    OimoScalar d2 = d * d;

    box->base.inertia_coeff = oimo_mat3(
        (1.0f / 3.0f) * (h2 + d2), 0, 0,
        0, (1.0f / 3.0f) * (w2 + d2), 0,
        0, 0, (1.0f / 3.0f) * (w2 + h2)
    );
}

// Compute AABB for box at given transform
static inline void oimo_box_geometry_compute_aabb(
    const OimoBoxGeometry* box,
    OimoAabb* aabb,
    const OimoTransform* tf
) {
    // Transform each half-axis and take absolute values
    OimoVec3 half_x = oimo_vec3(box->half_extents.x, 0, 0);
    OimoVec3 half_y = oimo_vec3(0, box->half_extents.y, 0);
    OimoVec3 half_z = oimo_vec3(0, 0, box->half_extents.z);

    // Rotate each half-axis
    OimoVec3 tfx = oimo_mat3_mul_vec3(&tf->rotation, half_x);
    OimoVec3 tfy = oimo_mat3_mul_vec3(&tf->rotation, half_y);
    OimoVec3 tfz = oimo_mat3_mul_vec3(&tf->rotation, half_z);

    // Take absolute values
    tfx.x = oimo_abs(tfx.x); tfx.y = oimo_abs(tfx.y); tfx.z = oimo_abs(tfx.z);
    tfy.x = oimo_abs(tfy.x); tfy.y = oimo_abs(tfy.y); tfy.z = oimo_abs(tfy.z);
    tfz.x = oimo_abs(tfz.x); tfz.y = oimo_abs(tfz.y); tfz.z = oimo_abs(tfz.z);

    // Sum up the contributions
    OimoVec3 extent;
    extent.x = tfx.x + tfy.x + tfz.x;
    extent.y = tfx.y + tfy.y + tfz.y;
    extent.z = tfx.z + tfy.z + tfz.z;

    // AABB = position ± extent
    aabb->min = oimo_vec3_sub(tf->position, extent);
    aabb->max = oimo_vec3_add(tf->position, extent);
}

// Ray cast against box in local coordinates (slab method)
static inline int oimo_box_geometry_ray_cast_local(
    const OimoBoxGeometry* box,
    const OimoVec3* begin,
    const OimoVec3* end,
    OimoRayCastHit* hit
) {
    OimoScalar p1x = begin->x, p1y = begin->y, p1z = begin->z;
    OimoScalar p2x = end->x, p2y = end->y, p2z = end->z;
    OimoScalar hw = box->half_extents.x;
    OimoScalar hh = box->half_extents.y;
    OimoScalar hd = box->half_extents.z;

    OimoScalar dx = p2x - p1x;
    OimoScalar dy = p2y - p1y;
    OimoScalar dz = p2z - p1z;

    OimoScalar tminx = 0, tminy = 0, tminz = 0;
    OimoScalar tmaxx = 1, tmaxy = 1, tmaxz = 1;

    // X axis slab
    if (dx > -OIMO_EPSILON && dx < OIMO_EPSILON) {
        if (p1x <= -hw || p1x >= hw) return 0;
    } else {
        OimoScalar inv_dx = 1.0f / dx;
        OimoScalar t1 = (-hw - p1x) * inv_dx;
        OimoScalar t2 = (hw - p1x) * inv_dx;
        if (t1 > t2) { OimoScalar tmp = t1; t1 = t2; t2 = tmp; }
        if (t1 > 0) tminx = t1;
        if (t2 < 1) tmaxx = t2;
    }

    // Y axis slab
    if (dy > -OIMO_EPSILON && dy < OIMO_EPSILON) {
        if (p1y <= -hh || p1y >= hh) return 0;
    } else {
        OimoScalar inv_dy = 1.0f / dy;
        OimoScalar t1 = (-hh - p1y) * inv_dy;
        OimoScalar t2 = (hh - p1y) * inv_dy;
        if (t1 > t2) { OimoScalar tmp = t1; t1 = t2; t2 = tmp; }
        if (t1 > 0) tminy = t1;
        if (t2 < 1) tmaxy = t2;
    }

    // Z axis slab
    if (dz > -OIMO_EPSILON && dz < OIMO_EPSILON) {
        if (p1z <= -hd || p1z >= hd) return 0;
    } else {
        OimoScalar inv_dz = 1.0f / dz;
        OimoScalar t1 = (-hd - p1z) * inv_dz;
        OimoScalar t2 = (hd - p1z) * inv_dz;
        if (t1 > t2) { OimoScalar tmp = t1; t1 = t2; t2 = tmp; }
        if (t1 > 0) tminz = t1;
        if (t2 < 1) tmaxz = t2;
    }

    // Check for no intersection
    if (tminx >= 1 || tminy >= 1 || tminz >= 1 ||
        tmaxx <= 0 || tmaxy <= 0 || tmaxz <= 0) return 0;

    // Find the actual intersection interval
    OimoScalar tmin = tminx;
    OimoScalar tmax = tmaxx;
    int hit_axis = 0;  // 0=X, 1=Y, 2=Z

    if (tminy > tmin) { tmin = tminy; hit_axis = 1; }
    if (tminz > tmin) { tmin = tminz; hit_axis = 2; }
    if (tmaxy < tmax) tmax = tmaxy;
    if (tmaxz < tmax) tmax = tmaxz;

    // No valid intersection
    if (tmin > tmax) return 0;
    if (tmin <= OIMO_EPSILON) return 0;  // Ray starts inside

    // Compute hit position
    hit->position.x = p1x + dx * tmin;
    hit->position.y = p1y + dy * tmin;
    hit->position.z = p1z + dz * tmin;
    hit->fraction = tmin;

    // Compute hit normal based on which face was hit
    switch (hit_axis) {
        case 0:  // X face
            hit->normal = oimo_vec3(dx > 0 ? -1.0f : 1.0f, 0, 0);
            break;
        case 1:  // Y face
            hit->normal = oimo_vec3(0, dy > 0 ? -1.0f : 1.0f, 0);
            break;
        case 2:  // Z face
            hit->normal = oimo_vec3(0, 0, dz > 0 ? -1.0f : 1.0f);
            break;
    }

    return 1;
}

// Ray cast against box at given transform (world coordinates)
static inline int oimo_box_geometry_ray_cast(
    const OimoBoxGeometry* box,
    const OimoVec3* begin,
    const OimoVec3* end,
    const OimoTransform* tf,
    OimoRayCastHit* hit
) {
    // Transform ray to local space
    OimoVec3 local_begin = oimo_transform_inv_point(tf, begin);
    OimoVec3 local_end = oimo_transform_inv_point(tf, end);

    // Perform ray cast in local space
    if (!oimo_box_geometry_ray_cast_local(box, &local_begin, &local_end, hit)) {
        return 0;
    }

    // Transform result back to world space
    hit->position = oimo_transform_point(tf, &hit->position);
    hit->normal = oimo_transform_vector(tf, &hit->normal);

    return 1;
}

// Compute local supporting vertex in given direction
static inline OimoVec3 oimo_box_geometry_support_local(
    const OimoBoxGeometry* box,
    const OimoVec3* dir
) {
    return oimo_vec3(
        dir->x > 0 ? box->half_extents.x : -box->half_extents.x,
        dir->y > 0 ? box->half_extents.y : -box->half_extents.y,
        dir->z > 0 ? box->half_extents.z : -box->half_extents.z
    );
}

// Get box vertex by index (0-7)
// Vertices are ordered: (-,-,-), (+,-,-), (-,+,-), (+,+,-), (-,-,+), (+,-,+), (-,+,+), (+,+,+)
static inline OimoVec3 oimo_box_geometry_get_vertex(const OimoBoxGeometry* box, int index) {
    OimoScalar sx = (index & 1) ? box->half_extents.x : -box->half_extents.x;
    OimoScalar sy = (index & 2) ? box->half_extents.y : -box->half_extents.y;
    OimoScalar sz = (index & 4) ? box->half_extents.z : -box->half_extents.z;
    return oimo_vec3(sx, sy, sz);
}

// Get box vertex transformed by given transform
static inline OimoVec3 oimo_box_geometry_get_vertex_world(
    const OimoBoxGeometry* box,
    int index,
    const OimoTransform* tf
) {
    OimoVec3 local = oimo_box_geometry_get_vertex(box, index);
    return oimo_transform_point(tf, &local);
}

#endif // OIMO_COLLISION_GEOMETRY_BOX_GEOMETRY_H
