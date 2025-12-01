/**
 * OimoPhysics N64 Port - Geometry Implementation
 *
 * Implementation of generic dispatch functions for geometry operations.
 */

#include "geometry.h"
#include "sphere_geometry.h"
#include "box_geometry.h"

// ============================================================================
// Generic AABB Computation
// ============================================================================

void oimo_geometry_compute_aabb(const OimoGeometry* geom, OimoAabb* aabb, const OimoTransform* tf) {
    switch (geom->type) {
        case OIMO_GEOMETRY_SPHERE:
            oimo_sphere_geometry_compute_aabb(
                (const OimoSphereGeometry*)geom, aabb, tf);
            break;

        case OIMO_GEOMETRY_BOX:
            oimo_box_geometry_compute_aabb(
                (const OimoBoxGeometry*)geom, aabb, tf);
            break;

        default:
            // Unknown geometry type - create zero AABB at position
            aabb->min = oimo_vec3_copy(&tf->position);
            aabb->max = oimo_vec3_copy(&tf->position);
            break;
    }
}

// ============================================================================
// Generic Ray Casting
// ============================================================================

int oimo_geometry_ray_cast(
    const OimoGeometry* geom,
    const OimoVec3* begin,
    const OimoVec3* end,
    const OimoTransform* tf,
    OimoRayCastHit* hit
) {
    switch (geom->type) {
        case OIMO_GEOMETRY_SPHERE:
            return oimo_sphere_geometry_ray_cast(
                (const OimoSphereGeometry*)geom, begin, end, tf, hit);

        case OIMO_GEOMETRY_BOX:
            return oimo_box_geometry_ray_cast(
                (const OimoBoxGeometry*)geom, begin, end, tf, hit);

        default:
            return 0;  // No hit for unknown geometry type
    }
}
