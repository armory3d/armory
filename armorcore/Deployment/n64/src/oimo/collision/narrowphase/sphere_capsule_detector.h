#pragma once

#include "detector.h"
#include "detector_result.h"
#include "../geometry/capsule_geometry.h"
#include "../geometry/sphere_geometry.h"
#include "../../common/transform.h"
#include "../../common/vec3.h"
#include "../../common/math_util.h"

#ifdef __cplusplus
extern "C" {
#endif

// Sphere vs Capsule detector (matches OimoPhysics)
// If swapped is true, expects CapsuleGeometry and SphereGeometry
// If swapped is false, expects SphereGeometry and CapsuleGeometry
typedef struct OimoSphereCapsuleDetector {
    OimoDetector base;
    bool swapped;
} OimoSphereCapsuleDetector;

static inline void oimo_sphere_capsule_detector_init(OimoSphereCapsuleDetector* detector, bool swapped) {
    oimo_detector_init(&detector->base, swapped ? OIMO_DETECTOR_CAPSULE_SPHERE : OIMO_DETECTOR_SPHERE_CAPSULE, swapped);
    detector->swapped = swapped;
}

// Always called with sphere as s1, capsule as c2 (handles swapped internally via result normal)
static inline void oimo_sphere_capsule_detector_detect(
    OimoSphereCapsuleDetector* detector,
    OimoDetectorResult* result,
    const OimoSphereGeometry* s1,
    const OimoCapsuleGeometry* c2,
    const OimoTransform* tf1,
    const OimoTransform* tf2)
{
    OimoScalar hh2 = c2->halfHeight;
    OimoScalar r1 = s1->radius;
    OimoScalar r2 = c2->radius;

    // capsule axis (Y axis = column 1)
    OimoVec3 axis2;
    axis2.x = tf2->rotation.e01;
    axis2.y = tf2->rotation.e11;
    axis2.z = tf2->rotation.e21;

    // closest point 1 is just sphere center
    OimoVec3 cp1;
    cp1.x = tf1->position.x;
    cp1.y = tf1->position.y;
    cp1.z = tf1->position.z;

    // find closest point on segment 2
    // line segment (p2, q2)
    OimoVec3 p2, q2;
    p2.x = tf2->position.x - axis2.x * hh2;
    p2.y = tf2->position.y - axis2.y * hh2;
    p2.z = tf2->position.z - axis2.z * hh2;
    q2.x = tf2->position.x + axis2.x * hh2;
    q2.y = tf2->position.y + axis2.y * hh2;
    q2.z = tf2->position.z + axis2.z * hh2;

    // p12 = cp1 - p2
    OimoVec3 p12;
    p12.x = cp1.x - p2.x;
    p12.y = cp1.y - p2.y;
    p12.z = cp1.z - p2.z;

    // d2 = q2 - p2
    OimoVec3 d2;
    d2.x = q2.x - p2.x;
    d2.y = q2.y - p2.y;
    d2.z = q2.z - p2.z;

    OimoScalar d22 = hh2 * hh2 * 4;

    OimoScalar t = p12.x * d2.x + p12.y * d2.y + p12.z * d2.z;
    if (t < 0) t = 0;
    else if (t > d22) t = 1;
    else t /= d22;

    OimoVec3 cp2;
    cp2.x = p2.x + d2.x * t;
    cp2.y = p2.y + d2.y * t;
    cp2.z = p2.z + d2.z * t;

    // perform sphere vs sphere collision
    OimoVec3 d;
    d.x = cp1.x - cp2.x;
    d.y = cp1.y - cp2.y;
    d.z = cp1.z - cp2.z;

    OimoScalar len2 = d.x * d.x + d.y * d.y + d.z * d.z;
    if (len2 >= (r1 + r2) * (r1 + r2)) return;

    OimoScalar len = oimo_sqrt(len2);
    OimoVec3 n;
    if (len > 0) {
        OimoScalar invLen = 1.0f / len;
        n.x = d.x * invLen;
        n.y = d.y * invLen;
        n.z = d.z * invLen;
    } else {
        n.x = 1;
        n.y = 0;
        n.z = 0;
    }

    // If swapped, flip normal
    if (detector->swapped) {
        n.x = -n.x;
        n.y = -n.y;
        n.z = -n.z;
    }

    result->normal = n;

    OimoVec3 pos1, pos2;
    if (detector->swapped) {
        // Normal points from capsule to sphere
        pos1.x = cp2.x - n.x * r2;
        pos1.y = cp2.y - n.y * r2;
        pos1.z = cp2.z - n.z * r2;
        pos2.x = cp1.x + n.x * r1;
        pos2.y = cp1.y + n.y * r1;
        pos2.z = cp1.z + n.z * r1;
    } else {
        // Normal points from sphere to capsule
        pos1.x = cp1.x - n.x * r1;
        pos1.y = cp1.y - n.y * r1;
        pos1.z = cp1.z - n.z * r1;
        pos2.x = cp2.x + n.x * r2;
        pos2.y = cp2.y + n.y * r2;
        pos2.z = cp2.z + n.z * r2;
    }

    oimo_detector_result_add_point(result, &pos1, &pos2, r1 + r2 - len, 0);
}

#ifdef __cplusplus
}
#endif

