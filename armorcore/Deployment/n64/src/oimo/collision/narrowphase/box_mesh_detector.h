#pragma once

// box_mesh_detector.h - Box vs Static Mesh collision detection (Optimized for N64)

#include "detector.h"
#include "detector_result.h"
#include "triangle_util.h"
#include "mesh_contact.h"
#include "../geometry/box_geometry.h"
#include "../geometry/static_mesh_geometry.h"
#include "../broadphase/bvh.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoBoxMeshDetector {
    OimoDetector base;
} OimoBoxMeshDetector;

static inline void oimo_box_mesh_detector_init(OimoBoxMeshDetector* detector, bool swapped) {
    oimo_detector_init(&detector->base,
        swapped ? OIMO_DETECTOR_MESH_BOX : OIMO_DETECTOR_BOX_MESH,
        swapped);
}

// Cached box axes structure to avoid recomputing per-triangle
typedef struct OimoBoxAxes {
    OimoVec3 x, y, z;      // Box axes in mesh local space
    OimoVec3 half_ext;     // Half extents
    float max_extent;       // Maximum extent for quick rejection
} OimoBoxAxes;

// Compute box's effective radius along a direction using cached axes
static inline float oimo_box_support_distance_cached(const OimoBoxAxes* axes, const OimoVec3* dir) {
    return axes->half_ext.x * fabsf(oimo_vec3_dot(axes->x, *dir)) +
           axes->half_ext.y * fabsf(oimo_vec3_dot(axes->y, *dir)) +
           axes->half_ext.z * fabsf(oimo_vec3_dot(axes->z, *dir));
}

// Get support point using cached axes
static inline OimoVec3 oimo_box_support_point_cached(
    const OimoBoxAxes* axes,
    const OimoVec3* box_center,
    const OimoVec3* dir
) {
    OimoVec3 result = *box_center;
    result = oimo_vec3_add(result, oimo_vec3_scale(axes->x, oimo_vec3_dot(axes->x, *dir) > 0 ? axes->half_ext.x : -axes->half_ext.x));
    result = oimo_vec3_add(result, oimo_vec3_scale(axes->y, oimo_vec3_dot(axes->y, *dir) > 0 ? axes->half_ext.y : -axes->half_ext.y));
    result = oimo_vec3_add(result, oimo_vec3_scale(axes->z, oimo_vec3_dot(axes->z, *dir) > 0 ? axes->half_ext.z : -axes->half_ext.z));
    return result;
}

