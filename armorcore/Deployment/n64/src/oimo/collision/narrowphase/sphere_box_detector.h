#ifndef OIMO_COLLISION_NARROWPHASE_SPHERE_BOX_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_SPHERE_BOX_DETECTOR_H

#include "detector.h"
#include "detector_result.h"
#include "../geometry/sphere_geometry.h"
#include "../geometry/box_geometry.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"
#include "../../common/mat3.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoSphereBoxDetector {
    OimoDetector base;
} OimoSphereBoxDetector;

static inline void oimo_sphere_box_detector_init(OimoSphereBoxDetector* detector, bool swapped) {
    oimo_detector_init(&detector->base,
        swapped ? OIMO_DETECTOR_BOX_SPHERE : OIMO_DETECTOR_SPHERE_BOX,
        swapped);
}

static inline void oimo_sphere_box_detector_detect(
    OimoSphereBoxDetector* detector,
    OimoDetectorResult* result,
    const OimoSphereGeometry* sphere,
    const OimoBoxGeometry* box,
    const OimoTransform* tf_sphere,
    const OimoTransform* tf_box
) {
    result->incremental = false;

    OimoVec3 half_ext = box->half_extents;
    OimoVec3 neg_half_ext;
    oimo_vec3_negate_to(&neg_half_ext, &half_ext);

    OimoScalar r = sphere->radius;

    // Vector from box center to sphere center
    OimoVec3 box_to_sphere;
    oimo_vec3_sub_to(&box_to_sphere, &tf_sphere->position, &tf_box->position);

    // Transform to box's local space (multiply by transposed rotation)
    OimoMat3 rot_transposed = oimo_mat3_transpose(&tf_box->rotation);
    OimoVec3 box_to_sphere_in_box = oimo_mat3_mul_vec3(&rot_transposed, box_to_sphere);

    // Check if sphere center is inside the box
    bool inside_box =
        box_to_sphere_in_box.x >= neg_half_ext.x && box_to_sphere_in_box.x <= half_ext.x &&
        box_to_sphere_in_box.y >= neg_half_ext.y && box_to_sphere_in_box.y <= half_ext.y &&
        box_to_sphere_in_box.z >= neg_half_ext.z && box_to_sphere_in_box.z <= half_ext.z;

    if (inside_box) {
        // Compute distance to each face
        OimoVec3 sphere_to_box_surface;
        sphere_to_box_surface.x = half_ext.x - oimo_abs(box_to_sphere_in_box.x);
        sphere_to_box_surface.y = half_ext.y - oimo_abs(box_to_sphere_in_box.y);
        sphere_to_box_surface.z = half_ext.z - oimo_abs(box_to_sphere_in_box.z);

        OimoVec3 normal_in_box;
        OimoVec3 projection_mask;
        OimoScalar depth;

        // Find minimum distance axis
        OimoScalar dist_x = sphere_to_box_surface.x;
        OimoScalar dist_y = sphere_to_box_surface.y;
        OimoScalar dist_z = sphere_to_box_surface.z;

        if (dist_x <= dist_y && dist_x <= dist_z) {
            // X axis is closest
            if (box_to_sphere_in_box.x > 0.0f) {
                oimo_vec3_set(&normal_in_box, 1.0f, 0.0f, 0.0f);
            } else {
                oimo_vec3_set(&normal_in_box, -1.0f, 0.0f, 0.0f);
            }
            oimo_vec3_set(&projection_mask, 0.0f, 1.0f, 1.0f);
            depth = dist_x;
        } else if (dist_y <= dist_x && dist_y <= dist_z) {
            // Y axis is closest
            if (box_to_sphere_in_box.y > 0.0f) {
                oimo_vec3_set(&normal_in_box, 0.0f, 1.0f, 0.0f);
            } else {
                oimo_vec3_set(&normal_in_box, 0.0f, -1.0f, 0.0f);
            }
            oimo_vec3_set(&projection_mask, 1.0f, 0.0f, 1.0f);
            depth = dist_y;
        } else {
            // Z axis is closest
            if (box_to_sphere_in_box.z > 0.0f) {
                oimo_vec3_set(&normal_in_box, 0.0f, 0.0f, 1.0f);
            } else {
                oimo_vec3_set(&normal_in_box, 0.0f, 0.0f, -1.0f);
            }
            oimo_vec3_set(&projection_mask, 1.0f, 1.0f, 0.0f);
            depth = dist_z;
        }

        // Compute closest point on box
        OimoVec3 base;
        base.x = projection_mask.x * box_to_sphere_in_box.x;
        base.y = projection_mask.y * box_to_sphere_in_box.y;
        base.z = projection_mask.z * box_to_sphere_in_box.z;

        OimoVec3 box_to_closest_in_box;
        box_to_closest_in_box.x = normal_in_box.x * half_ext.x + base.x;
        box_to_closest_in_box.y = normal_in_box.y * half_ext.y + base.y;
        box_to_closest_in_box.z = normal_in_box.z * half_ext.z + base.z;

        // Transform back to world space
        OimoVec3 box_to_closest = oimo_mat3_mul_vec3(&tf_box->rotation, box_to_closest_in_box);
        OimoVec3 normal = oimo_mat3_mul_vec3(&tf_box->rotation, normal_in_box);

        oimo_detector_set_normal(&detector->base, result, &normal);

        // Contact positions
        OimoVec3 pos1, pos2;
        OimoVec3 scaled_n;
        oimo_vec3_scale_to(&scaled_n, &normal, -r);
        oimo_vec3_add_to(&pos1, &tf_sphere->position, &scaled_n);
        oimo_vec3_add_to(&pos2, &tf_box->position, &box_to_closest);

        oimo_detector_add_point(&detector->base, result, &pos1, &pos2, depth, 0);
        return;
    }

    // Sphere center is outside the box
    // Clamp sphere center to box bounds to find closest point

    // Avoid division by zero with epsilon adjustment
    OimoScalar eps = 1e-9f;
    OimoVec3 adjusted_half_ext, adjusted_neg_half_ext;
    oimo_vec3_set(&adjusted_half_ext, half_ext.x - eps, half_ext.y - eps, half_ext.z - eps);
    oimo_vec3_set(&adjusted_neg_half_ext, neg_half_ext.x + eps, neg_half_ext.y + eps, neg_half_ext.z + eps);

    OimoVec3 box_to_closest_in_box;
    box_to_closest_in_box.x = oimo_clamp(box_to_sphere_in_box.x, adjusted_neg_half_ext.x, adjusted_half_ext.x);
    box_to_closest_in_box.y = oimo_clamp(box_to_sphere_in_box.y, adjusted_neg_half_ext.y, adjusted_half_ext.y);
    box_to_closest_in_box.z = oimo_clamp(box_to_sphere_in_box.z, adjusted_neg_half_ext.z, adjusted_half_ext.z);

    // Vector from closest point to sphere center
    OimoVec3 closest_to_sphere_in_box;
    oimo_vec3_sub_to(&closest_to_sphere_in_box, &box_to_sphere_in_box, &box_to_closest_in_box);

    OimoScalar dist2 = oimo_vec3_dot(closest_to_sphere_in_box, closest_to_sphere_in_box);
    if (dist2 >= r * r) {
        return;  // No collision
    }

    OimoScalar dist = oimo_sqrt(dist2);

    // Transform back to world space
    OimoVec3 box_to_closest = oimo_mat3_mul_vec3(&tf_box->rotation, box_to_closest_in_box);
    OimoVec3 closest_to_sphere = oimo_mat3_mul_vec3(&tf_box->rotation, closest_to_sphere_in_box);

    // Normal from box to sphere
    OimoVec3 normal;
    oimo_vec3_normalize_to(&normal, &closest_to_sphere);
    oimo_detector_set_normal(&detector->base, result, &normal);

    // Contact positions
    OimoVec3 pos1, pos2;
    OimoVec3 scaled_n;
    oimo_vec3_scale_to(&scaled_n, &normal, -r);
    oimo_vec3_add_to(&pos1, &tf_sphere->position, &scaled_n);
    oimo_vec3_add_to(&pos2, &tf_box->position, &box_to_closest);

    OimoScalar depth = r - dist;
    oimo_detector_add_point(&detector->base, result, &pos1, &pos2, depth, 0);
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_SPHERE_BOX_DETECTOR_H

