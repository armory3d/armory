// contact_solver_info_row.h
// 1:1 port from OimoPhysics ContactSolverInfoRow.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_INFO_CONTACT_SOLVER_INFO_ROW_H
#define OIMO_DYNAMICS_CONSTRAINT_INFO_CONTACT_SOLVER_INFO_ROW_H

#include "../jacobian_row.h"
#include "../../contact/contact_impulse.h"

typedef struct OimoContactSolverInfoRow {
    OimoJacobianRow jacobianN;  // Normal jacobian (velocity + position solver)
    OimoJacobianRow jacobianT;  // Tangent jacobian (velocity solver)
    OimoJacobianRow jacobianB;  // Binormal jacobian (velocity solver)
    OimoScalar rhs;             // Right-hand side (velocity + position solver)
    OimoScalar cfm;             // Constraint force mixing (velocity solver)
    OimoScalar friction;        // Friction coefficient (velocity solver)
    OimoContactImpulse* impulse; // Impulse pointer (velocity + position solver)
} OimoContactSolverInfoRow;

static inline OimoContactSolverInfoRow oimo_contact_solver_info_row_create(void) {
    OimoContactSolverInfoRow row;
    row.jacobianN = oimo_jacobian_row_create();
    row.jacobianT = oimo_jacobian_row_create();
    row.jacobianB = oimo_jacobian_row_create();
    row.rhs = 0.0f;
    row.cfm = 0.0f;
    row.friction = 0.0f;
    row.impulse = NULL;
    return row;
}

static inline void oimo_contact_solver_info_row_clear(OimoContactSolverInfoRow* row) {
    oimo_jacobian_row_clear(&row->jacobianN);
    oimo_jacobian_row_clear(&row->jacobianT);
    oimo_jacobian_row_clear(&row->jacobianB);
    row->rhs = 0.0f;
    row->cfm = 0.0f;
    row->friction = 0.0f;
    row->impulse = NULL;
}

#endif // OIMO_DYNAMICS_CONSTRAINT_INFO_CONTACT_SOLVER_INFO_ROW_H
