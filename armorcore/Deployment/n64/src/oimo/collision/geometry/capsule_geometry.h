#pragma once

#include "../../common/setting.h"
#include "../../common/math_util.h"
#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/transform.h"
#include "geometry_type.h"
#include "aabb.h"
#include "geometry.h"

// Capsule geometry: a cylinder with hemispherical caps
// Aligned along Y axis by default (same as OimoPhysics)
typedef struct OimoCapsuleGeometry {
    OimoGeometry base;
    OimoScalar radius;
    OimoScalar halfHeight;  // Half of the cylinder portion (not including caps)
} OimoCapsuleGeometry;

static inline void oimo_capsule_geometry_init(OimoCapsuleGeometry* capsule, OimoScalar radius, OimoScalar halfHeight) {
    oimo_geometry_init(&capsule->base, OIMO_GEOMETRY_CAPSULE);
    capsule->radius = radius;
    capsule->halfHeight = halfHeight;

    OimoScalar r = radius;
    OimoScalar hh = halfHeight;
    OimoScalar r2 = r * r;
    OimoScalar hh2 = hh * hh;

    // Volume calculation (matches OimoPhysics exactly)
    // cylinderVolume = 2*PI * r^2 * halfHeight
    // sphereVolume = (4/3) * PI * r^3
    OimoScalar cylinderVolume = OIMO_TWO_PI * r2 * hh;
    OimoScalar sphereVolume = OIMO_PI * r2 * r * (4.0f / 3.0f);
    capsule->base.volume = cylinderVolume + sphereVolume;

    // Inertia coefficient calculation (matches OimoPhysics)
    // These are I/m values (inertia divided by mass)
    OimoScalar invVolume = (oimo_abs(capsule->base.volume) <= OIMO_EPSILON) ? 0.0f : (1.0f / capsule->base.volume);

    // Iyy: rotation around the capsule's long axis (Y)
    OimoScalar inertiaY = invVolume * (
        cylinderVolume * r2 * 0.5f +
        sphereVolume * r2 * 0.4f
    );

    // Ixx = Izz: rotation perpendicular to the capsule's long axis
    OimoScalar inertiaXZ = invVolume * (
        cylinderVolume * (r2 * 0.25f + hh2 / 3.0f) +
        sphereVolume * (r2 * 0.4f + hh * r * 0.75f + hh2)
    );

    capsule->base.inertia_coeff = oimo_mat3(
        inertiaXZ, 0, 0,
        0, inertiaY, 0,
        0, 0, inertiaXZ
    );
}

// Create capsule geometry (returns by value)
static inline OimoCapsuleGeometry oimo_capsule_geometry(OimoScalar radius, OimoScalar halfHeight) {
    OimoCapsuleGeometry capsule;
    oimo_capsule_geometry_init(&capsule, radius, halfHeight);
    return capsule;
}

// Get radius
static inline OimoScalar oimo_capsule_geometry_get_radius(const OimoCapsuleGeometry* capsule) {
    return capsule->radius;
}

// Get half height
static inline OimoScalar oimo_capsule_geometry_get_half_height(const OimoCapsuleGeometry* capsule) {
    return capsule->halfHeight;
}

// Get total height (cylinder + 2*radius for caps)
static inline OimoScalar oimo_capsule_geometry_get_total_height(const OimoCapsuleGeometry* capsule) {
    return 2.0f * (capsule->halfHeight + capsule->radius);
}

// Compute AABB for capsule at given transform (matches OimoPhysics)
static inline void oimo_capsule_geometry_compute_aabb(
    const OimoCapsuleGeometry* capsule,
    OimoAabb* aabb,
    const OimoTransform* tf
) {
    OimoScalar r = capsule->radius;
    OimoScalar hh = capsule->halfHeight;

    // Get Y axis from rotation matrix and scale by halfHeight
    OimoVec3 axis;
    axis.x = tf->rotation.e01 * hh;
    axis.y = tf->rotation.e11 * hh;
    axis.z = tf->rotation.e21 * hh;

    // Take absolute values
    OimoScalar ax = oimo_abs(axis.x);
    OimoScalar ay = oimo_abs(axis.y);
    OimoScalar az = oimo_abs(axis.z);

    // AABB = position ± (abs(axis) + radius)
    aabb->min.x = tf->position.x - ax - r;
    aabb->min.y = tf->position.y - ay - r;
    aabb->min.z = tf->position.z - az - r;
    aabb->max.x = tf->position.x + ax + r;
    aabb->max.y = tf->position.y + ay + r;
    aabb->max.z = tf->position.z + az + r;
}

