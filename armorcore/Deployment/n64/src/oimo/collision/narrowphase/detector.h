#ifndef OIMO_COLLISION_NARROWPHASE_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_DETECTOR_H

#include "detector_result.h"
#include "../geometry/geometry.h"
#include "../../common/transform.h"
#include "../../common/vec3.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum OimoDetectorType {
    OIMO_DETECTOR_SPHERE_SPHERE = 0,
    OIMO_DETECTOR_SPHERE_BOX = 1,
    OIMO_DETECTOR_BOX_SPHERE = 2,
    OIMO_DETECTOR_BOX_BOX = 3,
    OIMO_DETECTOR_SPHERE_CAPSULE = 4,
    OIMO_DETECTOR_CAPSULE_SPHERE = 5,
    OIMO_DETECTOR_CAPSULE_CAPSULE = 6,
    OIMO_DETECTOR_BOX_CAPSULE = 7,
    OIMO_DETECTOR_CAPSULE_BOX = 8,
    OIMO_DETECTOR_SPHERE_MESH = 9,
    OIMO_DETECTOR_MESH_SPHERE = 10,
    OIMO_DETECTOR_BOX_MESH = 11,
    OIMO_DETECTOR_MESH_BOX = 12,
    OIMO_DETECTOR_CAPSULE_MESH = 13,
    OIMO_DETECTOR_MESH_CAPSULE = 14,
    OIMO_DETECTOR_COUNT
} OimoDetectorType;

typedef struct OimoDetector {
    OimoDetectorType type;
    bool swapped;
} OimoDetector;

static inline void oimo_detector_init(OimoDetector* detector, OimoDetectorType type, bool swapped) {
    detector->type = type;
    detector->swapped = swapped;
}

static inline void oimo_detector_set_normal(
    OimoDetector* detector,
    OimoDetectorResult* result,
    const OimoVec3* normal
) {
    if (detector->swapped) {
        oimo_vec3_negate_to(&result->normal, normal);
    } else {
        result->normal = *normal;
    }
}

static inline void oimo_detector_add_point(
    OimoDetector* detector,
    OimoDetectorResult* result,
    const OimoVec3* pos1,
    const OimoVec3* pos2,
    OimoScalar depth,
    int id
) {
    if (detector->swapped) {
        oimo_detector_result_add_point(result, pos2, pos1, depth, id);
    } else {
        oimo_detector_result_add_point(result, pos1, pos2, depth, id);
    }
}

#ifdef __cplusplus
}
#endif

#endif

