#pragma once

// sphere_mesh_detector.h - Sphere vs Static Mesh collision detection (Optimized for N64)

#include "detector.h"
#include "detector_result.h"
#include "triangle_util.h"
#include "mesh_contact.h"
#include "../geometry/sphere_geometry.h"
#include "../geometry/static_mesh_geometry.h"
#include "../broadphase/bvh.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"

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

// Detect sphere vs mesh collision (optimized single-pass)
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
    float radius_sq = radius * radius;

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

    if (bvh_result.count == 0) return;

    // Initialize contact storage
    OimoMeshContactStorage storage;
    oimo_mesh_contact_storage_init(&storage);

    for (int i = 0; i < bvh_result.count; i++) {
        int tri_idx = bvh_result.triangles[i];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        // EARLY OUT: Quick plane distance check
        float plane_dist = oimo_point_plane_distance(&sphere_local, &tri->v0, &tri->normal);
        if (plane_dist > radius || plane_dist < -radius) {
            continue;  // Sphere too far from triangle plane
        }

        OimoVec3 closest = oimo_closest_point_on_triangle(
            &sphere_local, &tri->v0, &tri->v1, &tri->v2
        );

        OimoVec3 diff = oimo_vec3_sub(sphere_local, closest);
        float dist_sq = oimo_vec3_dot(diff, diff);

        if (dist_sq < radius_sq) {
            // Use fast inverse sqrt
            float inv_dist = oimo_fast_inv_sqrt(dist_sq);
            float dist = dist_sq * inv_dist;
            float depth = radius - dist;

            OimoVec3 normal_dir;
            if (dist_sq > 1e-6f) {
                normal_dir = oimo_vec3_scale(diff, inv_dist);
            } else {
                normal_dir = tri->normal;
            }

            oimo_mesh_contact_storage_add(&storage, &closest, &normal_dir, depth, tri_idx);
        }
    }

    if (!storage.has_contact) return;

    // Transform primary normal to world space and set it
    OimoVec3 normal_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, storage.primary_normal);
    oimo_detector_set_normal(&detector->base, result, &normal_world);

    // Add all stored contacts
    for (int i = 0; i < storage.count; i++) {
        OimoMeshContact* c = &storage.contacts[i];

        // Contact point on mesh (in world space)
        OimoVec3 closest_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, c->closest);
        OimoVec3 mesh_contact = oimo_vec3_add(closest_world, tf_mesh->position);

        // Contact point on sphere (in world space)
        OimoVec3 sphere_contact_offset = oimo_vec3_scale(normal_world, -radius);
        OimoVec3 sphere_contact = oimo_vec3_add(sphere_world, sphere_contact_offset);

        oimo_detector_add_point(&detector->base, result, &sphere_contact, &mesh_contact,
            c->depth, c->tri_idx);
    }
}

#ifdef __cplusplus
}
#endif
