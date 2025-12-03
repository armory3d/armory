// box_mesh_detector.h - Box vs Static Mesh collision detection
#ifndef OIMO_COLLISION_NARROWPHASE_BOX_MESH_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_BOX_MESH_DETECTOR_H

#include "detector.h"
#include "detector_result.h"
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

// Project box onto axis and get min/max
static inline void oimo_box_project_on_axis(
    const OimoVec3* half_ext,
    const OimoMat3* box_rot,
    const OimoVec3* box_center,
    const OimoVec3* axis,
    float* out_min,
    float* out_max
) {
    // Project box center onto axis
    float center_proj = oimo_vec3_dot(*box_center, *axis);

    // Compute extent projection (sum of absolute projections of half-extents)
    OimoVec3 box_x = oimo_vec3(box_rot->e00, box_rot->e10, box_rot->e20);
    OimoVec3 box_y = oimo_vec3(box_rot->e01, box_rot->e11, box_rot->e21);
    OimoVec3 box_z = oimo_vec3(box_rot->e02, box_rot->e12, box_rot->e22);

    float extent = half_ext->x * fabsf(oimo_vec3_dot(box_x, *axis)) +
                   half_ext->y * fabsf(oimo_vec3_dot(box_y, *axis)) +
                   half_ext->z * fabsf(oimo_vec3_dot(box_z, *axis));

    *out_min = center_proj - extent;
    *out_max = center_proj + extent;
}

// Project triangle onto axis and get min/max
static inline void oimo_triangle_project_on_axis(
    const OimoVec3* v0,
    const OimoVec3* v1,
    const OimoVec3* v2,
    const OimoVec3* axis,
    float* out_min,
    float* out_max
) {
    float p0 = oimo_vec3_dot(*v0, *axis);
    float p1 = oimo_vec3_dot(*v1, *axis);
    float p2 = oimo_vec3_dot(*v2, *axis);

    *out_min = fminf(p0, fminf(p1, p2));
    *out_max = fmaxf(p0, fmaxf(p1, p2));
}

// Test SAT (Separating Axis Theorem) on one axis
static inline bool oimo_sat_test_axis(
    const OimoVec3* half_ext,
    const OimoMat3* box_rot,
    const OimoVec3* box_center,
    const OimoVec3* v0,
    const OimoVec3* v1,
    const OimoVec3* v2,
    const OimoVec3* axis,
    float* min_overlap,
    OimoVec3* min_axis
) {
    float axis_len_sq = oimo_vec3_dot(*axis, *axis);
    if (axis_len_sq < 1e-10f) return true;  // Degenerate axis, skip

    float box_min, box_max, tri_min, tri_max;
    oimo_box_project_on_axis(half_ext, box_rot, box_center, axis, &box_min, &box_max);
    oimo_triangle_project_on_axis(v0, v1, v2, axis, &tri_min, &tri_max);

    // Check for separation
    if (box_max < tri_min || tri_max < box_min) {
        return false;  // Separated on this axis
    }

    // Compute overlap
    float overlap = fminf(box_max - tri_min, tri_max - box_min);
    if (overlap < *min_overlap) {
        *min_overlap = overlap;
        float inv_len = 1.0f / sqrtf(axis_len_sq);
        *min_axis = oimo_vec3_scale(*axis, inv_len);
    }

    return true;  // Overlapping on this axis
}