// Compute local supporting vertex for GJK (matches OimoPhysics)
static inline void oimo_capsule_geometry_compute_local_supporting_vertex(
    const OimoCapsuleGeometry* capsule,
    const OimoVec3* dir,
    OimoVec3* out
) {
    // Return the center of the hemisphere in the direction of dir
    if (dir->y > 0) {
        out->x = 0;
        out->y = capsule->halfHeight;
        out->z = 0;
    } else {
        out->x = 0;
        out->y = -capsule->halfHeight;
        out->z = 0;
    }
}

// Ray cast against capsule (matches OimoPhysics algorithm)
static inline int oimo_capsule_geometry_ray_cast(
    const OimoCapsuleGeometry* capsule,
    const OimoVec3* begin,
    const OimoVec3* end,
    const OimoTransform* tf,
    OimoRayCastHit* hit
) {
    // Transform ray to local space
    OimoVec3 localBegin = oimo_transform_inv_point(tf, begin);
    OimoVec3 localEnd = oimo_transform_inv_point(tf, end);

    OimoScalar p1x = localBegin.x;
    OimoScalar p1y = localBegin.y;
    OimoScalar p1z = localBegin.z;
    OimoScalar p2x = localEnd.x;
    OimoScalar p2y = localEnd.y;
    OimoScalar p2z = localEnd.z;

    OimoScalar halfH = capsule->halfHeight;
    OimoScalar r = capsule->radius;

    OimoScalar dx = p2x - p1x;
    OimoScalar dy = p2y - p1y;
    OimoScalar dz = p2z - p1z;

    // Test against infinite cylinder in XZ plane
    OimoScalar tminxz = 0;
    OimoScalar tmaxxz = 1;

    OimoScalar a = dx * dx + dz * dz;
    OimoScalar b = p1x * dx + p1z * dz;
    OimoScalar c = (p1x * p1x + p1z * p1z) - r * r;
    OimoScalar D = b * b - a * c;

    if (D < 0) return 0;

    if (a > 0) {
        OimoScalar sqrtD = oimo_sqrt(D);
        tminxz = (-b - sqrtD) / a;
        tmaxxz = (-b + sqrtD) / a;
        if (tminxz >= 1 || tmaxxz <= 0) return 0;
    } else {
        if (c >= 0) return 0;
        tminxz = 0;
        tmaxxz = 1;
    }

    OimoScalar crossY = p1y + dy * tminxz;

    // Check if we hit the cylindrical part
    if (crossY > -halfH && crossY < halfH) {
        if (tminxz > 0) {
            // Hit the cylinder side
            hit->fraction = tminxz;
            hit->position.x = p1x + dx * tminxz;
            hit->position.y = crossY;
            hit->position.z = p1z + dz * tminxz;

            // Normal is perpendicular to Y axis
            OimoScalar nx = hit->position.x;
            OimoScalar nz = hit->position.z;
            OimoScalar invLen = 1.0f / oimo_sqrt(nx * nx + nz * nz);
            hit->normal.x = nx * invLen;
            hit->normal.y = 0;
            hit->normal.z = nz * invLen;

            // Transform back to world space
            hit->position = oimo_transform_point(tf, &hit->position);
            hit->normal = oimo_mat3_mul_vec3(&tf->rotation, hit->normal);

            return 1;
        }
        return 0;
    }

    // Test against hemisphere caps
    OimoScalar sphereY = crossY < 0 ? -halfH : halfH;
    OimoScalar spx = 0, spy = sphereY, spz = 0;  // Sphere center

    OimoScalar ox = p1x - spx;
    OimoScalar oy = p1y - spy;
    OimoScalar oz = p1z - spz;

    a = dx * dx + dy * dy + dz * dz;
    b = ox * dx + oy * dy + oz * dz;
    c = ox * ox + oy * oy + oz * oz - r * r;

    D = b * b - a * c;
    if (D < 0) return 0;

    OimoScalar t = (-b - oimo_sqrt(D)) / a;
    if (t < 0 || t > 1) return 0;

    hit->fraction = t;
    hit->position.x = p1x + dx * t;
    hit->position.y = p1y + dy * t;
    hit->position.z = p1z + dz * t;

    // Normal points from sphere center to hit point
    hit->normal.x = hit->position.x - spx;
    hit->normal.y = hit->position.y - spy;
    hit->normal.z = hit->position.z - spz;
    OimoScalar invLen = 1.0f / oimo_sqrt(
        hit->normal.x * hit->normal.x +
        hit->normal.y * hit->normal.y +
        hit->normal.z * hit->normal.z
    );
    hit->normal.x *= invLen;
    hit->normal.y *= invLen;
    hit->normal.z *= invLen;

    // Transform back to world space
    hit->position = oimo_transform_point(tf, &hit->position);
    hit->normal = oimo_mat3_mul_vec3(&tf->rotation, hit->normal);

    return 1;
}

