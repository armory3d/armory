#pragma once

#include "detector.h"
#include "detector_result.h"
#include "../geometry/box_geometry.h"
#include "../geometry/capsule_geometry.h"
#include "../../common/transform.h"
#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/math_util.h"

#ifdef __cplusplus
extern "C" {
#endif

// Box vs Capsule detector
// Analytical approach: find closest point on capsule segment to box
typedef struct OimoBoxCapsuleDetector {
    OimoDetector base;
    bool swapped;  // true if capsule is geom1, box is geom2
} OimoBoxCapsuleDetector;

static inline void oimo_box_capsule_detector_init(OimoBoxCapsuleDetector* detector, bool swapped) {
    oimo_detector_init(&detector->base, swapped ? OIMO_DETECTOR_CAPSULE_BOX : OIMO_DETECTOR_BOX_CAPSULE, swapped);
    detector->swapped = swapped;
}

// Clamp a point to box bounds
static inline OimoVec3 oimo_clamp_to_box(const OimoVec3* p, const OimoVec3* halfExt) {
    OimoVec3 result;
    result.x = oimo_clamp(p->x, -halfExt->x, halfExt->x);
    result.y = oimo_clamp(p->y, -halfExt->y, halfExt->y);
    result.z = oimo_clamp(p->z, -halfExt->z, halfExt->z);
    return result;
}

// Compute squared distance from point to clamped point on box
static inline OimoScalar oimo_point_to_box_dist2(const OimoVec3* p, const OimoVec3* halfExt) {
    OimoVec3 clamped = oimo_clamp_to_box(p, halfExt);
    OimoScalar dx = p->x - clamped.x;
    OimoScalar dy = p->y - clamped.y;
    OimoScalar dz = p->z - clamped.z;
    return dx*dx + dy*dy + dz*dz;
}

// Find closest point on segment [p, q] to box
// Returns the closest point on segment and the closest point on box
static inline void oimo_closest_segment_box(
    const OimoVec3* p, const OimoVec3* q,
    const OimoVec3* halfExt,
    OimoVec3* closestOnSeg,
    OimoVec3* closestOnBox)
{
    OimoVec3 d;
    d.x = q->x - p->x;
    d.y = q->y - p->y;
    d.z = q->z - p->z;

    OimoScalar segLen2 = d.x*d.x + d.y*d.y + d.z*d.z;

    if (segLen2 < OIMO_EPSILON) {
        // Degenerate segment (point)
        *closestOnSeg = *p;
        *closestOnBox = oimo_clamp_to_box(p, halfExt);
        return;
    }

    // We'll find the t that minimizes distance from segment point to box
    // The distance function is piecewise and convex, so we can use a simple approach:
    // 1. Test endpoints
    // 2. For each box face/edge/corner region, solve for the closest t analytically

    // For simplicity and robustness, use ternary search on the convex distance function
    OimoScalar lo = 0.0f;
    OimoScalar hi = 1.0f;

    for (int iter = 0; iter < 16; iter++) {
        OimoScalar m1 = lo + (hi - lo) / 3.0f;
        OimoScalar m2 = hi - (hi - lo) / 3.0f;

        OimoVec3 pt1, pt2;
        pt1.x = p->x + d.x * m1;
        pt1.y = p->y + d.y * m1;
        pt1.z = p->z + d.z * m1;
        pt2.x = p->x + d.x * m2;
        pt2.y = p->y + d.y * m2;
        pt2.z = p->z + d.z * m2;

        OimoScalar dist1 = oimo_point_to_box_dist2(&pt1, halfExt);
        OimoScalar dist2 = oimo_point_to_box_dist2(&pt2, halfExt);

        if (dist1 < dist2) {
            hi = m2;
        } else {
            lo = m1;
        }
    }

    OimoScalar t = (lo + hi) * 0.5f;
    closestOnSeg->x = p->x + d.x * t;
    closestOnSeg->y = p->y + d.y * t;
    closestOnSeg->z = p->z + d.z * t;
    *closestOnBox = oimo_clamp_to_box(closestOnSeg, halfExt);
}

static inline void oimo_box_capsule_detector_detect(
    OimoBoxCapsuleDetector* detector,
    OimoDetectorResult* result,
    const OimoBoxGeometry* box,
    const OimoCapsuleGeometry* capsule,
    const OimoTransform* tfBox,
    const OimoTransform* tfCapsule)
{
    OimoScalar hh = capsule->halfHeight;
    OimoScalar capsuleRadius = capsule->radius;
    OimoVec3 boxHalfExtents = box->half_extents;

    // Get capsule axis in world space (Y axis = column 1)
    OimoVec3 capsuleAxis;
    capsuleAxis.x = tfCapsule->rotation.e01;
    capsuleAxis.y = tfCapsule->rotation.e11;
    capsuleAxis.z = tfCapsule->rotation.e21;

    // Capsule endpoints in world space
    OimoVec3 capP, capQ;
    capP.x = tfCapsule->position.x - capsuleAxis.x * hh;
    capP.y = tfCapsule->position.y - capsuleAxis.y * hh;
    capP.z = tfCapsule->position.z - capsuleAxis.z * hh;
    capQ.x = tfCapsule->position.x + capsuleAxis.x * hh;
    capQ.y = tfCapsule->position.y + capsuleAxis.y * hh;
    capQ.z = tfCapsule->position.z + capsuleAxis.z * hh;

    // Transform capsule endpoints to box local space
    OimoVec3 relP, relQ;
    relP.x = capP.x - tfBox->position.x;
    relP.y = capP.y - tfBox->position.y;
    relP.z = capP.z - tfBox->position.z;
    relQ.x = capQ.x - tfBox->position.x;
    relQ.y = capQ.y - tfBox->position.y;
    relQ.z = capQ.z - tfBox->position.z;

    // Multiply by transpose of rotation (inverse for orthonormal matrix)
    OimoVec3 localP, localQ;
    localP.x = tfBox->rotation.e00 * relP.x + tfBox->rotation.e10 * relP.y + tfBox->rotation.e20 * relP.z;
    localP.y = tfBox->rotation.e01 * relP.x + tfBox->rotation.e11 * relP.y + tfBox->rotation.e21 * relP.z;
    localP.z = tfBox->rotation.e02 * relP.x + tfBox->rotation.e12 * relP.y + tfBox->rotation.e22 * relP.z;

    localQ.x = tfBox->rotation.e00 * relQ.x + tfBox->rotation.e10 * relQ.y + tfBox->rotation.e20 * relQ.z;
    localQ.y = tfBox->rotation.e01 * relQ.x + tfBox->rotation.e11 * relQ.y + tfBox->rotation.e21 * relQ.z;
    localQ.z = tfBox->rotation.e02 * relQ.x + tfBox->rotation.e12 * relQ.y + tfBox->rotation.e22 * relQ.z;

    // Find closest points between segment and box in local space
    OimoVec3 closestOnSeg, closestOnBox;
    oimo_closest_segment_box(&localP, &localQ, &boxHalfExtents, &closestOnSeg, &closestOnBox);

    // Compute separation vector in local space
    OimoVec3 diff;
    diff.x = closestOnSeg.x - closestOnBox.x;
    diff.y = closestOnSeg.y - closestOnBox.y;
    diff.z = closestOnSeg.z - closestOnBox.z;

    OimoScalar dist2 = diff.x * diff.x + diff.y * diff.y + diff.z * diff.z;

    // Check if the sphere around the closest segment point penetrates the box
    if (dist2 >= capsuleRadius * capsuleRadius) {
        return;  // No collision
    }

    OimoScalar dist = oimo_sqrt(dist2);
    OimoVec3 localNormal;

    if (dist > OIMO_EPSILON) {
        // Normal points from box to capsule segment
        OimoScalar invDist = 1.0f / dist;
        localNormal.x = diff.x * invDist;
        localNormal.y = diff.y * invDist;
        localNormal.z = diff.z * invDist;
    } else {
        // Segment point is inside box - find closest face normal
        OimoScalar dx = boxHalfExtents.x - oimo_abs(closestOnSeg.x);
        OimoScalar dy = boxHalfExtents.y - oimo_abs(closestOnSeg.y);
        OimoScalar dz = boxHalfExtents.z - oimo_abs(closestOnSeg.z);

        if (dx <= dy && dx <= dz) {
            localNormal.x = closestOnSeg.x >= 0 ? 1.0f : -1.0f;
            localNormal.y = 0;
            localNormal.z = 0;
        } else if (dy <= dz) {
            localNormal.x = 0;
            localNormal.y = closestOnSeg.y >= 0 ? 1.0f : -1.0f;
            localNormal.z = 0;
        } else {
            localNormal.x = 0;
            localNormal.y = 0;
            localNormal.z = closestOnSeg.z >= 0 ? 1.0f : -1.0f;
        }
    }

    // Transform normal back to world space
    OimoVec3 worldNormal;
    worldNormal.x = tfBox->rotation.e00 * localNormal.x + tfBox->rotation.e01 * localNormal.y + tfBox->rotation.e02 * localNormal.z;
    worldNormal.y = tfBox->rotation.e10 * localNormal.x + tfBox->rotation.e11 * localNormal.y + tfBox->rotation.e12 * localNormal.z;
    worldNormal.z = tfBox->rotation.e20 * localNormal.x + tfBox->rotation.e21 * localNormal.y + tfBox->rotation.e22 * localNormal.z;

    // Transform contact points to world space
    OimoVec3 pos1;  // Contact on box surface
    pos1.x = tfBox->rotation.e00 * closestOnBox.x + tfBox->rotation.e01 * closestOnBox.y + tfBox->rotation.e02 * closestOnBox.z + tfBox->position.x;
    pos1.y = tfBox->rotation.e10 * closestOnBox.x + tfBox->rotation.e11 * closestOnBox.y + tfBox->rotation.e12 * closestOnBox.z + tfBox->position.y;
    pos1.z = tfBox->rotation.e20 * closestOnBox.x + tfBox->rotation.e21 * closestOnBox.y + tfBox->rotation.e22 * closestOnBox.z + tfBox->position.z;

    // pos2 is on the capsule surface
    OimoVec3 worldClosestOnSeg;
    worldClosestOnSeg.x = tfBox->rotation.e00 * closestOnSeg.x + tfBox->rotation.e01 * closestOnSeg.y + tfBox->rotation.e02 * closestOnSeg.z + tfBox->position.x;
    worldClosestOnSeg.y = tfBox->rotation.e10 * closestOnSeg.x + tfBox->rotation.e11 * closestOnSeg.y + tfBox->rotation.e12 * closestOnSeg.z + tfBox->position.y;
    worldClosestOnSeg.z = tfBox->rotation.e20 * closestOnSeg.x + tfBox->rotation.e21 * closestOnSeg.y + tfBox->rotation.e22 * closestOnSeg.z + tfBox->position.z;

    OimoVec3 pos2;  // Contact on capsule surface
    pos2.x = worldClosestOnSeg.x - worldNormal.x * capsuleRadius;
    pos2.y = worldClosestOnSeg.y - worldNormal.y * capsuleRadius;
    pos2.z = worldClosestOnSeg.z - worldNormal.z * capsuleRadius;

    OimoScalar depth = capsuleRadius - dist;

    // If swapped, flip normal (normal points from geom1 to geom2)
    if (detector->swapped) {
        worldNormal.x = -worldNormal.x;
        worldNormal.y = -worldNormal.y;
        worldNormal.z = -worldNormal.z;
        // Also swap pos1 and pos2
        oimo_detector_add_point(&detector->base, result, &pos2, &pos1, depth, 0);
    } else {
        oimo_detector_add_point(&detector->base, result, &pos1, &pos2, depth, 0);
    }

    oimo_detector_set_normal(&detector->base, result, &worldNormal);
}

#ifdef __cplusplus
}
#endif