// Detect box vs mesh collision
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

    // Transform box to mesh local space
    OimoVec3 box_to_mesh = oimo_vec3_sub(tf_box->position, tf_mesh->position);
    OimoMat3 mesh_rot_inv = oimo_mat3_transpose(&tf_mesh->rotation);
    OimoVec3 box_center_local = oimo_mat3_mul_vec3(&mesh_rot_inv, box_to_mesh);
    OimoMat3 box_rot_local = oimo_mat3_mul(&mesh_rot_inv, &tf_box->rotation);

    // Build query AABB around box in mesh local space
    // We need to compute the AABB of the rotated box
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

    // Test each triangle using SAT
    for (int i = 0; i < bvh_result.count && result->num_points < OIMO_MAX_MANIFOLD_POINTS; i++) {
        int tri_idx = bvh_result.triangles[i];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        float min_overlap = 1e30f;
        OimoVec3 min_axis = oimo_vec3_zero();

        // Get box axes in mesh local space
        OimoVec3 axes[3];
        axes[0] = oimo_vec3(box_rot_local.e00, box_rot_local.e10, box_rot_local.e20);
        axes[1] = oimo_vec3(box_rot_local.e01, box_rot_local.e11, box_rot_local.e21);
        axes[2] = oimo_vec3(box_rot_local.e02, box_rot_local.e12, box_rot_local.e22);

        // Triangle edges
        OimoVec3 edge0 = oimo_vec3_sub(tri->v1, tri->v0);
        OimoVec3 edge1 = oimo_vec3_sub(tri->v2, tri->v1);
        OimoVec3 edge2 = oimo_vec3_sub(tri->v0, tri->v2);

        bool separated = false;

        // Test triangle normal
        if (!oimo_sat_test_axis(&half_ext, &box_rot_local, &box_center_local,
            &tri->v0, &tri->v1, &tri->v2, &tri->normal, &min_overlap, &min_axis)) {
            separated = true;
        }

        // Test box face normals (3 axes)
        if (!separated) {
            for (int j = 0; j < 3 && !separated; j++) {
                if (!oimo_sat_test_axis(&half_ext, &box_rot_local, &box_center_local,
                    &tri->v0, &tri->v1, &tri->v2, &axes[j], &min_overlap, &min_axis)) {
                    separated = true;
                }
            }
        }

        // Test edge cross products (9 axes)
        if (!separated) {
            OimoVec3 edges[3] = { edge0, edge1, edge2 };
            for (int j = 0; j < 3 && !separated; j++) {
                for (int k = 0; k < 3 && !separated; k++) {
                    OimoVec3 cross = oimo_vec3_cross(axes[j], edges[k]);
                    if (!oimo_sat_test_axis(&half_ext, &box_rot_local, &box_center_local,
                        &tri->v0, &tri->v1, &tri->v2, &cross, &min_overlap, &min_axis)) {
                        separated = true;
                    }
                }
            }
        }

        if (separated) continue;  // No collision with this triangle

        // Ensure normal points from triangle to box
        OimoVec3 tri_center = oimo_vec3(
            (tri->v0.x + tri->v1.x + tri->v2.x) / 3.0f,
            (tri->v0.y + tri->v1.y + tri->v2.y) / 3.0f,
            (tri->v0.z + tri->v1.z + tri->v2.z) / 3.0f
        );
        OimoVec3 to_box = oimo_vec3_sub(box_center_local, tri_center);
        if (oimo_vec3_dot(to_box, min_axis) < 0) {
            min_axis = oimo_vec3_scale(min_axis, -1.0f);
        }

        // Transform normal back to world space
        OimoVec3 normal_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, min_axis);

        // Approximate contact point (center of box projected onto triangle plane)
        OimoVec3 axis_offset = oimo_vec3_scale(min_axis, min_overlap * 0.5f);
        OimoVec3 contact_local = oimo_vec3_sub(box_center_local, axis_offset);

        OimoVec3 contact_world_offset = oimo_mat3_mul_vec3(&tf_mesh->rotation, contact_local);
        OimoVec3 contact_mesh = oimo_vec3_add(contact_world_offset, tf_mesh->position);

        OimoVec3 contact_box_offset = oimo_vec3_scale(normal_world, min_overlap);
        OimoVec3 contact_box = oimo_vec3_sub(contact_mesh, contact_box_offset);

        // Set result (only set normal once, on first contact)
        if (result->num_points == 0) {
            oimo_detector_set_normal(&detector->base, result, &normal_world);
        }
        oimo_detector_add_point(&detector->base, result, &contact_box, &contact_mesh, min_overlap, tri_idx);
    }
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_BOX_MESH_DETECTOR_H
