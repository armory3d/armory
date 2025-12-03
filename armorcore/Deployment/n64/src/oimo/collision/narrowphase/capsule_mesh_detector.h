// capsule_mesh_detector.h - Capsule vs Static Mesh collision detection
#ifndef OIMO_COLLISION_NARROWPHASE_CAPSULE_MESH_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_CAPSULE_MESH_DETECTOR_H

#include "detector.h"
#include "detector_result.h"
#include "triangle_util.h"
#include "../geometry/capsule_geometry.h"
#include "../geometry/static_mesh_geometry.h"
#include "../broadphase/bvh.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"
#include <math.h>

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

// Closest point on line segment (in local space)
static inline OimoVec3 oimo_closest_point_on_segment(OimoVec3 p, OimoVec3 a, OimoVec3 b) {
    OimoVec3 ab = oimo_vec3_sub(b, a);
    OimoVec3 ap = oimo_vec3_sub(p, a);

    float ab_len_sq = oimo_vec3_dot(ab, ab);
    if (ab_len_sq < 1e-10f) return a;

    float t = oimo_vec3_dot(ap, ab) / ab_len_sq;
    if (t < 0.0f) t = 0.0f;
    if (t > 1.0f) t = 1.0f;

    return oimo_vec3_add(a, oimo_vec3_scale(ab, t));
}

// Closest points between two line segments
static inline void oimo_closest_points_segments(
    OimoVec3 p1, OimoVec3 p2, OimoVec3 p3, OimoVec3 p4,
    OimoVec3* closest1, OimoVec3* closest2
) {
    OimoVec3 d1 = oimo_vec3_sub(p2, p1);
    OimoVec3 d2 = oimo_vec3_sub(p4, p3);
    OimoVec3 r = oimo_vec3_sub(p1, p3);

    float a = oimo_vec3_dot(d1, d1);
    float e = oimo_vec3_dot(d2, d2);
    float f = oimo_vec3_dot(d2, r);

    float s, t;

    if (a <= 1e-6f && e <= 1e-6f) {
        *closest1 = p1;
        *closest2 = p3;
        return;
    }

    if (a <= 1e-6f) {
        s = 0.0f;
        t = f / e;
        if (t < 0.0f) t = 0.0f;
        if (t > 1.0f) t = 1.0f;
    } else {
        float c = oimo_vec3_dot(d1, r);
        if (e <= 1e-6f) {
            t = 0.0f;
            s = -c / a;
            if (s < 0.0f) s = 0.0f;
            if (s > 1.0f) s = 1.0f;
        } else {
            float b = oimo_vec3_dot(d1, d2);
            float denom = a * e - b * b;

            if (denom != 0.0f) {
                s = (b * f - c * e) / denom;
                if (s < 0.0f) s = 0.0f;
                if (s > 1.0f) s = 1.0f;
            } else {
                s = 0.0f;
            }

            t = (b * s + f) / e;

            if (t < 0.0f) {
                t = 0.0f;
                s = -c / a;
                if (s < 0.0f) s = 0.0f;
                if (s > 1.0f) s = 1.0f;
            } else if (t > 1.0f) {
                t = 1.0f;
                s = (b - c) / a;
                if (s < 0.0f) s = 0.0f;
                if (s > 1.0f) s = 1.0f;
            }
        }
    }

    *closest1 = oimo_vec3_add(p1, oimo_vec3_scale(d1, s));
    *closest2 = oimo_vec3_add(p3, oimo_vec3_scale(d2, t));
}

