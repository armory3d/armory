#pragma once

#include "../../common/vec3.h"
#include "../../common/setting.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoDetectorResultPoint {
    OimoVec3 position1;  // Closest point on first geometry (world space)
    OimoVec3 position2;  // Closest point on second geometry (world space)
    OimoScalar depth;    // Penetration depth (positive = overlapping)
    int id;              // Point ID for contact persistence
} OimoDetectorResultPoint;

static inline void oimo_detector_result_point_init(OimoDetectorResultPoint* point) {
    oimo_vec3_set(&point->position1, 0.0f, 0.0f, 0.0f);
    oimo_vec3_set(&point->position2, 0.0f, 0.0f, 0.0f);
    point->depth = 0.0f;
    point->id = 0;
}

typedef struct OimoDetectorResult {
    int num_points;                                    // Number of valid contact points
    OimoDetectorResultPoint points[OIMO_MAX_MANIFOLD_POINTS]; // Contact points array
    OimoVec3 normal;                                   // Contact normal (from geom1 to geom2)
    bool incremental;                                  // For GJK/EPA incremental results
} OimoDetectorResult;

static inline void oimo_detector_result_init(OimoDetectorResult* result) {
    result->num_points = 0;
    oimo_vec3_set(&result->normal, 0.0f, 0.0f, 0.0f);
    result->incremental = false;
    for (int i = 0; i < OIMO_MAX_MANIFOLD_POINTS; i++) {
        oimo_detector_result_point_init(&result->points[i]);
    }
}

static inline void oimo_detector_result_clear(OimoDetectorResult* result) {
    result->num_points = 0;
    oimo_vec3_set(&result->normal, 0.0f, 0.0f, 0.0f);
    result->incremental = false;
}

// Create and return a zero-initialized detector result
static inline OimoDetectorResult oimo_detector_result_create(void) {
    OimoDetectorResult result;
    result.num_points = 0;
    oimo_vec3_set(&result.normal, 0.0f, 0.0f, 0.0f);
    result.incremental = false;
    for (int i = 0; i < OIMO_MAX_MANIFOLD_POINTS; i++) {
        oimo_detector_result_point_init(&result.points[i]);
    }
    return result;
}

static inline OimoScalar oimo_detector_result_get_max_depth(const OimoDetectorResult* result) {
    OimoScalar max_depth = 0.0f;
    for (int i = 0; i < result->num_points; i++) {
        if (result->points[i].depth > max_depth) {
            max_depth = result->points[i].depth;
        }
    }
    return max_depth;
}

static inline bool oimo_detector_result_add_point(
    OimoDetectorResult* result,
    const OimoVec3* pos1,
    const OimoVec3* pos2,
    OimoScalar depth,
    int id
) {
    if (result->num_points >= OIMO_MAX_MANIFOLD_POINTS) {
        return false;
    }

    OimoDetectorResultPoint* point = &result->points[result->num_points];
    point->position1 = *pos1;
    point->position2 = *pos2;
    point->depth = depth;
    point->id = id;
    result->num_points++;

    return true;
}

#ifdef __cplusplus
}
#endif

