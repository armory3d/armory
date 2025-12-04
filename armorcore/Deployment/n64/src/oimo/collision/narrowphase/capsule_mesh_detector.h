#pragma once

// capsule_mesh_detector.h - Capsule vs Static Mesh collision detection (Optimized for N64)

#include "detector.h"
#include "detector_result.h"
#include "triangle_util.h"
#include "mesh_contact.h"
#include "../geometry/capsule_geometry.h"
#include "../geometry/static_mesh_geometry.h"
#include "../broadphase/bvh.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoCapsuleMeshDetector {
    OimoDetector base;
} OimoCapsuleMeshDetector;

static inline void oimo_capsule_mesh_detector_init(OimoCapsuleMeshDetector* detector, bool swapped) {
    oimo_detector_init(&detector->base,
        swapped ? OIMO_DETECTOR_MESH_CAPSULE : OIMO_DETECTOR_CAPSULE_MESH,
        swapped);
}

// Helper: Test capsule segment against a triangle edge, update contact if closer
static inline void oimo_test_capsule_vs_edge(
    const OimoVec3* cap_p1, const OimoVec3* cap_p2,
    const OimoVec3* edge_a, const OimoVec3* edge_b,
    const OimoVec3* tri_normal,
    float radius, float radius_sq, int tri_idx,
    OimoMeshContactStorage* storage
) {
    OimoVec3 closest_cap, closest_edge;
    oimo_closest_points_segments(*cap_p1, *cap_p2, *edge_a, *edge_b, &closest_cap, &closest_edge);

    OimoVec3 diff = oimo_vec3_sub(closest_cap, closest_edge);
    float dist_sq = oimo_vec3_dot(diff, diff);

    if (dist_sq < radius_sq && dist_sq > 1e-8f) {
        float inv_dist = oimo_fast_inv_sqrt(dist_sq);
        float dist = dist_sq * inv_dist;
        float depth = radius - dist;

        if (depth > 0.0f) {
            OimoVec3 normal_dir = oimo_vec3_scale(diff, inv_dist);
            oimo_mesh_contact_storage_add(storage, &closest_edge, &normal_dir, depth, tri_idx);
        }
    }
}

// Helper: Test a point against a triangle face
static inline void oimo_test_point_vs_triangle(
    const OimoVec3* point,
    const OimoVec3* v0, const OimoVec3* v1, const OimoVec3* v2,
    const OimoVec3* tri_normal,
    float radius, float radius_sq, int tri_idx,
    OimoMeshContactStorage* storage
) {
    OimoVec3 closest = oimo_closest_point_on_triangle(point, v0, v1, v2);
    OimoVec3 diff = oimo_vec3_sub(*point, closest);
    float dist_sq = oimo_vec3_dot(diff, diff);

    if (dist_sq < radius_sq && dist_sq > 1e-8f) {
        float inv_dist = oimo_fast_inv_sqrt(dist_sq);
        float dist = dist_sq * inv_dist;
        float depth = radius - dist;

        if (depth > 0.0f) {
            OimoVec3 normal_dir = oimo_vec3_scale(diff, inv_dist);
            oimo_mesh_contact_storage_add(storage, &closest, &normal_dir, depth, tri_idx);
        }
    }
}

// Helper: Test triangle vertex against capsule axis
static inline void oimo_test_vertex_vs_capsule(
    const OimoVec3* vertex,
    const OimoVec3* cap_p1, const OimoVec3* cap_p2,
    const OimoVec3* tri_normal,
    float radius, float radius_sq, int tri_idx,
    OimoMeshContactStorage* storage
) {
    OimoVec3 closest_cap = oimo_closest_point_on_segment(*vertex, *cap_p1, *cap_p2);
    OimoVec3 diff = oimo_vec3_sub(closest_cap, *vertex);
    float dist_sq = oimo_vec3_dot(diff, diff);

    if (dist_sq < radius_sq && dist_sq > 1e-8f) {
        float inv_dist = oimo_fast_inv_sqrt(dist_sq);
        float dist = dist_sq * inv_dist;
        float depth = radius - dist;

        if (depth > 0.0f) {
            OimoVec3 normal_dir = oimo_vec3_scale(diff, inv_dist);
            oimo_mesh_contact_storage_add(storage, vertex, &normal_dir, depth, tri_idx);
        }
    }
}

