#ifndef OIMO_COLLISION_NARROWPHASE_COLLISION_MATRIX_H
#define OIMO_COLLISION_NARROWPHASE_COLLISION_MATRIX_H

#include "detector.h"
#include "detector_result.h"
#include "sphere_sphere_detector.h"
#include "sphere_box_detector.h"
#include "box_box_detector.h"
#include "../geometry/geometry_type.h"
#include "../geometry/sphere_geometry.h"
#include "../geometry/box_geometry.h"
#include "../../common/transform.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoCollisionMatrix {
    OimoSphereSphereDetector sphere_sphere;
    OimoSphereBoxDetector sphere_box;      // sphere is geom1
    OimoSphereBoxDetector box_sphere;      // box is geom1 (swapped)
    OimoBoxBoxDetector box_box;
} OimoCollisionMatrix;

static inline void oimo_collision_matrix_init(OimoCollisionMatrix* matrix) {
    oimo_sphere_sphere_detector_init(&matrix->sphere_sphere);
    oimo_sphere_box_detector_init(&matrix->sphere_box, false);  // sphere-box order
    oimo_sphere_box_detector_init(&matrix->box_sphere, true);   // box-sphere order (swapped)
    oimo_box_box_detector_init(&matrix->box_box);
}

static inline OimoCollisionMatrix oimo_collision_matrix_create(void) {
    OimoCollisionMatrix matrix;
    oimo_collision_matrix_init(&matrix);
    return matrix;
}

// Get a detector pointer for the given geometry types (for storing in contacts)
static inline OimoDetector* oimo_collision_matrix_get_detector(
    OimoCollisionMatrix* matrix,
    OimoGeometryType type1,
    OimoGeometryType type2)
{
    if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_SPHERE) {
        return &matrix->sphere_sphere.base;
    }
    if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_BOX) {
        return &matrix->sphere_box.base;
    }
    if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_SPHERE) {
        return &matrix->box_sphere.base;
    }
    if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_BOX) {
        return &matrix->box_box.base;
    }
    return NULL;
}

static inline bool oimo_collision_matrix_detect(
    OimoCollisionMatrix* matrix,
    OimoDetectorResult* result,
    const OimoGeometry* geom1,
    const OimoGeometry* geom2,
    const OimoTransform* tf1,
    const OimoTransform* tf2)
{
    oimo_detector_result_clear(result);

    int type1 = geom1->type;
    int type2 = geom2->type;

    // Dispatch based on geometry types
    if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_SPHERE) {
        oimo_sphere_sphere_detector_detect(
            &matrix->sphere_sphere,
            result,
            (const OimoSphereGeometry*)geom1,
            (const OimoSphereGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_BOX) {
        oimo_sphere_box_detector_detect(
            &matrix->sphere_box,
            result,
            (const OimoSphereGeometry*)geom1,
            (const OimoBoxGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_SPHERE) {
        // Box-sphere: pass box as "sphere" position, sphere as "box" position
        // The detector internally handles the swap
        oimo_sphere_box_detector_detect(
            &matrix->box_sphere,
            result,
            (const OimoSphereGeometry*)geom2,  // sphere
            (const OimoBoxGeometry*)geom1,     // box
            tf2, tf1);  // transforms also swapped
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_BOX) {
        oimo_box_box_detector_detect(
            &matrix->box_box,
            result,
            (const OimoBoxGeometry*)geom1,
            (const OimoBoxGeometry*)geom2,
            tf1, tf2);
        return true;
    }

    // Unsupported geometry combination
    return false;
}

static inline OimoDetectorType oimo_collision_matrix_get_detector_type(int geom_type1, int geom_type2) {
    if (geom_type1 == OIMO_GEOMETRY_SPHERE && geom_type2 == OIMO_GEOMETRY_SPHERE) {
        return OIMO_DETECTOR_SPHERE_SPHERE;
    }
    if (geom_type1 == OIMO_GEOMETRY_SPHERE && geom_type2 == OIMO_GEOMETRY_BOX) {
        return OIMO_DETECTOR_SPHERE_BOX;
    }
    if (geom_type1 == OIMO_GEOMETRY_BOX && geom_type2 == OIMO_GEOMETRY_SPHERE) {
        return OIMO_DETECTOR_BOX_SPHERE;
    }
    if (geom_type1 == OIMO_GEOMETRY_BOX && geom_type2 == OIMO_GEOMETRY_BOX) {
        return OIMO_DETECTOR_BOX_BOX;
    }
    return (OimoDetectorType)-1;  // Unsupported
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_COLLISION_MATRIX_H
