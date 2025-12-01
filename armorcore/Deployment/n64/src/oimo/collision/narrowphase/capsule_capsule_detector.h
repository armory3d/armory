#ifndef OIMO_COLLISION_NARROWPHASE_CAPSULE_CAPSULE_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_CAPSULE_CAPSULE_DETECTOR_H

#include "detector.h"
#include "detector_result.h"
#include "../geometry/capsule_geometry.h"
#include "../../common/transform.h"
#include "../../common/vec3.h"
#include "../../common/math_util.h"

#ifdef __cplusplus
extern "C" {
#endif

// Capsule vs Capsule detector (matches OimoPhysics)
typedef struct OimoCapsuleCapsuleDetector {
    OimoDetector base;
} OimoCapsuleCapsuleDetector;

static inline void oimo_capsule_capsule_detector_init(OimoCapsuleCapsuleDetector* detector) {
    oimo_detector_init(&detector->base, OIMO_DETECTOR_CAPSULE_CAPSULE, false);
}

static inline void oimo_capsule_capsule_detector_detect(
    OimoCapsuleCapsuleDetector* detector,
    OimoDetectorResult* result,
    const OimoCapsuleGeometry* c1,
    const OimoCapsuleGeometry* c2,
    const OimoTransform* tf1,
    const OimoTransform* tf2)
{
    (void)detector;

    // Y axes (column 1 of rotation matrix)
    OimoVec3 axis1, axis2;
    axis1.x = tf1->rotation.e01;
    axis1.y = tf1->rotation.e11;
    axis1.z = tf1->rotation.e21;

    axis2.x = tf2->rotation.e01;
    axis2.y = tf2->rotation.e11;
    axis2.z = tf2->rotation.e21;

    OimoScalar hh1 = c1->halfHeight;
    OimoScalar hh2 = c2->halfHeight;
    OimoScalar r1 = c1->radius;
    OimoScalar r2 = c2->radius;

    // line segments (p1, q1), (p2, q2)
    OimoVec3 p1, q1, p2, q2;
    p1.x = tf1->position.x - axis1.x * hh1;
    p1.y = tf1->position.y - axis1.y * hh1;
    p1.z = tf1->position.z - axis1.z * hh1;
    q1.x = tf1->position.x + axis1.x * hh1;
    q1.y = tf1->position.y + axis1.y * hh1;
    q1.z = tf1->position.z + axis1.z * hh1;

    p2.x = tf2->position.x - axis2.x * hh2;
    p2.y = tf2->position.y - axis2.y * hh2;
    p2.z = tf2->position.z - axis2.z * hh2;
    q2.x = tf2->position.x + axis2.x * hh2;
    q2.y = tf2->position.y + axis2.y * hh2;
    q2.z = tf2->position.z + axis2.z * hh2;

    // p1 - p2
    OimoVec3 p12;
    p12.x = p1.x - p2.x;
    p12.y = p1.y - p2.y;
    p12.z = p1.z - p2.z;

    // d1 = q1 - p1, d2 = q2 - p2
    OimoVec3 d1, d2;
    d1.x = q1.x - p1.x;
    d1.y = q1.y - p1.y;
    d1.z = q1.z - p1.z;
    d2.x = q2.x - p2.x;
    d2.y = q2.y - p2.y;
    d2.z = q2.z - p2.z;

    OimoScalar p21d1 = -(p12.x * d1.x + p12.y * d1.y + p12.z * d1.z);
    OimoScalar p12d2 = p12.x * d2.x + p12.y * d2.y + p12.z * d2.z;

    OimoScalar d11 = hh1 * hh1 * 4;
    OimoScalar d12 = d1.x * d2.x + d1.y * d2.y + d1.z * d2.z;
    OimoScalar d22 = hh2 * hh2 * 4;

    // closest points: p1 + t1 * d1, p2 + t2 * d2
    OimoScalar t1, t2;

    if (d11 == 0 && d22 == 0) {
        // point vs point
        t1 = 0;
        t2 = 0;
    } else if (d11 == 0) {
        // point vs segment
        t1 = 0;
        // t2 = t1 * d12 + p12d2; <- t1 = 0
        t2 = p12d2;
        if (t2 < 0) t2 = 0;
        else if (t2 > d22) t2 = 1;
        else t2 /= d22;
    } else if (d22 == 0) {
        // segment vs point
        t2 = 0;
        // t1 = t2 * d12 + p21d1; <- t2 = 0
        t1 = p21d1;
        if (t1 < 0) t1 = 0;
        else if (t1 > d11) t1 = 1;
        else t1 /= d11;
    } else {
        OimoScalar det = d11 * d22 - d12 * d12;

        if (det == 0) {
            // d1 is parallel to d2. use 0 for t1
            t1 = 0;
        } else {
            t1 = d12 * p12d2 + d22 * p21d1;
            if (t1 < 0) t1 = 0;
            else if (t1 > det) t1 = 1;
            else t1 /= det;
        }

        t2 = t1 * d12 + p12d2;
        if (t2 < 0) {
            // clamp t2 and recompute t1
            t2 = 0;
            // t1 = t2 * d12 + p21d1; <- t2 = 0
            t1 = p21d1;
            if (t1 < 0) t1 = 0;
            else if (t1 > d11) t1 = 1;
            else t1 /= d11;
        } else if (t2 > d22) {
            // clamp t2 and recompute t1
            t2 = 1;
            // t1 = t2 * d12 + p21d1; <- t2 = 1
            t1 = d12 + p21d1;
            if (t1 < 0) t1 = 0;
            else if (t1 > d11) t1 = 1;
            else t1 /= d11;
        } else {
            t2 /= d22;
        }
    }

    // closest points on each segment
    OimoVec3 cp1, cp2;
    cp1.x = p1.x + d1.x * t1;
    cp1.y = p1.y + d1.y * t1;
    cp1.z = p1.z + d1.z * t1;
    cp2.x = p2.x + d2.x * t2;
    cp2.y = p2.y + d2.y * t2;
    cp2.z = p2.z + d2.z * t2;

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

    result->normal = n;

    OimoVec3 pos1, pos2;
    pos1.x = cp1.x - n.x * r1;
    pos1.y = cp1.y - n.y * r1;
    pos1.z = cp1.z - n.z * r1;
    pos2.x = cp2.x + n.x * r2;
    pos2.y = cp2.y + n.y * r2;
    pos2.z = cp2.z + n.z * r2;

    oimo_detector_result_add_point(result, &pos1, &pos2, r1 + r2 - len, 0);
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_CAPSULE_CAPSULE_DETECTOR_H