// Detect box vs mesh collision (optimized single-pass version)
static inline void oimo_box_mesh_detector_detect(
    OimoBoxMeshDetector* detector,
    OimoDetectorResult* result,
    const OimoBoxGeometry* box,
    const OimoStaticMeshGeometry* mesh,
    const OimoTransform* tf_box,
    const OimoTransform* tf_mesh
) {
    result->incremental = false;

    // Transform box center to mesh local space
    OimoVec3 box_to_mesh = oimo_vec3_sub(tf_box->position, tf_mesh->position);
    OimoMat3 mesh_rot_inv = oimo_mat3_transpose(&tf_mesh->rotation);
    OimoVec3 box_center_local = oimo_mat3_mul_vec3(&mesh_rot_inv, box_to_mesh);

    // Box rotation in mesh local space
    OimoMat3 box_rot_local = oimo_mat3_mul(&mesh_rot_inv, &tf_box->rotation);

    // Cache box axes (computed once, used for all triangles)
    OimoBoxAxes axes;
    axes.x = oimo_vec3(box_rot_local.e00, box_rot_local.e10, box_rot_local.e20);
    axes.y = oimo_vec3(box_rot_local.e01, box_rot_local.e11, box_rot_local.e21);
    axes.z = oimo_vec3(box_rot_local.e02, box_rot_local.e12, box_rot_local.e22);
    axes.half_ext = box->half_extents;
    // Max extent for quick plane distance rejection
    axes.max_extent = axes.half_ext.x + axes.half_ext.y + axes.half_ext.z;

    // Build query AABB using cached axes
    float extent_x = axes.half_ext.x * fabsf(axes.x.x) + axes.half_ext.y * fabsf(axes.y.x) + axes.half_ext.z * fabsf(axes.z.x);
    float extent_y = axes.half_ext.x * fabsf(axes.x.y) + axes.half_ext.y * fabsf(axes.y.y) + axes.half_ext.z * fabsf(axes.z.y);
    float extent_z = axes.half_ext.x * fabsf(axes.x.z) + axes.half_ext.y * fabsf(axes.y.z) + axes.half_ext.z * fabsf(axes.z.z);

    OimoAabb query_aabb;
    query_aabb.min.x = box_center_local.x - extent_x;
    query_aabb.min.y = box_center_local.y - extent_y;
    query_aabb.min.z = box_center_local.z - extent_z;
    query_aabb.max.x = box_center_local.x + extent_x;
    query_aabb.max.y = box_center_local.y + extent_y;
    query_aabb.max.z = box_center_local.z + extent_z;

    // Query BVH for overlapping triangles
    OimoBvhQueryResult bvh_result;
    oimo_static_mesh_query_triangles(mesh, &query_aabb, &bvh_result);

    if (bvh_result.count == 0) return;

    // Initialize contact storage
    OimoMeshContactStorage storage;
    oimo_mesh_contact_storage_init(&storage);

    for (int t = 0; t < bvh_result.count; t++) {
        int tri_idx = bvh_result.triangles[t];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        // EARLY OUT: Quick plane distance check
        // If box center is too far from triangle plane, skip expensive closest point
        float plane_dist = oimo_point_plane_distance(&box_center_local, &tri->v0, &tri->normal);
        if (plane_dist > axes.max_extent || plane_dist < -axes.max_extent) {
            continue;  // Box can't possibly touch this triangle
        }

        // Find closest point on triangle to box center
        OimoVec3 closest = oimo_closest_point_on_triangle(
            &box_center_local, &tri->v0, &tri->v1, &tri->v2
        );

        // Vector from closest point to box center
        OimoVec3 diff = oimo_vec3_sub(box_center_local, closest);
        float dist_sq = oimo_vec3_dot(diff, diff);

        // EARLY OUT: If distance squared > max_extent squared, no collision possible
        if (dist_sq > axes.max_extent * axes.max_extent) {
            continue;
        }

        // Use fast inverse sqrt for normalization
        OimoVec3 normal_dir;
        float dist;
        if (dist_sq > 1e-6f) {
            float inv_dist = oimo_fast_inv_sqrt(dist_sq);
            dist = dist_sq * inv_dist;  // dist = dist_sq / sqrt(dist_sq) = sqrt(dist_sq)
            normal_dir = oimo_vec3_scale(diff, inv_dist);
        } else {
            normal_dir = tri->normal;
            dist = 0.0f;
        }

        // Compute box's effective radius along this direction
        float effective_radius = oimo_box_support_distance_cached(&axes, &normal_dir);

        // Check if penetrating
        if (dist < effective_radius) {
            float depth = effective_radius - dist;
            oimo_mesh_contact_storage_add(&storage, &closest, &normal_dir, depth, tri_idx);
        }
    }

    if (!storage.has_contact) return;

    // Transform primary normal to world space
    OimoVec3 normal_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, storage.primary_normal);
    oimo_detector_set_normal(&detector->base, result, &normal_world);

    // Add all stored contacts
    for (int i = 0; i < storage.count; i++) {
        OimoMeshContact* c = &storage.contacts[i];

        // Mesh contact point (in world space)
        OimoVec3 closest_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, c->closest);
        closest_world = oimo_vec3_add(closest_world, tf_mesh->position);

        // Box contact point: support point in -normal direction
        OimoVec3 neg_normal_local = oimo_vec3_scale(c->normal_dir, -1.0f);
        OimoVec3 box_contact = oimo_box_support_point_cached(&axes, &box_center_local, &neg_normal_local);
        box_contact = oimo_mat3_mul_vec3(&tf_mesh->rotation, box_contact);
        box_contact = oimo_vec3_add(box_contact, tf_mesh->position);

        oimo_detector_add_point(&detector->base, result,
            &box_contact, &closest_world, c->depth, c->tri_idx);
    }
}

#ifdef __cplusplus
}
#endif
