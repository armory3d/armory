// box_mesh_detector.h - Box vs Static Mesh collision detection
#ifndef OIMO_COLLISION_NARROWPHASE_BOX_MESH_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_BOX_MESH_DETECTOR_H

#include "detector.h"
#include "detector_result.h"
#include "triangle_util.h"
#include "../geometry/box_geometry.h"
#include "../geometry/static_mesh_geometry.h"
#include "../broadphase/bvh.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"
#include <math.h>

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

// Compute the "effective radius" of a box along a given direction
// This is the distance from center to the farthest point in that direction
static inline float oimo_box_support_distance(const OimoVec3* half_ext, const OimoMat3* box_rot, const OimoVec3* dir) {
    // Box axes in mesh local space
    OimoVec3 ax = oimo_vec3(box_rot->e00, box_rot->e10, box_rot->e20);
    OimoVec3 ay = oimo_vec3(box_rot->e01, box_rot->e11, box_rot->e21);
    OimoVec3 az = oimo_vec3(box_rot->e02, box_rot->e12, box_rot->e22);

    // Project each axis onto direction and sum absolute contributions
    return half_ext->x * fabsf(oimo_vec3_dot(ax, *dir)) +
           half_ext->y * fabsf(oimo_vec3_dot(ay, *dir)) +
           half_ext->z * fabsf(oimo_vec3_dot(az, *dir));
}

// Get the support point of the box in a given direction (in mesh local space)
static inline OimoVec3 oimo_box_support_point(
    const OimoVec3* half_ext,
    const OimoMat3* box_rot,
    const OimoVec3* box_center,
    const OimoVec3* dir
) {
    OimoVec3 ax = oimo_vec3(box_rot->e00, box_rot->e10, box_rot->e20);
    OimoVec3 ay = oimo_vec3(box_rot->e01, box_rot->e11, box_rot->e21);
    OimoVec3 az = oimo_vec3(box_rot->e02, box_rot->e12, box_rot->e22);

    OimoVec3 result = *box_center;
    result = oimo_vec3_add(result, oimo_vec3_scale(ax, oimo_vec3_dot(ax, *dir) > 0 ? half_ext->x : -half_ext->x));
    result = oimo_vec3_add(result, oimo_vec3_scale(ay, oimo_vec3_dot(ay, *dir) > 0 ? half_ext->y : -half_ext->y));
    result = oimo_vec3_add(result, oimo_vec3_scale(az, oimo_vec3_dot(az, *dir) > 0 ? half_ext->z : -half_ext->z));
    return result;
}

