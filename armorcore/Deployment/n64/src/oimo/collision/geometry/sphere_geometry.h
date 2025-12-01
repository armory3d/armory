/**
 * OimoPhysics N64 Port - Sphere Geometry
 *
 * Sphere collision geometry.
 * Based on OimoPhysics SphereGeometry.hx
 */

#ifndef OIMO_COLLISION_GEOMETRY_SPHERE_GEOMETRY_H
#define OIMO_COLLISION_GEOMETRY_SPHERE_GEOMETRY_H

#include "../../common/setting.h"
#include "../../common/math_util.h"
#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/transform.h"
#include "geometry_type.h"
#include "aabb.h"
#include "geometry.h"

// ============================================================================
// Sphere Geometry Structure
// ============================================================================
typedef struct OimoSphereGeometry {
    OimoGeometry base;    // Base geometry (must be first for casting)
    OimoScalar radius;    // Sphere radius
} OimoSphereGeometry;

// ============================================================================
// Construction
// ============================================================================

// Initialize sphere geometry with given radius
static inline void oimo_sphere_geometry_init(OimoSphereGeometry* sphere, OimoScalar radius) {
    oimo_geometry_init(&sphere->base, OIMO_GEOMETRY_SPHERE);
    sphere->radius = radius;

    // Compute volume: V = (4/3) * PI * r^3
    sphere->base.volume = (4.0f / 3.0f) * OIMO_PI * radius * radius * radius;

    // Compute inertia coefficient: I/m = (2/5) * r^2 for all axes (diagonal matrix)
    OimoScalar inertia_coeff = (2.0f / 5.0f) * radius * radius;
    sphere->base.inertia_coeff = oimo_mat3(
        inertia_coeff, 0, 0,
        0, inertia_coeff, 0,
        0, 0, inertia_coeff
    );
}

// Create sphere geometry (returns by value)
static inline OimoSphereGeometry oimo_sphere_geometry(OimoScalar radius) {
    OimoSphereGeometry sphere;
    oimo_sphere_geometry_init(&sphere, radius);
    return sphere;
}

// ============================================================================
// Getters
// ============================================================================

// Get radius
static inline OimoScalar oimo_sphere_geometry_get_radius(const OimoSphereGeometry* sphere) {
    return sphere->radius;
}

// ============================================================================
// Setters
// ============================================================================

// Set radius and update mass properties
static inline void oimo_sphere_geometry_set_radius(OimoSphereGeometry* sphere, OimoScalar radius) {
    sphere->radius = radius;

    // Update volume
    sphere->base.volume = (4.0f / 3.0f) * OIMO_PI * radius * radius * radius;

    // Update inertia coefficient
    OimoScalar inertia_coeff = (2.0f / 5.0f) * radius * radius;
    sphere->base.inertia_coeff = oimo_mat3(
        inertia_coeff, 0, 0,
        0, inertia_coeff, 0,
        0, 0, inertia_coeff
    );
}

// ============================================================================
// AABB Computation
// ============================================================================

// Compute AABB for sphere at given transform
static inline void oimo_sphere_geometry_compute_aabb(
    const OimoSphereGeometry* sphere,
    OimoAabb* aabb,
    const OimoTransform* tf
) {
    // Sphere AABB is just position ± radius on all axes
    OimoScalar r = sphere->radius;
    aabb->min.x = tf->position.x - r;
    aabb->min.y = tf->position.y - r;
    aabb->min.z = tf->position.z - r;
    aabb->max.x = tf->position.x + r;
    aabb->max.y = tf->position.y + r;
    aabb->max.z = tf->position.z + r;
}

// ============================================================================
// Ray Casting
// ============================================================================

// Ray cast against sphere in local coordinates
// begin and end are in local space (relative to sphere center)
static inline int oimo_sphere_geometry_ray_cast_local(
    const OimoSphereGeometry* sphere,
    const OimoVec3* begin,
    const OimoVec3* end,
    OimoRayCastHit* hit
) {
    // Ray: P(t) = begin + t * d, where d = end - begin
    OimoVec3 d = oimo_vec3_sub(end, begin);

    // Solve: |begin + t*d|^2 = r^2
    // => (d·d)*t^2 + 2*(begin·d)*t + (begin·begin - r^2) = 0
    OimoScalar a = oimo_vec3_dot(&d, &d);
    OimoScalar b = oimo_vec3_dot(begin, &d);
    OimoScalar c = oimo_vec3_dot(begin, begin) - sphere->radius * sphere->radius;

    // Discriminant: D = b^2 - a*c
    OimoScalar discriminant = b * b - a * c;
    if (discriminant < 0) return 0;  // No intersection

    // t = (-b - sqrt(D)) / a  (take the nearer intersection)
    OimoScalar t = (-b - oimo_sqrt(discriminant)) / a;

    // Check if intersection is within ray segment
    if (t < 0 || t > 1) return 0;

    // Compute hit position and normal
    OimoVec3 hit_pos = oimo_vec3_add_scaled(begin, &d, t);
    OimoVec3 hit_normal = oimo_vec3_normalize(&hit_pos);

    hit->position = hit_pos;
    hit->normal = hit_normal;
    hit->fraction = t;

    return 1;
}

// Ray cast against sphere at given transform (world coordinates)
static inline int oimo_sphere_geometry_ray_cast(
    const OimoSphereGeometry* sphere,
    const OimoVec3* begin,
    const OimoVec3* end,
    const OimoTransform* tf,
    OimoRayCastHit* hit
) {
    // Transform ray to local space
    OimoVec3 local_begin = oimo_transform_inv_point(tf, begin);
    OimoVec3 local_end = oimo_transform_inv_point(tf, end);

    // Perform ray cast in local space
    if (!oimo_sphere_geometry_ray_cast_local(sphere, &local_begin, &local_end, hit)) {
        return 0;
    }

    // Transform result back to world space
    hit->position = oimo_transform_point(tf, &hit->position);
    hit->normal = oimo_transform_vector(tf, &hit->normal);

    return 1;
}

// ============================================================================
// Supporting Vertex (for GJK, if needed in future)
// ============================================================================

// Compute local supporting vertex in given direction
// For a sphere, the supporting vertex is always at the center (for core geometry)
static inline OimoVec3 oimo_sphere_geometry_support_local(
    const OimoSphereGeometry* sphere,
    const OimoVec3* dir
) {
    (void)sphere;  // Unused
    (void)dir;     // Unused
    return oimo_vec3_zero();
}

#endif // OIMO_COLLISION_GEOMETRY_SPHERE_GEOMETRY_H
