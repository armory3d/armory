#pragma once

#include "detector.h"
#include "detector_result.h"
#include "sphere_sphere_detector.h"
#include "sphere_box_detector.h"
#include "box_box_detector.h"
#include "capsule_capsule_detector.h"
#include "sphere_capsule_detector.h"
#include "box_capsule_detector.h"
#include "sphere_mesh_detector.h"
#include "box_mesh_detector.h"
#include "capsule_mesh_detector.h"
#include "../geometry/geometry_type.h"
#include "../geometry/sphere_geometry.h"
#include "../geometry/box_geometry.h"
#include "../geometry/capsule_geometry.h"
#include "../geometry/static_mesh_geometry.h"
#include "../../common/transform.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct OimoCollisionMatrix {
    OimoSphereSphereDetector sphere_sphere;
    OimoSphereBoxDetector sphere_box;      // sphere is geom1
    OimoSphereBoxDetector box_sphere;      // box is geom1 (swapped)
    OimoBoxBoxDetector box_box;
    OimoCapsuleCapsuleDetector capsule_capsule;
    OimoSphereCapsuleDetector sphere_capsule;  // sphere is geom1
    OimoSphereCapsuleDetector capsule_sphere;  // capsule is geom1 (swapped)
    OimoBoxCapsuleDetector box_capsule;        // box is geom1
    OimoBoxCapsuleDetector capsule_box;        // capsule is geom1 (swapped)
    // Mesh detectors
    OimoSphereMeshDetector sphere_mesh;
    OimoSphereMeshDetector mesh_sphere;
    OimoBoxMeshDetector box_mesh;
    OimoBoxMeshDetector mesh_box;
    OimoCapsuleMeshDetector capsule_mesh;
    OimoCapsuleMeshDetector mesh_capsule;
} OimoCollisionMatrix;

