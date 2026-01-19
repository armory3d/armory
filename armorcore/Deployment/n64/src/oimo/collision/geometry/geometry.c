/**
 * OimoPhysics N64 Port - Geometry Implementation
 *
 * Implementation of generic dispatch functions for geometry operations.
 */

#include "geometry.h"
#include "sphere_geometry.h"
#include "box_geometry.h"
#include "capsule_geometry.h"
#include "static_mesh_geometry.h"

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

        case OIMO_GEOMETRY_CAPSULE:
            oimo_capsule_geometry_compute_aabb(
                (const OimoCapsuleGeometry*)geom, aabb, tf);
            break;

        case OIMO_GEOMETRY_STATIC_MESH:
            oimo_static_mesh_compute_aabb(
                (const OimoStaticMeshGeometry*)geom, aabb, tf);
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

        case OIMO_GEOMETRY_CAPSULE:
            return oimo_capsule_geometry_ray_cast(
                (const OimoCapsuleGeometry*)geom, begin, end, tf, hit);

        case OIMO_GEOMETRY_STATIC_MESH: {
            // Transform ray to local space
            OimoVec3 local_begin = oimo_transform_inv_point(tf, begin);
            OimoVec3 local_end = oimo_transform_inv_point(tf, end);
            if (oimo_static_mesh_ray_cast(
                (const OimoStaticMeshGeometry*)geom, &local_begin, &local_end, hit)) {
                // Transform hit back to world space
                hit->position = oimo_transform_point(tf, &hit->position);
                hit->normal = oimo_transform_vector(tf, &hit->normal);
                return 1;
            }
            return 0;
        }

        default:
            return 0;  // No hit for unknown geometry type
    }
}
