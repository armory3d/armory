#pragma once

#include "detector.h"
#include "detector_result.h"
#include "../geometry/sphere_geometry.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoSphereSphereDetector {
    OimoDetector base;
} OimoSphereSphereDetector;

static inline void oimo_sphere_sphere_detector_init(OimoSphereSphereDetector* detector) {
    oimo_detector_init(&detector->base, OIMO_DETECTOR_SPHERE_SPHERE, false);
}

static inline void oimo_sphere_sphere_detector_detect(
    OimoSphereSphereDetector* detector,
    OimoDetectorResult* result,
    const OimoSphereGeometry* sphere1,
    const OimoSphereGeometry* sphere2,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    result->incremental = false;

    // Vector from sphere2 center to sphere1 center
    OimoVec3 d;
    oimo_vec3_sub_to(&d, &tf1->position, &tf2->position);

    OimoScalar r1 = sphere1->radius;
    OimoScalar r2 = sphere2->radius;
    OimoScalar sum_radii = r1 + r2;

    // Check if spheres are separated
    OimoScalar len2 = oimo_vec3_dot(d, d);
    if (len2 >= sum_radii * sum_radii) {
        return;  // No collision
    }

    OimoScalar len = oimo_sqrt(len2);

    // Compute contact normal
    OimoVec3 n;
    if (len > 0.0f) {
        oimo_vec3_scale_to(&n, &d, 1.0f / len);
    } else {
        // Spheres are coincident, use arbitrary normal
        oimo_vec3_set(&n, 1.0f, 0.0f, 0.0f);
    }

    // Set normal (from sphere2 to sphere1, but we want geom1 to geom2)
    // OimoPhysics: normal points from geom1's contact point to geom2's
    oimo_detector_set_normal(&detector->base, result, &n);

    // Compute contact positions
    // pos1 = center1 - normal * r1 (point on sphere1 surface)
    // pos2 = center2 + normal * r2 (point on sphere2 surface)
    OimoVec3 pos1, pos2;
    OimoVec3 scaled_n;

    oimo_vec3_scale_to(&scaled_n, &n, -r1);
    oimo_vec3_add_to(&pos1, &tf1->position, &scaled_n);

    oimo_vec3_scale_to(&scaled_n, &n, r2);
    oimo_vec3_add_to(&pos2, &tf2->position, &scaled_n);

    // Penetration depth
    OimoScalar depth = sum_radii - len;

    oimo_detector_add_point(&detector->base, result, &pos1, &pos2, depth, 0);
}

#ifdef __cplusplus
}
#endif