// Detect capsule vs mesh collision (optimized single-pass with 4 contacts)
static inline void oimo_capsule_mesh_detector_detect(
    OimoCapsuleMeshDetector* detector,
    OimoDetectorResult* result,
    const OimoCapsuleGeometry* capsule,
    const OimoStaticMeshGeometry* mesh,
    const OimoTransform* tf_capsule,
    const OimoTransform* tf_mesh
) {
    result->incremental = false;

    OimoScalar radius = capsule->radius;
    OimoScalar half_height = capsule->halfHeight;
    float radius_sq = radius * radius;
    float max_extent = radius + half_height;

    // Get capsule axis in world space (local Y axis)
    OimoVec3 axis_world = oimo_vec3(
        tf_capsule->rotation.e01,
        tf_capsule->rotation.e11,
        tf_capsule->rotation.e21
    );

    // Capsule endpoints in world space
    OimoVec3 axis_offset = oimo_vec3_scale(axis_world, half_height);
    OimoVec3 cap_p1_world = oimo_vec3_add(tf_capsule->position, axis_offset);
    OimoVec3 cap_p2_world = oimo_vec3_sub(tf_capsule->position, axis_offset);

    // Transform capsule to mesh local space
    OimoVec3 capsule_to_mesh = oimo_vec3_sub(tf_capsule->position, tf_mesh->position);
    OimoMat3 mesh_rot_inv = oimo_mat3_transpose(&tf_mesh->rotation);
    OimoVec3 capsule_local = oimo_mat3_mul_vec3(&mesh_rot_inv, capsule_to_mesh);

    // Also transform endpoints to mesh local space
    OimoVec3 p1_to_mesh = oimo_vec3_sub(cap_p1_world, tf_mesh->position);
    OimoVec3 p2_to_mesh = oimo_vec3_sub(cap_p2_world, tf_mesh->position);
    OimoVec3 cap_p1_local = oimo_mat3_mul_vec3(&mesh_rot_inv, p1_to_mesh);
    OimoVec3 cap_p2_local = oimo_mat3_mul_vec3(&mesh_rot_inv, p2_to_mesh);

    // Build query AABB in mesh local space
    float query_extent = max_extent + 0.01f;
    OimoAabb query_aabb;
    query_aabb.min.x = capsule_local.x - query_extent;
    query_aabb.min.y = capsule_local.y - query_extent;
    query_aabb.min.z = capsule_local.z - query_extent;
    query_aabb.max.x = capsule_local.x + query_extent;
    query_aabb.max.y = capsule_local.y + query_extent;
    query_aabb.max.z = capsule_local.z + query_extent;

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

        // EARLY OUT: Quick plane distance check using capsule center
        float plane_dist = oimo_point_plane_distance(&capsule_local, &tri->v0, &tri->normal);
        if (plane_dist > max_extent || plane_dist < -max_extent) {
            continue;
        }

        // Test capsule axis against all triangle edges
        oimo_test_capsule_vs_edge(&cap_p1_local, &cap_p2_local, &tri->v0, &tri->v1,
            &tri->normal, radius, radius_sq, tri_idx, &storage);
        oimo_test_capsule_vs_edge(&cap_p1_local, &cap_p2_local, &tri->v1, &tri->v2,
            &tri->normal, radius, radius_sq, tri_idx, &storage);
        oimo_test_capsule_vs_edge(&cap_p1_local, &cap_p2_local, &tri->v2, &tri->v0,
            &tri->normal, radius, radius_sq, tri_idx, &storage);

        // Test capsule endpoints against triangle face
        oimo_test_point_vs_triangle(&cap_p1_local, &tri->v0, &tri->v1, &tri->v2,
            &tri->normal, radius, radius_sq, tri_idx, &storage);
        oimo_test_point_vs_triangle(&cap_p2_local, &tri->v0, &tri->v1, &tri->v2,
            &tri->normal, radius, radius_sq, tri_idx, &storage);

        // Test triangle vertices against capsule axis
        oimo_test_vertex_vs_capsule(&tri->v0, &cap_p1_local, &cap_p2_local,
            &tri->normal, radius, radius_sq, tri_idx, &storage);
        oimo_test_vertex_vs_capsule(&tri->v1, &cap_p1_local, &cap_p2_local,
            &tri->normal, radius, radius_sq, tri_idx, &storage);
        oimo_test_vertex_vs_capsule(&tri->v2, &cap_p1_local, &cap_p2_local,
            &tri->normal, radius, radius_sq, tri_idx, &storage);
    }

    // No collision
    if (!storage.has_contact) return;

    // Transform primary normal to world space
    OimoVec3 normal_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, storage.primary_normal);
    oimo_detector_set_normal(&detector->base, result, &normal_world);

    // Add all stored contacts
    for (int i = 0; i < storage.count; i++) {
        OimoMeshContact* c = &storage.contacts[i];

        // Mesh contact point (in world space)
        OimoVec3 closest_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, c->closest);
        OimoVec3 mesh_contact = oimo_vec3_add(closest_world, tf_mesh->position);

        // Capsule contact point: mesh contact offset by (depth - radius) along normal
        // This places the contact on the capsule surface
        OimoVec3 cap_contact = oimo_vec3_add(mesh_contact,
            oimo_vec3_scale(normal_world, c->depth));

        oimo_detector_add_point(&detector->base, result, &cap_contact, &mesh_contact,
            c->depth, c->tri_idx);
    }
}

#ifdef __cplusplus
}
#endif
