#pragma once

// contact_solver_mass_data_row.h
// 1:1 port from OimoPhysics ContactSolverMassDataRow.hx

#include "../../../common/vec3.h"

typedef struct OimoContactSolverMassDataRow {
    // Normal impulse -> linear/angular velocity change
    OimoVec3 invMLinN1;
    OimoVec3 invMLinN2;
    OimoVec3 invMAngN1;
    OimoVec3 invMAngN2;

    // Tangent impulse -> linear/angular velocity change
    OimoVec3 invMLinT1;
    OimoVec3 invMLinT2;
    OimoVec3 invMAngT1;
    OimoVec3 invMAngT2;

    // Binormal impulse -> linear/angular velocity change
    OimoVec3 invMLinB1;
    OimoVec3 invMLinB2;
    OimoVec3 invMAngB1;
    OimoVec3 invMAngB2;

    // Normal mass
    OimoScalar massN;

    // Tangent/binormal mass matrix for cone friction
    OimoScalar massTB00;
    OimoScalar massTB01;
    OimoScalar massTB10;
    OimoScalar massTB11;
} OimoContactSolverMassDataRow;

static inline OimoContactSolverMassDataRow oimo_contact_solver_mass_data_row_create(void) {
    OimoContactSolverMassDataRow row;
    row.invMLinN1 = oimo_vec3_zero();
    row.invMLinN2 = oimo_vec3_zero();
    row.invMAngN1 = oimo_vec3_zero();
    row.invMAngN2 = oimo_vec3_zero();
    row.invMLinT1 = oimo_vec3_zero();
    row.invMLinT2 = oimo_vec3_zero();
    row.invMAngT1 = oimo_vec3_zero();
    row.invMAngT2 = oimo_vec3_zero();
    row.invMLinB1 = oimo_vec3_zero();
    row.invMLinB2 = oimo_vec3_zero();
    row.invMAngB1 = oimo_vec3_zero();
    row.invMAngB2 = oimo_vec3_zero();
    row.massN = 0.0f;
    row.massTB00 = 0.0f;
    row.massTB01 = 0.0f;
    row.massTB10 = 0.0f;
    row.massTB11 = 0.0f;
    return row;
}
