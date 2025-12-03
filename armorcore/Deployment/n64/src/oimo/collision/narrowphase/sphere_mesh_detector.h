// sphere_mesh_detector.h - Sphere vs Static Mesh collision detection
#ifndef OIMO_COLLISION_NARROWPHASE_SPHERE_MESH_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_SPHERE_MESH_DETECTOR_H

#include "detector.h"
#include "detector_result.h"
#include "triangle_util.h"
#include "../geometry/sphere_geometry.h"
#include "../geometry/static_mesh_geometry.h"
#include "../broadphase/bvh.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoSphereMeshDetector {
    OimoDetector base;
} OimoSphereMeshDetector;

static inline void oimo_sphere_mesh_detector_init(OimoSphereMeshDetector* detector, bool swapped) {
    oimo_detector_init(&detector->base,
        swapped ? OIMO_DETECTOR_MESH_SPHERE : OIMO_DETECTOR_SPHERE_MESH,
        swapped);
}

// Detect sphere vs mesh collision
static inline void oimo_sphere_mesh_detector_detect(
    OimoSphereMeshDetector* detector,
    OimoDetectorResult* result,
    const OimoSphereGeometry* sphere,
    const OimoStaticMeshGeometry* mesh,
    const OimoTransform* tf_sphere,
    const OimoTransform* tf_mesh
) {
    result->incremental = false;

    OimoScalar radius = sphere->radius;

    // Transform sphere center to mesh local space
    OimoVec3 sphere_world = tf_sphere->position;
    OimoVec3 sphere_to_mesh = oimo_vec3_sub(sphere_world, tf_mesh->position);
    OimoMat3 mesh_rot_inv = oimo_mat3_transpose(&tf_mesh->rotation);
    OimoVec3 sphere_local = oimo_mat3_mul_vec3(&mesh_rot_inv, sphere_to_mesh);

    // Build query AABB around sphere in mesh local space
    OimoAabb query_aabb;
    query_aabb.min.x = sphere_local.x - radius;
    query_aabb.min.y = sphere_local.y - radius;
    query_aabb.min.z = sphere_local.z - radius;
    query_aabb.max.x = sphere_local.x + radius;
    query_aabb.max.y = sphere_local.y + radius;
    query_aabb.max.z = sphere_local.z + radius;

    // Query BVH for overlapping triangles
    OimoBvhQueryResult bvh_result;
    oimo_static_mesh_query_triangles(mesh, &query_aabb, &bvh_result);

    // First pass: find the deepest penetration to set the primary normal
    float max_depth = 0.0f;
    OimoVec3 primary_normal_local = {0, 1, 0};
    bool has_contact = false;

    for (int i = 0; i < bvh_result.count; i++) {
        int tri_idx = bvh_result.triangles[i];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        OimoVec3 closest = oimo_closest_point_on_triangle(
            &sphere_local, &tri->v0, &tri->v1, &tri->v2
        );

        OimoVec3 diff = oimo_vec3_sub(sphere_local, closest);
        float dist_sq = oimo_vec3_dot(diff, diff);

        if (dist_sq < radius * radius) {
            float dist = sqrtf(dist_sq);
            float depth = radius - dist;

            if (depth > max_depth) {
                max_depth = depth;
                has_contact = true;
                if (dist > 1e-6f) {
                    primary_normal_local = oimo_vec3_scale(diff, 1.0f / dist);
                } else {
                    primary_normal_local = tri->normal;
                }
            }
        }
    }

    if (!has_contact) return;

    // Transform primary normal to world space and set it
    OimoVec3 normal_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, primary_normal_local);
    oimo_detector_set_normal(&detector->base, result, &normal_world);

    // Second pass: add contact points for ALL penetrating triangles (up to 4)
    int contact_count = 0;
    const int MAX_CONTACTS = 4;

    for (int i = 0; i < bvh_result.count && contact_count < MAX_CONTACTS; i++) {
        int tri_idx = bvh_result.triangles[i];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        OimoVec3 closest = oimo_closest_point_on_triangle(
            &sphere_local, &tri->v0, &tri->v1, &tri->v2
        );

        OimoVec3 diff = oimo_vec3_sub(sphere_local, closest);
        float dist_sq = oimo_vec3_dot(diff, diff);

        if (dist_sq < radius * radius) {
            float dist = sqrtf(dist_sq);
            float depth = radius - dist;

            // Contact point on mesh (in world space)
            OimoVec3 closest_world_local = oimo_mat3_mul_vec3(&tf_mesh->rotation, closest);
            OimoVec3 mesh_contact = oimo_vec3_add(closest_world_local, tf_mesh->position);

            // Contact point on sphere (in world space)
            OimoVec3 sphere_contact_offset = oimo_vec3_scale(normal_world, -radius);
            OimoVec3 sphere_contact = oimo_vec3_add(sphere_world, sphere_contact_offset);

            oimo_detector_add_point(&detector->base, result, &sphere_contact, &mesh_contact, depth, tri_idx);
            contact_count++;
        }
    }
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_SPHERE_MESH_DETECTOR_H
