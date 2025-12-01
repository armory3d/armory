/**
 * Oimo Physics - N64 Port
 * Detector - Base collision detector functions
 *
 * Based on OimoPhysics by saharan
 * https://github.com/saharan/OimoPhysics
 */

#ifndef OIMO_COLLISION_NARROWPHASE_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_DETECTOR_H

#include "detector_result.h"
#include "../geometry/geometry.h"
#include "../../common/transform.h"
#include "../../common/vec3.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Detector type enumeration - one for each collision pair we support.
 */
typedef enum OimoDetectorType {
    OIMO_DETECTOR_SPHERE_SPHERE = 0,
    OIMO_DETECTOR_SPHERE_BOX = 1,
    OIMO_DETECTOR_BOX_SPHERE = 2,  // Swapped version
    OIMO_DETECTOR_BOX_BOX = 3,
    OIMO_DETECTOR_COUNT
} OimoDetectorType;

/**
 * Base detector structure.
 * Handles swapped geometry pairs (e.g., box-sphere vs sphere-box).
 */
typedef struct OimoDetector {
    OimoDetectorType type;
    bool swapped;  // If true, geometries are swapped from expected order
} OimoDetector;

/**
 * Initialize a detector with swapped flag.
 */
static inline void oimo_detector_init(OimoDetector* detector, OimoDetectorType type, bool swapped) {
    detector->type = type;
    detector->swapped = swapped;
}

/**
 * Set the contact normal, negating if geometries were swapped.
 * The normal should point from geometry1 to geometry2.
 */
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

/**
 * Add a contact point, swapping positions if geometries were swapped.
 */
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

#endif // OIMO_COLLISION_NARROWPHASE_DETECTOR_H

