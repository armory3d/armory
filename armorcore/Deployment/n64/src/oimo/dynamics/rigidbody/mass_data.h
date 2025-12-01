#ifndef OIMO_DYNAMICS_RIGIDBODY_MASS_DATA_H
#define OIMO_DYNAMICS_RIGIDBODY_MASS_DATA_H

#include "../../common/mat3.h"

typedef struct OimoMassData {
    OimoScalar mass;           // Mass (0 for non-dynamic)
    OimoMat3 localInertia;     // Inertia tensor in local space
} OimoMassData;

static inline void oimo_mass_data_init(OimoMassData* md) {
    md->mass = 0;
    md->localInertia = oimo_mat3_zero();
}

static inline OimoMassData oimo_mass_data(void) {
    OimoMassData md;
    oimo_mass_data_init(&md);
    return md;
}

#endif // OIMO_DYNAMICS_RIGIDBODY_MASS_DATA_H