static inline void oimo_collision_matrix_init(OimoCollisionMatrix* matrix) {
    oimo_sphere_sphere_detector_init(&matrix->sphere_sphere);
    oimo_sphere_box_detector_init(&matrix->sphere_box, false);  // sphere-box order
    oimo_sphere_box_detector_init(&matrix->box_sphere, true);   // box-sphere order (swapped)
    oimo_box_box_detector_init(&matrix->box_box);
    oimo_capsule_capsule_detector_init(&matrix->capsule_capsule);
    oimo_sphere_capsule_detector_init(&matrix->sphere_capsule, false);  // sphere-capsule order
    oimo_sphere_capsule_detector_init(&matrix->capsule_sphere, true);   // capsule-sphere order (swapped)
    oimo_box_capsule_detector_init(&matrix->box_capsule, false);        // box-capsule order
    oimo_box_capsule_detector_init(&matrix->capsule_box, true);         // capsule-box order (swapped)
    // Mesh detectors
    oimo_sphere_mesh_detector_init(&matrix->sphere_mesh, false);
    oimo_sphere_mesh_detector_init(&matrix->mesh_sphere, true);
    oimo_box_mesh_detector_init(&matrix->box_mesh, false);
    oimo_box_mesh_detector_init(&matrix->mesh_box, true);
    oimo_capsule_mesh_detector_init(&matrix->capsule_mesh, false);
    oimo_capsule_mesh_detector_init(&matrix->mesh_capsule, true);
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
    if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_CAPSULE) {
        return &matrix->capsule_capsule.base;
    }
    if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_CAPSULE) {
        return &matrix->sphere_capsule.base;
    }
    if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_SPHERE) {
        return &matrix->capsule_sphere.base;
    }
    if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_CAPSULE) {
        return &matrix->box_capsule.base;
    }
    if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_BOX) {
        return &matrix->capsule_box.base;
    }
    // Mesh collisions
    if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_STATIC_MESH) {
        return &matrix->sphere_mesh.base;
    }
    if (type1 == OIMO_GEOMETRY_STATIC_MESH && type2 == OIMO_GEOMETRY_SPHERE) {
        return &matrix->mesh_sphere.base;
    }
    if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_STATIC_MESH) {
        return &matrix->box_mesh.base;
    }
    if (type1 == OIMO_GEOMETRY_STATIC_MESH && type2 == OIMO_GEOMETRY_BOX) {
        return &matrix->mesh_box.base;
    }
    if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_STATIC_MESH) {
        return &matrix->capsule_mesh.base;
    }
    if (type1 == OIMO_GEOMETRY_STATIC_MESH && type2 == OIMO_GEOMETRY_CAPSULE) {
        return &matrix->mesh_capsule.base;
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
    // Capsule collisions
    else if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_CAPSULE) {
        oimo_capsule_capsule_detector_detect(
            &matrix->capsule_capsule,
            result,
            (const OimoCapsuleGeometry*)geom1,
            (const OimoCapsuleGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_CAPSULE) {
        oimo_sphere_capsule_detector_detect(
            &matrix->sphere_capsule,
            result,
            (const OimoSphereGeometry*)geom1,
            (const OimoCapsuleGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_SPHERE) {
        // Capsule-sphere: pass sphere first, capsule second (swapped detector handles normal flip)
        oimo_sphere_capsule_detector_detect(
            &matrix->capsule_sphere,
            result,
            (const OimoSphereGeometry*)geom2,  // sphere
            (const OimoCapsuleGeometry*)geom1, // capsule
            tf2, tf1);  // transforms also swapped
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_CAPSULE) {
        oimo_box_capsule_detector_detect(
            &matrix->box_capsule,
            result,
            (const OimoBoxGeometry*)geom1,
            (const OimoCapsuleGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_BOX) {
        // Capsule-box: pass box first, capsule second (swapped detector handles normal flip)
        oimo_box_capsule_detector_detect(
            &matrix->capsule_box,
            result,
            (const OimoBoxGeometry*)geom2,     // box
            (const OimoCapsuleGeometry*)geom1, // capsule
            tf2, tf1);  // transforms also swapped
        return true;
    }
    // Mesh collisions
    else if (type1 == OIMO_GEOMETRY_SPHERE && type2 == OIMO_GEOMETRY_STATIC_MESH) {
        oimo_sphere_mesh_detector_detect(
            &matrix->sphere_mesh,
            result,
            (const OimoSphereGeometry*)geom1,
            (const OimoStaticMeshGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_STATIC_MESH && type2 == OIMO_GEOMETRY_SPHERE) {
        oimo_sphere_mesh_detector_detect(
            &matrix->mesh_sphere,
            result,
            (const OimoSphereGeometry*)geom2,
            (const OimoStaticMeshGeometry*)geom1,
            tf2, tf1);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_BOX && type2 == OIMO_GEOMETRY_STATIC_MESH) {
        oimo_box_mesh_detector_detect(
            &matrix->box_mesh,
            result,
            (const OimoBoxGeometry*)geom1,
            (const OimoStaticMeshGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_STATIC_MESH && type2 == OIMO_GEOMETRY_BOX) {
        oimo_box_mesh_detector_detect(
            &matrix->mesh_box,
            result,
            (const OimoBoxGeometry*)geom2,
            (const OimoStaticMeshGeometry*)geom1,
            tf2, tf1);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_CAPSULE && type2 == OIMO_GEOMETRY_STATIC_MESH) {
        oimo_capsule_mesh_detector_detect(
            &matrix->capsule_mesh,
            result,
            (const OimoCapsuleGeometry*)geom1,
            (const OimoStaticMeshGeometry*)geom2,
            tf1, tf2);
        return true;
    }
    else if (type1 == OIMO_GEOMETRY_STATIC_MESH && type2 == OIMO_GEOMETRY_CAPSULE) {
        oimo_capsule_mesh_detector_detect(
            &matrix->mesh_capsule,
            result,
            (const OimoCapsuleGeometry*)geom2,
            (const OimoStaticMeshGeometry*)geom1,
            tf2, tf1);
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
    if (geom_type1 == OIMO_GEOMETRY_CAPSULE && geom_type2 == OIMO_GEOMETRY_CAPSULE) {
        return OIMO_DETECTOR_CAPSULE_CAPSULE;
    }
    if (geom_type1 == OIMO_GEOMETRY_SPHERE && geom_type2 == OIMO_GEOMETRY_CAPSULE) {
        return OIMO_DETECTOR_SPHERE_CAPSULE;
    }
    if (geom_type1 == OIMO_GEOMETRY_CAPSULE && geom_type2 == OIMO_GEOMETRY_SPHERE) {
        return OIMO_DETECTOR_CAPSULE_SPHERE;
    }
    if (geom_type1 == OIMO_GEOMETRY_BOX && geom_type2 == OIMO_GEOMETRY_CAPSULE) {
        return OIMO_DETECTOR_BOX_CAPSULE;
    }
    if (geom_type1 == OIMO_GEOMETRY_CAPSULE && geom_type2 == OIMO_GEOMETRY_BOX) {
        return OIMO_DETECTOR_CAPSULE_BOX;
    }
    // Mesh collisions
    if (geom_type1 == OIMO_GEOMETRY_SPHERE && geom_type2 == OIMO_GEOMETRY_STATIC_MESH) {
        return OIMO_DETECTOR_SPHERE_MESH;
    }
    if (geom_type1 == OIMO_GEOMETRY_STATIC_MESH && geom_type2 == OIMO_GEOMETRY_SPHERE) {
        return OIMO_DETECTOR_MESH_SPHERE;
    }
    if (geom_type1 == OIMO_GEOMETRY_BOX && geom_type2 == OIMO_GEOMETRY_STATIC_MESH) {
        return OIMO_DETECTOR_BOX_MESH;
    }
    if (geom_type1 == OIMO_GEOMETRY_STATIC_MESH && geom_type2 == OIMO_GEOMETRY_BOX) {
        return OIMO_DETECTOR_MESH_BOX;
    }
    if (geom_type1 == OIMO_GEOMETRY_CAPSULE && geom_type2 == OIMO_GEOMETRY_STATIC_MESH) {
        return OIMO_DETECTOR_CAPSULE_MESH;
    }
    if (geom_type1 == OIMO_GEOMETRY_STATIC_MESH && geom_type2 == OIMO_GEOMETRY_CAPSULE) {
        return OIMO_DETECTOR_MESH_CAPSULE;
    }
    return (OimoDetectorType)-1;  // Unsupported
}

#ifdef __cplusplus
}
#endif