// Detect box vs mesh collision
// Treat the box like a sphere with direction-dependent radius
static inline void oimo_box_mesh_detector_detect(
    OimoBoxMeshDetector* detector,
    OimoDetectorResult* result,
    const OimoBoxGeometry* box,
    const OimoStaticMeshGeometry* mesh,
    const OimoTransform* tf_box,
    const OimoTransform* tf_mesh
) {
    result->incremental = false;

    OimoVec3 half_ext = box->half_extents;

    // Transform box center to mesh local space
    OimoVec3 box_to_mesh = oimo_vec3_sub(tf_box->position, tf_mesh->position);
    OimoMat3 mesh_rot_inv = oimo_mat3_transpose(&tf_mesh->rotation);
    OimoVec3 box_center_local = oimo_mat3_mul_vec3(&mesh_rot_inv, box_to_mesh);

    // Box rotation in mesh local space
    OimoMat3 box_rot_local = oimo_mat3_mul(&mesh_rot_inv, &tf_box->rotation);

    // Build query AABB around box in mesh local space
    OimoVec3 box_x = oimo_vec3(box_rot_local.e00, box_rot_local.e10, box_rot_local.e20);
    OimoVec3 box_y = oimo_vec3(box_rot_local.e01, box_rot_local.e11, box_rot_local.e21);
    OimoVec3 box_z = oimo_vec3(box_rot_local.e02, box_rot_local.e12, box_rot_local.e22);

    float extent_x = half_ext.x * fabsf(box_x.x) + half_ext.y * fabsf(box_y.x) + half_ext.z * fabsf(box_z.x);
    float extent_y = half_ext.x * fabsf(box_x.y) + half_ext.y * fabsf(box_y.y) + half_ext.z * fabsf(box_z.y);
    float extent_z = half_ext.x * fabsf(box_x.z) + half_ext.y * fabsf(box_y.z) + half_ext.z * fabsf(box_z.z);

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

    // First pass: find the deepest penetration and primary normal
    // Use sphere-like approach: find closest point on triangle to box center,
    // then check if the box's extent along that direction overlaps
    float max_depth = 0.0f;
    OimoVec3 primary_normal_local = oimo_vec3(0, 1, 0);
    bool has_contact = false;

    for (int t = 0; t < bvh_result.count; t++) {
        int tri_idx = bvh_result.triangles[t];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        // Find closest point on triangle to box center (like sphere)
        OimoVec3 closest = oimo_closest_point_on_triangle(
            &box_center_local, &tri->v0, &tri->v1, &tri->v2
        );

        // Vector from closest point to box center
        OimoVec3 diff = oimo_vec3_sub(box_center_local, closest);
        float dist_sq = oimo_vec3_dot(diff, diff);
        float dist = sqrtf(dist_sq);

        // Compute box's effective radius along this direction
        OimoVec3 normal_dir;
        if (dist > 1e-6f) {
            normal_dir = oimo_vec3_scale(diff, 1.0f / dist);
        } else {
            // Box center is on the triangle - use triangle normal
            normal_dir = tri->normal;
            dist = 0.0f;
        }

        float effective_radius = oimo_box_support_distance(&half_ext, &box_rot_local, &normal_dir);

        // Check if penetrating (like sphere: if dist < radius)
        if (dist < effective_radius) {
            float depth = effective_radius - dist;

            if (depth > max_depth) {
                max_depth = depth;
                primary_normal_local = normal_dir;
                has_contact = true;
            }
        }
    }

    if (!has_contact) return;

    // Transform primary normal to world space
    OimoVec3 normal_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, primary_normal_local);
    oimo_detector_set_normal(&detector->base, result, &normal_world);

    // Second pass: add contact points
    int contact_count = 0;
    const int MAX_CONTACTS = 4;

    for (int t = 0; t < bvh_result.count && contact_count < MAX_CONTACTS; t++) {
        int tri_idx = bvh_result.triangles[t];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        OimoVec3 closest = oimo_closest_point_on_triangle(
            &box_center_local, &tri->v0, &tri->v1, &tri->v2
        );

        OimoVec3 diff = oimo_vec3_sub(box_center_local, closest);
        float dist_sq = oimo_vec3_dot(diff, diff);
        float dist = sqrtf(dist_sq);

        OimoVec3 normal_dir;
        if (dist > 1e-6f) {
            normal_dir = oimo_vec3_scale(diff, 1.0f / dist);
        } else {
            normal_dir = tri->normal;
            dist = 0.0f;
        }

        float effective_radius = oimo_box_support_distance(&half_ext, &box_rot_local, &normal_dir);

        if (dist < effective_radius) {
            float depth = effective_radius - dist;

            // Mesh contact point (in world space)
            OimoVec3 closest_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, closest);
            closest_world = oimo_vec3_add(closest_world, tf_mesh->position);

            // Box contact point: support point in -normal direction (in mesh local space)
            OimoVec3 neg_normal_local = oimo_vec3_scale(normal_dir, -1.0f);
            OimoVec3 box_contact = oimo_box_support_point(&half_ext, &box_rot_local, &box_center_local, &neg_normal_local);
            box_contact = oimo_mat3_mul_vec3(&tf_mesh->rotation, box_contact);
            box_contact = oimo_vec3_add(box_contact, tf_mesh->position);

            oimo_detector_add_point(&detector->base, result,
                &box_contact, &closest_world, depth, tri_idx);
            contact_count++;
        }
    }
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_BOX_MESH_DETECTOR_H
