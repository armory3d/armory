// manifold_point.h
// 1:1 port from OimoPhysics ManifoldPoint.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_POINT_H
#define OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_POINT_H

#include "../../../common/vec3.h"
#include "../../../common/mat3.h"
#include "../../../common/transform.h"
#include "../../../collision/narrowphase/detector_result.h"
#include "contact_impulse.h"

typedef struct OimoManifoldPoint {
    // Local position relative to rigid bodies (NOT shapes)
    OimoVec3 _localPos1;
    OimoVec3 _localPos2;

    // Local position with rotation applied
    OimoVec3 _relPos1;
    OimoVec3 _relPos2;

    // World position
    OimoVec3 _pos1;
    OimoVec3 _pos2;

    OimoScalar _depth;
    OimoContactImpulse _impulse;

    bool _warmStarted;
    bool _disabled;
    int _id;
} OimoManifoldPoint;

static inline OimoManifoldPoint oimo_manifold_point_create(void) {
    OimoManifoldPoint mp;
    mp._localPos1 = oimo_vec3_zero();
    mp._localPos2 = oimo_vec3_zero();
    mp._relPos1 = oimo_vec3_zero();
    mp._relPos2 = oimo_vec3_zero();
    mp._pos1 = oimo_vec3_zero();
    mp._pos2 = oimo_vec3_zero();
    mp._depth = 0.0f;
    mp._impulse = oimo_contact_impulse_create();
    mp._warmStarted = false;
    mp._disabled = false;
    mp._id = -1;
    return mp;
}

static inline void oimo_manifold_point_clear(OimoManifoldPoint* mp) {
    mp->_localPos1 = oimo_vec3_zero();
    mp->_localPos2 = oimo_vec3_zero();
    mp->_relPos1 = oimo_vec3_zero();
    mp->_relPos2 = oimo_vec3_zero();
    mp->_pos1 = oimo_vec3_zero();
    mp->_pos2 = oimo_vec3_zero();
    mp->_depth = 0.0f;
    oimo_contact_impulse_clear(&mp->_impulse);
    mp->_warmStarted = false;
    mp->_disabled = false;
    mp->_id = -1;
}

static inline void oimo_manifold_point_initialize(
    OimoManifoldPoint* mp,
    const OimoDetectorResultPoint* result,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    // World position
    mp->_pos1 = result->position1;
    mp->_pos2 = result->position2;

    // Local position with rotation (relPos = pos - tf.position)
    mp->_relPos1 = oimo_vec3_sub(mp->_pos1, tf1->position);
    mp->_relPos2 = oimo_vec3_sub(mp->_pos2, tf2->position);

    // Local position (localPos = R^T * relPos)
    mp->_localPos1 = oimo_mat3_tmul_vec3(&tf1->rotation, mp->_relPos1);
    mp->_localPos2 = oimo_mat3_tmul_vec3(&tf2->rotation, mp->_relPos2);

    mp->_depth = result->depth;
    oimo_contact_impulse_clear(&mp->_impulse);
    mp->_id = result->id;
    mp->_warmStarted = false;
    mp->_disabled = false;
}

static inline void oimo_manifold_point_update_depth_and_positions(
    OimoManifoldPoint* mp,
    const OimoDetectorResultPoint* result,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    mp->_pos1 = result->position1;
    mp->_pos2 = result->position2;
    mp->_relPos1 = oimo_vec3_sub(mp->_pos1, tf1->position);
    mp->_relPos2 = oimo_vec3_sub(mp->_pos2, tf2->position);
    mp->_localPos1 = oimo_mat3_tmul_vec3(&tf1->rotation, mp->_relPos1);
    mp->_localPos2 = oimo_mat3_tmul_vec3(&tf2->rotation, mp->_relPos2);
    mp->_depth = result->depth;
}

static inline void oimo_manifold_point_copy_from(OimoManifoldPoint* dst, const OimoManifoldPoint* src) {
    dst->_localPos1 = src->_localPos1;
    dst->_localPos2 = src->_localPos2;
    dst->_relPos1 = src->_relPos1;
    dst->_relPos2 = src->_relPos2;
    dst->_pos1 = src->_pos1;
    dst->_pos2 = src->_pos2;
    dst->_depth = src->_depth;
    oimo_contact_impulse_copy_from(&dst->_impulse, &src->_impulse);
    dst->_id = src->_id;
    dst->_warmStarted = src->_warmStarted;
    dst->_disabled = false;
}

// Public getters
static inline OimoVec3 oimo_manifold_point_get_position1(const OimoManifoldPoint* mp) {
    return mp->_pos1;
}

static inline OimoVec3 oimo_manifold_point_get_position2(const OimoManifoldPoint* mp) {
    return mp->_pos2;
}

static inline OimoScalar oimo_manifold_point_get_depth(const OimoManifoldPoint* mp) {
    return mp->_depth;
}

static inline bool oimo_manifold_point_is_warm_started(const OimoManifoldPoint* mp) {
    return mp->_warmStarted;
}

static inline OimoScalar oimo_manifold_point_get_normal_impulse(const OimoManifoldPoint* mp) {
    return mp->_impulse.impulseN;
}

static inline OimoScalar oimo_manifold_point_get_tangent_impulse(const OimoManifoldPoint* mp) {
    return mp->_impulse.impulseT;
}

static inline OimoScalar oimo_manifold_point_get_binormal_impulse(const OimoManifoldPoint* mp) {
    return mp->_impulse.impulseB;
}

static inline bool oimo_manifold_point_is_enabled(const OimoManifoldPoint* mp) {
    return !mp->_disabled;
}

#endif // OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_POINT_H