// Detect capsule vs mesh collision (optimized for N64)
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
    float max_extent = radius + half_height;  // For early-out

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

    // Find deepest penetration using squared distances to avoid sqrt in loop
    float min_dist_sq = 1e30f;
    OimoVec3 best_closest_capsule = oimo_vec3_zero();
    OimoVec3 best_closest_tri = oimo_vec3_zero();
    OimoVec3 best_normal = oimo_vec3(0, 1, 0);
    int best_triangle = -1;

    for (int i = 0; i < bvh_result.count; i++) {
        int tri_idx = bvh_result.triangles[i];
        const OimoTriangle* tri = oimo_static_mesh_get_triangle(mesh, tri_idx);
        if (!tri) continue;

        // EARLY OUT: Quick plane distance check using capsule center
        float plane_dist = oimo_point_plane_distance(&capsule_local, &tri->v0, &tri->normal);
        if (plane_dist > max_extent || plane_dist < -max_extent) {
            continue;
        }

        // Test capsule axis against triangle edges using squared distances for speed
        // Edge 0: v0 -> v1
        {
            OimoVec3 closest_cap, closest_edge;
            oimo_closest_points_segments(
                cap_p1_local, cap_p2_local,
                tri->v0, tri->v1,
                &closest_cap, &closest_edge
            );
            OimoVec3 diff = oimo_vec3_sub(closest_cap, closest_edge);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = closest_cap;
                best_closest_tri = closest_edge;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }
        // Edge 1: v1 -> v2
        {
            OimoVec3 closest_cap, closest_edge;
            oimo_closest_points_segments(
                cap_p1_local, cap_p2_local,
                tri->v1, tri->v2,
                &closest_cap, &closest_edge
            );
            OimoVec3 diff = oimo_vec3_sub(closest_cap, closest_edge);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = closest_cap;
                best_closest_tri = closest_edge;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }
        // Edge 2: v2 -> v0
        {
            OimoVec3 closest_cap, closest_edge;
            oimo_closest_points_segments(
                cap_p1_local, cap_p2_local,
                tri->v2, tri->v0,
                &closest_cap, &closest_edge
            );
            OimoVec3 diff = oimo_vec3_sub(closest_cap, closest_edge);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = closest_cap;
                best_closest_tri = closest_edge;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }

        // Test capsule endpoint 1 against triangle face
        {
            OimoVec3 closest = oimo_closest_point_on_triangle(
                &cap_p1_local, &tri->v0, &tri->v1, &tri->v2
            );
            OimoVec3 diff = oimo_vec3_sub(cap_p1_local, closest);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = cap_p1_local;
                best_closest_tri = closest;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }
        // Test capsule endpoint 2 against triangle face
        {
            OimoVec3 closest = oimo_closest_point_on_triangle(
                &cap_p2_local, &tri->v0, &tri->v1, &tri->v2
            );
            OimoVec3 diff = oimo_vec3_sub(cap_p2_local, closest);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = cap_p2_local;
                best_closest_tri = closest;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }

        // Test triangle vertices against capsule axis
        {
            OimoVec3 closest = oimo_closest_point_on_segment(tri->v0, cap_p1_local, cap_p2_local);
            OimoVec3 diff = oimo_vec3_sub(closest, tri->v0);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = closest;
                best_closest_tri = tri->v0;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }
        {
            OimoVec3 closest = oimo_closest_point_on_segment(tri->v1, cap_p1_local, cap_p2_local);
            OimoVec3 diff = oimo_vec3_sub(closest, tri->v1);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = closest;
                best_closest_tri = tri->v1;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }
        {
            OimoVec3 closest = oimo_closest_point_on_segment(tri->v2, cap_p1_local, cap_p2_local);
            OimoVec3 diff = oimo_vec3_sub(closest, tri->v2);
            float dist_sq = oimo_vec3_dot(diff, diff);
            if (dist_sq < min_dist_sq && dist_sq < radius_sq) {
                min_dist_sq = dist_sq;
                best_closest_capsule = closest;
                best_closest_tri = tri->v2;
                best_normal = tri->normal;
                best_triangle = tri_idx;
            }
        }
    }

    // No collision
    if (best_triangle < 0) return;

    // Compute penetration and normal using fast inverse sqrt
    OimoVec3 diff = oimo_vec3_sub(best_closest_capsule, best_closest_tri);
    float inv_dist = oimo_fast_inv_sqrt(min_dist_sq);
    float min_dist = min_dist_sq * inv_dist;  // Actual distance
    float depth = radius - min_dist;

    OimoVec3 normal_local;
    if (min_dist_sq > 1e-6f) {
        normal_local = oimo_vec3_scale(diff, inv_dist);
    } else {
        normal_local = best_normal;
    }

    // Transform normal to world space
    OimoVec3 normal_world = oimo_mat3_mul_vec3(&tf_mesh->rotation, normal_local);

    // Contact points in world space
    OimoVec3 tri_contact_local = oimo_mat3_mul_vec3(&tf_mesh->rotation, best_closest_tri);
    OimoVec3 tri_contact = oimo_vec3_add(tri_contact_local, tf_mesh->position);

    OimoVec3 cap_contact_local = oimo_mat3_mul_vec3(&tf_mesh->rotation, best_closest_capsule);
    OimoVec3 cap_contact_world = oimo_vec3_add(cap_contact_local, tf_mesh->position);
    OimoVec3 cap_contact_offset = oimo_vec3_scale(normal_world, -radius);
    OimoVec3 cap_contact = oimo_vec3_add(cap_contact_world, cap_contact_offset);

    // Set result
    oimo_detector_set_normal(&detector->base, result, &normal_world);
    oimo_detector_add_point(&detector->base, result, &cap_contact, &tri_contact, depth, best_triangle);
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_CAPSULE_MESH_DETECTOR_H
