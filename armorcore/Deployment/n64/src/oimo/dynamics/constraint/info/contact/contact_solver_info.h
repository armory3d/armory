// contact_solver_info.h
// 1:1 port from OimoPhysics ContactSolverInfo.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_INFO_CONTACT_SOLVER_INFO_H
#define OIMO_DYNAMICS_CONSTRAINT_INFO_CONTACT_SOLVER_INFO_H

#include "../../../../common/setting.h"
#include "contact_solver_info_row.h"

// Forward declare
struct OimoRigidBody;

typedef struct OimoContactSolverInfo {
    struct OimoRigidBody* b1;
    struct OimoRigidBody* b2;
    int numRows;
    OimoContactSolverInfoRow rows[OIMO_MAX_MANIFOLD_POINTS];
} OimoContactSolverInfo;

static inline OimoContactSolverInfo oimo_contact_solver_info_create(void) {
    OimoContactSolverInfo info;
    info.b1 = NULL;
    info.b2 = NULL;
    info.numRows = 0;
    for (int i = 0; i < OIMO_MAX_MANIFOLD_POINTS; i++) {
        info.rows[i] = oimo_contact_solver_info_row_create();
    }
    return info;
}

#endif // OIMO_DYNAMICS_CONSTRAINT_INFO_CONTACT_SOLVER_INFO_H
