// contact_impulse.h
// 1:1 port from OimoPhysics ContactImpulse.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_CONTACT_IMPULSE_H
#define OIMO_DYNAMICS_CONSTRAINT_CONTACT_IMPULSE_H

#include "../../../common/vec3.h"

typedef struct OimoContactImpulse {
    OimoScalar impulseN;  // Normal impulse
    OimoScalar impulseT;  // Tangent impulse
    OimoScalar impulseB;  // Binormal impulse
    OimoScalar impulseP;  // Position impulse
    OimoVec3 impulseL;    // Lateral impulse
} OimoContactImpulse;

static inline OimoContactImpulse oimo_contact_impulse_create(void) {
    OimoContactImpulse imp;
    imp.impulseN = 0.0f;
    imp.impulseT = 0.0f;
    imp.impulseB = 0.0f;
    imp.impulseP = 0.0f;
    imp.impulseL = oimo_vec3_zero();
    return imp;
}

static inline void oimo_contact_impulse_clear(OimoContactImpulse* imp) {
    imp->impulseN = 0.0f;
    imp->impulseT = 0.0f;
    imp->impulseB = 0.0f;
    imp->impulseP = 0.0f;
    imp->impulseL = oimo_vec3_zero();
}

static inline void oimo_contact_impulse_copy_from(OimoContactImpulse* dst, const OimoContactImpulse* src) {
    dst->impulseN = src->impulseN;
    dst->impulseT = src->impulseT;
    dst->impulseB = src->impulseB;
    dst->impulseL = src->impulseL;
}

#endif // OIMO_DYNAMICS_CONSTRAINT_CONTACT_IMPULSE_H
